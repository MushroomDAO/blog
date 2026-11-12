"""Read one pinned SimReady package with OpenUSD; does not run a physics engine."""
from pathlib import Path
import sys,json,hashlib,collections
from pxr import Usd, UsdGeom, UsdPhysics, UsdUtils

package=Path(sys.argv[1]).resolve()
bom=json.loads((package/'.metadata/com.nvidia.simready.packaging.bom.json').read_text())
checks=[]
for item in bom['items']:
    path=package/item['relative_path']
    checks.append({'path':item['relative_path'],'exists':path.exists(),'sizeMatches':path.exists() and path.stat().st_size==item['size'],'sha256Matches':path.exists() and hashlib.sha256(path.read_bytes()).hexdigest()==item['hash']['sha256']})
assert all(x['exists'] and x['sizeMatches'] and x['sha256Matches'] for x in checks)
root_path=package/'simready_usd/sm_box_corrugated_brown_b08_01.usd'
stage=Usd.Stage.Open(str(root_path));assert stage
root=stage.GetDefaultPrim();variant_sets={n:{'choices':root.GetVariantSet(n).GetVariantNames(),'selected':root.GetVariantSet(n).GetVariantSelection()} for n in root.GetVariantSets().GetNames()}
prims=list(Usd.PrimRange(stage.GetPseudoRoot(), Usd.TraverseInstanceProxies()))
def fields():
    out=[]
    for p in Usd.PrimRange(stage.GetPseudoRoot(),Usd.TraverseInstanceProxies()):
        values={}
        for a in p.GetAttributes():
            if (a.GetName().startswith('physics:') or a.GetName().startswith('semantics:labels:')) and a.HasAuthoredValueOpinion():
                values[a.GetName()]=str(a.Get())
        if values:out.append({'prim':str(p.GetPath()),'values':values})
    return out
initial=fields()
per_variant={}
with Usd.EditContext(stage,stage.GetSessionLayer()):
    for variant_name in ['PhysX','MuJoCo','Newton']:
        root.GetVariantSet(variant_name).SetVariantSelection('Disabled')
for name in ['PhysX','MuJoCo','Newton']:
    vs=root.GetVariantSet(name)
    if 'Enabled' not in vs.GetVariantNames():continue
    with Usd.EditContext(stage,stage.GetSessionLayer()):
        vs.SetVariantSelection('Enabled')
    stage.Load();per_variant[name]=fields()
    with Usd.EditContext(stage,stage.GetSessionLayer()):
        vs.SetVariantSelection('Disabled')
with Usd.EditContext(stage,stage.GetSessionLayer()):
    for variant_name in ['PhysX','MuJoCo','Newton']:
        root.GetVariantSet(variant_name).SetVariantSelection(variant_sets[variant_name]['selected'])
# Dependency discovery is a file-availability check, not shader rendering or physics validation.
layers,assets,unresolved=UsdUtils.ComputeAllDependencies(str(root_path))
meta=stage.GetRootLayer().customLayerData
embedded=meta.get('SimReady_Metadata',{}).get('validation',{})
report={'usdVersion':Usd.GetVersion(),'root':str(root_path),'defaultPrim':str(root.GetPath()),'metersPerUnit':UsdGeom.GetStageMetersPerUnit(stage),'upAxis':UsdGeom.GetStageUpAxis(stage),'kilogramsPerUnit':UsdPhysics.GetStageKilogramsPerUnit(stage),'defaultPrimCount':len(prims),'variantSets':variant_sets,'defaultAuthoredFields':initial,'enabledVariantFields':per_variant,'bomChecks':checks,'bomAllPass':True,'dependencyLayers':len(layers),'dependencyAssets':len(assets),'unresolvedDependencies':unresolved,'embeddedHistoricalValidation':embedded,'scope':'One complete package read/compose/BOM audit on Mac. No physics engine, rendering, robot training, sim-to-real, or full-library validation.'}
output=Path(sys.argv[2]);output.write_text(json.dumps(report,ensure_ascii=False,indent=2,default=str)+'\n')
print(json.dumps({'usdVersion':Usd.GetVersion(),'bomItems':len(checks),'bomAllPass':True,'metersPerUnit':report['metersPerUnit'],'kilogramsPerUnit':report['kilogramsPerUnit'],'variantSets':variant_sets,'fieldPrims':{k:len(v) for k,v in per_variant.items()},'dependencyLayers':len(layers),'dependencyAssets':len(assets),'unresolvedDependencies':unresolved},ensure_ascii=False))
