"""Synchronous recall service with explicit model roles and no scheduled jobs."""

import argparse
import json
import os
from pathlib import Path

import psycopg
from ..models.http_models import EmbeddingDimensionError

from ..storage.parents import replace_parents
from .recall_config import RecallSettings
from .rerank import order_candidates, select_candidates
from .rerank_context import TailContext
from .rerank_evidence import add_rerank_evidence
from .search import ThreeRouteSearch
from .search_store import SearchStore


class RecallService:
    def __init__(self, store, settings=None):
        self.store = store
        self.settings = RecallSettings() if settings is None else settings
        self.tail_context = TailContext(store)

    @classmethod
    def from_env(cls, space_id):
        return cls(SearchStore.from_env(space_id), RecallSettings.from_env())

    def recall(self, query, *, embedder, cleaner, reranker, selector, messages=(), rerank=True,
               check_time=None, on_progress=None):
        if type(rerank) is not bool:
            raise ValueError('精排开关必须为布尔值')
        stats = {}
        result = dict(candidates=[], ordered=[], final=[], retrieval_stats=stats,
                      ordering_stats={}, selection_stats={})

        def checkpoint(rows):
            if check_time is not None:
                check_time()
            if on_progress is not None:
                on_progress(rows[:5], result)

        coarse = ThreeRouteSearch(self.store,self.settings).search(
            query, embedder=embedder, cleaner=cleaner, diagnostics=stats, check_time=check_time)
        checkpoint([row for row in coarse if row.get('archive_reason') is None])
        policy = self.store.policy()
        if check_time is not None:
            check_time()
        self.store.check_revision(stats['policy_revision'])
        candidates = replace_parents(self.store,coarse,stats,check_time=check_time)
        candidates = add_rerank_evidence(candidates,coarse,stats,self.settings)
        result['candidates'] = candidates
        checkpoint(candidates)
        stats['rerank_context'] = dict(enabled=self.settings.full_list_enabled,tail_used=False,
            reason='not_evaluated' if self.settings.full_list_enabled else 'feature_disabled')
        if not candidates:
            stats['rerank_context']['reason'] = 'no_candidates'
            stats['status'] = 'failed' if stats['errors'] else 'empty'
            self.store.check_revision(policy['revision'])
            return result
        if not rerank:
            final = candidates[:5]
            result['ordering_stats'] = result['selection_stats'] = {'skipped':True,'reason':'disabled'}
            stats['rerank_context']['reason'] = 'rerank_disabled'
        else:
            llm_query = query
            if self.settings.full_list_enabled:
                debug = stats.get('graph_seeds',{})
                keyword_ids = debug.get('keyword_entity_ids_before_filter',debug.get('keyword_entity_ids'))
                llm_query, context = self.tail_context.build(query,messages,policy,self.settings,keyword_ids)
                stats['rerank_context'] = dict(enabled=True,**context)
                if check_time is not None:
                    check_time()
            ordered, order_stats = order_candidates(query,candidates,reranker,full_list=self.settings.full_list_enabled)
            result['ordering_stats'] = order_stats
            if order_stats.get('error'):
                stats['errors']['document_rerank'] = order_stats['error']
                final_input = candidates if self.settings.full_list_enabled else candidates[:15]
            else:
                result['ordered'] = ordered
                final_input = ordered if self.settings.full_list_enabled else ordered[:10]
            checkpoint(final_input)
            final, selection_stats = select_candidates(llm_query,final_input,selector)
            result['selection_stats'] = selection_stats
            if self.settings.full_list_enabled:
                context = stats['rerank_context']
                context['tail_prepared'] = context['tail_used']
                if selection_stats.get('skipped'):
                    context['tail_used'] = False
                if selection_stats.get('error') or selection_stats.get('valid_selected',5)<min(5,len(final_input)):
                    final = final_input[:5]
                    selection_stats['error'] = selection_stats.get('error') or 'IncompleteRerankOutput'
                    selection_stats['fallback'] = 'document_top5' if result['ordered'] else 'coarse_top5'
            if selection_stats.get('error'):
                stats['errors']['llm_rerank'] = selection_stats['error']
        checkpoint(final)
        child_map = stats['gardener']['matched_children']
        reference_ids = {r['memory_id'] for r in final}
        for row in final:
            reference_ids.update(child_map.get(str(row['memory_id']),[]))
        try:
            references = self.store.source_references(sorted(reference_ids))
        except Exception as exc:
            stats['errors']['source_references'] = type(exc).__name__
            references = {}
        for row in final:
            mid = row['memory_id']
            child_ids = child_map.get(str(mid),[])
            source_status = 'unavailable' if 'source_references' in stats['errors'] else 'unmapped'
            citations = [references.get(i,{'memory_id':i,'source_status':source_status}) for i in (child_ids or [mid])]
            # A caller can inject final.content directly: neither tail nor
            # matched-child snippets are mixed into the approved full text.
            result['final'].append({key:row.get(key) for key in (
                'memory_id','title','summary','content','source_date','item_kind','source_kind','experience_mode',
                'final_score','route_hits','reasons')} | {'citations':citations,'matched_child_ids':child_ids})
        if check_time is not None:
            check_time()
        self.store.check_revision(policy['revision'])
        if stats['errors']:
            stats['status'] = 'degraded' if result['final'] else 'failed'
        return result


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--show-defaults',action='store_true')
    parser.add_argument('--space')
    parser.add_argument('--query')
    parser.add_argument('--fixed-responses',type=Path)
    parser.add_argument('--messages',type=Path,help='synthetic previous messages JSON')
    parser.add_argument('--no-rerank',action='store_true')
    args = parser.parse_args(argv)
    if args.show_defaults:
        print(json.dumps(RecallSettings.environment_defaults(),ensure_ascii=False))
        return
    if not args.space or args.query is None:
        parser.error("需要显式 --space 和 --query")
    try:
        service = RecallService.from_env(args.space)
        if args.fixed_responses is not None:
            from ..testing.fixed_models import FixedModels

            models = FixedModels.from_file(args.fixed_responses)
        else:
            from ..models.http_models import HTTPRecallModels
            from ..models.model_config import RecallModelsConfig

            models = HTTPRecallModels(
                RecallModelsConfig.from_env(),
                service.store.settings.dimensions,
                main_url=os.environ.get("MEMORY_UPSTREAM_BASE_URL"),
                main_key=os.environ.get("MEMORY_UPSTREAM_API_KEY"),
            )
            models.verify_dimensions()
        messages = json.loads(args.messages.read_text()) if args.messages else []
        if not isinstance(messages,list) or any(not isinstance(m,dict) for m in messages):
            raise ValueError('invalid messages')
        result = service.recall(args.query,embedder=models,cleaner=models,reranker=models,selector=models,
                                messages=messages,rerank=not args.no_rerank)
    except EmbeddingDimensionError as exc:
        parser.exit(2, f"召回停止：{exc}\n")
    except psycopg.Error as exc:
        parser.exit(2,f'召回停止：数据库校验失败（SQLSTATE {exc.sqlstate or "unknown"}）\n')
    except (ValueError,TypeError,OSError) as exc:
        parser.exit(2,f'召回停止：输入、配置或固定响应无效（{type(exc).__name__}）\n')
    print(json.dumps(result,ensure_ascii=False))


if __name__=='__main__':
    main()
