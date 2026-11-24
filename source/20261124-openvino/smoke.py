from pathlib import Path
import json,platform,hashlib
import numpy as np
import onnx
from onnx import helper,TensorProto,numpy_helper
import openvino as ov
root=Path(__file__).parent;out=root/'research';checks=[]
w=np.array([[1.,-1.,0.5],[2.,0.,-0.5],[0.,1.,1.],[-1.,2.,0.]],dtype=np.float32);b=np.array([0.25,-0.25,0.5],dtype=np.float32)
g=helper.make_graph([helper.make_node('MatMul',['x','w'],['m']),helper.make_node('Add',['m','b'],['a']),helper.make_node('Relu',['a'],['y'])],'synthetic-linear-relu',[helper.make_tensor_value_info('x',TensorProto.FLOAT,['batch',4])],[helper.make_tensor_value_info('y',TensorProto.FLOAT,['batch',3])],[numpy_helper.from_array(w,'w'),numpy_helper.from_array(b,'b')]);proto=helper.make_model(g,opset_imports=[helper.make_opsetid('',13)],ir_version=9);onnx.checker.check_model(proto);onnx.save(proto,out/'synthetic.onnx')
core=ov.Core();devices=list(core.available_devices);assert 'CPU'in devices;checks.append('CPU device discovered')
model=ov.convert_model(out/'synthetic.onnx');assert model.input(0).partial_shape[0].is_dynamic;checks.append('ONNX conversion retains dynamic batch')
compiled=core.compile_model(model,'CPU',{'INFERENCE_PRECISION_HINT':'f32'});batches=[np.array([[1,2,3,4]],dtype=np.float32),np.arange(12,dtype=np.float32).reshape(3,4)/4];errors=[]
for x in batches:
 expected=np.maximum(x@w+b,0);actual=compiled([x])[0];np.testing.assert_allclose(actual,expected,rtol=1e-5,atol=1e-5);errors.append(float(np.max(np.abs(actual-expected))))
checks.append('CPU outputs match NumPy for batch1 and3')
ov.save_model(model,out/'synthetic.xml',compress_to_fp16=False);reloaded=core.compile_model(core.read_model(out/'synthetic.xml'),'CPU',{'INFERENCE_PRECISION_HINT':'f32'});np.testing.assert_allclose(reloaded([batches[1]])[0],np.maximum(batches[1]@w+b,0),rtol=1e-5,atol=1e-5);checks.append('FP32 IR save/reload matches reference')
requests=[compiled.create_infer_request()for _ in batches]
for r,x in zip(requests,batches):r.start_async({0:x})
for r,x in zip(requests,batches):r.wait();np.testing.assert_allclose(r.get_output_tensor(0).data,np.maximum(x@w+b,0),rtol=1e-5,atol=1e-5)
checks.append('two async requests match their independent inputs')
auto=core.compile_model(model,'AUTO:CPU',{'INFERENCE_PRECISION_HINT':'f32'});np.testing.assert_allclose(auto([batches[0]])[0],np.maximum(batches[0]@w+b,0),rtol=1e-5,atol=1e-5);execution=list(auto.get_property('EXECUTION_DEVICES'));assert all('CPU'in x for x in execution);checks.append('AUTO:CPU executes on reported CPU')
try: compiled([np.zeros((1,5),dtype=np.float32)])
except Exception as e: shapeError=str(e).splitlines()[0];checks.append('wrong feature dimension rejected')
else:raise AssertionError('invalid input accepted')
r={'version':ov.__version__,'build':ov.get_version(),'python':platform.python_version(),'platform':platform.platform(),'machine':platform.machine(),'devices':devices,'autoExecutionDevices':execution,'passed':len(checks),'checks':checks,'maxAbsErrors':errors,'shapeError':shapeError,'notTested':['real pretrained model quality','IntelGPU/NPU','quantization','multi-device scheduling','remote/cloud modelserver','performance/speedup/peakmemory'],'artifacts':{f.name:hashlib.sha256(f.read_bytes()).hexdigest()for f in out.glob('synthetic.*')}};(out/'smoke-results.json').write_text(json.dumps(r,indent=2));print(json.dumps(r,indent=2))
