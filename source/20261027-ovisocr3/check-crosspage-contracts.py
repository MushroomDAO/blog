"""Exercise released postprocessing on synthetic strings, without a model or renderer.
Usage: python check-crosspage-contracts.py /path/to/document_crosspage.py
"""
from pathlib import Path
import importlib.util,sys,json
path=Path(sys.argv[1]);spec=importlib.util.spec_from_file_location('ovis_crosspage_audit',path);m=importlib.util.module_from_spec(spec);sys.modules[spec.name]=m;spec.loader.exec_module(m)
report=[]
left='Page A\n<table><tr><td>A</td></tr></table>\nFoot A'
right='Page B\n<table><tr><td>B</td></tr></table>\nFoot B'
negative=json.dumps([{'source_pages':[],'html':m.NEGATIVE}]);assert m.parse_tables(negative)==[];assert m.apply_pair((left,right),[])==(left,right);report.append('No-continuation leaves both pages unchanged')
html='<table><tr><td>A</td></tr><tr><td>B</td></tr></table>';tables=m.parse_tables(json.dumps([{'source_pages':[1,2],'html':html}]))
a,b=m.apply_pair((left,right),tables);assert a=='Page A\n'+html+'\nFoot A' and b=='Page B\n\nFoot B';report.append('Positive merge replaces only the bound table fragments and preserves other text')
try:m.parse_tables(json.dumps([{'source_pages':[2,3],'html':html}]))
except ValueError:report.append('Document-global pages [2,3] rejected where pair-local [1,2] is required')
else:raise AssertionError('Invalid source pages accepted')
try:m.apply_pair((left,right),tables+tables)
except ValueError:report.append('Multiple merged tables rejected without explicit fragment bindings')
else:raise AssertionError('Ambiguous bindings accepted')
source=m.page_markdown('<img src="images/bbox_1_2_3_4.jpg" />',2);assert 'page_2/images/'in source and 'page_9/images/'in m.remap(source,{2:9});report.append('Crop references qualified to their source page and explicitly remapped')
print(json.dumps({'passed':len(report),'checks':report,'scope':'Synthetic postprocessing contracts only; no visual table recognition, model inference, browser rendering or benchmark reproduction.'},indent=2))
