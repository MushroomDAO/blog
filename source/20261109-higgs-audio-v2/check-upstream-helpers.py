"""Run real upstream pure helpers without loading heavy model dependencies."""
import ast,typing,pathlib,json
p=pathlib.Path('/tmp/higgs-audio-research/examples/generation.py')
tree=ast.parse(p.read_text());names={'prepare_chunk_text','normalize_chinese_punctuation'}
selected=[n for n in tree.body if isinstance(n,ast.FunctionDef)and n.name in names]
ns={'Optional':typing.Optional};exec(compile(ast.Module(body=selected,type_ignores=[]),str(p),'exec'),ns)
f=ns['prepare_chunk_text'];checks={}
checks['unchanged_input']=f('hello\nworld')==['hello\nworld']
text='[SPEAKER0] Hello\ncontinued\n[SPEAKER1] Hi\n[SPEAKER0] Bye'
checks['speaker_continuation']=f(text,'speaker')==['[SPEAKER0] Hello\ncontinued','[SPEAKER1] Hi','[SPEAKER0] Bye']
checks['group_two_turns']=f(text,'speaker',chunk_max_num_turns=2)==['[SPEAKER0] Hello\ncontinued\n[SPEAKER1] Hi','[SPEAKER0] Bye']
checks['special_tags']=len(f('<|speaker_id_start|>SPEAKER0<|speaker_id_end|> Hello\n<|speaker_id_start|>SPEAKER1<|speaker_id_end|> Hi','speaker'))==2
try:f('hi','invalid');checks['invalid_method']=False
except ValueError:checks['invalid_method']=True
checks['chinese_punctuation']=ns['normalize_chinese_punctuation']('你好，世界。')=='你好, 世界.'
report={'codeCommit':'05a145bb490501b534563bf51bf2f7aa2326b271','checks':checks,'passed':sum(checks.values()),'scope':'actual AST-extracted upstream pure functions; no model inference, audio, GPU, word-mode dependencies or API execution'}
print(json.dumps(report,ensure_ascii=False,indent=2));pathlib.Path(__file__).with_name('helper-check-results.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n');assert all(checks.values())
