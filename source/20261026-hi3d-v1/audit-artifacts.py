"""Read pinned public configs and safetensors headers only; no model execution."""
import json, math, struct, urllib.request
from pathlib import Path
REVISION = 'd502e938cbedc6e87aba8884614c5ca6d177a4b6'
BASE = f'https://huggingface.co/hi3d-official/Hi3Dv1.0/resolve/{REVISION}/'
def read_header(component):
 url = BASE + component + '/model.safetensors'
 request = urllib.request.Request(url, headers={'Range':'bytes=0-7'})
 with urllib.request.urlopen(request, timeout=60) as response:
  assert response.status == 206
  length = struct.unpack('<Q', response.read(8))[0]
  content_range = response.headers['Content-Range']
 assert length < 10_000_000
 request = urllib.request.Request(url, headers={'Range':f'bytes=8-{7+length}'})
 with urllib.request.urlopen(request, timeout=60) as response:
  assert response.status == 206
  header = json.loads(response.read(length))
 dtypes = {}
 for name, value in header.items():
  if name == '__metadata__': continue
  count = math.prod(value['shape'])
  dtypes[value['dtype']] = dtypes.get(value['dtype'], 0) + count
 return {'component':component,'range':content_range,'headerBytes':length,'elements':sum(dtypes.values()),'dtypes':dtypes}
if __name__ == '__main__':
 result = {'revision':REVISION,'components':[read_header(x) for x in ['vae','transformer_512','transformer_1024']], 'method':'HTTP Range headers only; no weights or inference'}
 print(json.dumps(result, indent=2))
