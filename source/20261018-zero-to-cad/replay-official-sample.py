from pathlib import Path
import base64,json,hashlib,runpy,math,platform
import cadquery as cq
b=Path(__file__).resolve().parent;r=json.loads((b/'test-row.json').read_text())['rows'][0]['row'];p=b/'official-test-sample.py';source=base64.b64decode(r['cadquery_file']);assert p.read_bytes()==source
# The saved source was manually reviewed: only CadQuery geometry construction.
model=runpy.run_path(str(p))['result'];shape=model.val();assert shape.isValid();assert len(model.solids().vals())==1;assert shape.Volume()>0
step=b/'replayed.step';stl=b/'replayed.stl';cq.exporters.export(model,str(step));cq.exporters.export(model,str(stl));again=cq.importers.importStep(str(step)).val();assert again.isValid();assert math.isclose(shape.Volume(),again.Volume(),rel_tol=1e-7)
reference=b/'reference.step';reference.write_bytes(base64.b64decode(r['step_file']));ref=cq.importers.importStep(str(reference)).val();box=shape.BoundingBox();rb=ref.BoundingBox()
report={'dataset':'ADSKAILab/Zero-To-CAD-1m','split':'test','rowOffset':0,'uuid':r['uuid'],'datasetMetadataRevision':json.loads((b/'dataset-metadata.json').read_text())['sha'],'sourceSha256':hashlib.sha256(source).hexdigest(),'environment':{'python':platform.python_version(),'platform':platform.platform(),'cadquery':cq.__version__},'valid':shape.isValid(),'solidCount':len(model.solids().vals()),'faceCount':len(shape.Faces()),'sourceReportedFaceCount':r['num_faces'],'volume':shape.Volume(),'referenceVolume':ref.Volume(),'volumeMatchesReference':math.isclose(shape.Volume(),ref.Volume(),rel_tol=1e-7),'bboxLengths':[box.xlen,box.ylen,box.zlen],'referenceBboxLengths':[rb.xlen,rb.ylen,rb.zlen],'stepRoundTripValid':again.isValid(),'stepBytes':step.stat().st_size,'stlBytes':stl.stat().st_size,'modelInference':False,'newPrediction':False,'benchmarkReproduction':False}
(b/'sample-replay.json').write_text(json.dumps(report,indent=2));print(json.dumps(report,indent=2))
