"""Demonstrate commit-range and default-diff limits in an isolated scratch repository."""
from pathlib import Path
import tempfile,subprocess,json

def git(p,*args):return subprocess.check_output(['git','-C',str(p),*args],text=True,stderr=subprocess.DEVNULL)
with tempfile.TemporaryDirectory(prefix='improve-drift-audit-')as d:
 p=Path(d);git(p,'init');git(p,'config','user.name','Local Audit');git(p,'config','user.email','audit@example.invalid');(p/'scope.txt').write_text('baseline\n');git(p,'add','.');git(p,'commit','-m','baseline');base=git(p,'rev-parse','HEAD').strip();(p/'scope.txt').write_text('uncommitted change\n');range_diff=git(p,'diff','--stat',base+'..HEAD','--','scope.txt');working_diff=git(p,'diff','--stat','HEAD','--','scope.txt');assert not range_diff.strip() and working_diff.strip()
 git(p,'restore','scope.txt');(p/'outside.txt').write_text('out of scope\n');git(p,'add','outside.txt');git(p,'commit','-m','executor committed out-of-scope edit');default_diff=git(p,'diff','--stat');committed_diff=git(p,'diff','--stat',base+'..HEAD');assert not default_diff.strip() and 'outside.txt'in committed_diff
 out={'checksPassed':2,'scope':'Only mechanical Git command behavior in a temporary repository, no LLM audit or executor run','case1':{'commitRangeMissesUncommittedChange':True,'workingTreeDiffSeesChange':True},'case2':{'defaultDiffMissesCommittedOutOfScopeFile':True,'baselineToHeadDiffSeesFile':True},'interpretation':'Template commands must be combined with clean-working-tree checks and explicit base comparisons; this is not a claim that every host reviewer misses these cases.'}
Path(__file__).with_name('git-check-results.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out))
