from pathlib import Path
import subprocess,random,json,audioop,sys,hashlib
root=Path(sys.argv[1]) if len(sys.argv)>1 else Path('/tmp/espica32-research/code/kiwi-radio-mini');work=Path('/tmp/espica32-research/host-test');work.mkdir(exist_ok=True)
b=random.Random(20261108).randbytes(4096);(work/'input.bin').write_bytes(b)
subprocess.run(['clang++','-std=c++17','-Wall','-Wextra','-Werror','-I',str(root),str(Path(__file__).with_name('host-smoke.cpp')),'-o',str(work/'test')],check=True)
r=json.loads(subprocess.check_output([str(work/'test'),str(work/'input.bin'),str(work/'pcm.bin')],text=True))
# audioop expects high nibble first; upstream Kiwi decoder consumes low nibble first.
reference,state=audioop.adpcm2lin(bytes(((v&15)<<4)|(v>>4)for v in b),2,(0,0));assert reference==(work/'pcm.bin').read_bytes()
r.update(python=sys.version,reference='CPython audioop.adpcm2lin, nibble-swapped input, initial state (0,0)',referenceMatches=True,compiler=subprocess.check_output(['clang++','--version'],text=True).splitlines()[0],inputSha256=hashlib.sha256(b).hexdigest(),scope='Actual outer-directory ADPCM and buffer headers compiled on macOS host; no Arduino firmware build, ESP32 hardware, network receiver or listening test.')
Path(__file__).with_name('host-test-result.json').write_text(json.dumps(r,indent=2));print(json.dumps(r,indent=2))
