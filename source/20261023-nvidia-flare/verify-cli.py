"""Exercise upstream argument parsing without loading weights or CUDA."""
import sys,json
from pathlib import Path
sys.path.insert(0,'/tmp/mycelium-flare-20261023')
from ignition.cli import _parser
parser=_parser()
single=parser.parse_args(['export','deepseek-v4.1-flash','--gpus','0,1,2,3','--max-concurrency','4','--mtp-draft-tokens','5','--output','dsv41.safetensors'])
assert single.gpus=='0,1,2,3'
assert single.max_concurrency==4 and single.mtp_draft_tokens==5
multi=parser.parse_args(['export','deepseek-v4.1-flash','--gpus','0','--ranks','4','--rendezvous','10.200.0.12:29630','--output','multi.safetensors'])
assert multi.ranks==4 and multi.rendezvous=='10.200.0.12:29630'
print(json.dumps({'singleHostTP4Parsed':True,'multiHostRanksParsed':True,'scope':'argument parser only; no CUDA build, inference or benchmark'}))
