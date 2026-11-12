self.DrawingModels ??= {};
self.DrawingModels['layer-stack'] = (parameters, options) => {
 const G=TechnicalGeometry,w=parameters.width;
 if(!Number.isFinite(w)||w<70||w>110)throw Error('Illustrative width must be 70–110');
 const rows=[['source','Source layer',0,0],['filter','Filter layer',2.3,1],['cover','Cover layer',4.6,2]];
 const parts=rows.map(([id,name,z,index])=>{
  const p=G.part(id,name,[-65*index,0,65*index]);
  G.box(p,[-w/2,-30,z],[w/2,30,z+2],{radius:2});return p;
 });
 return TechnicalProjection.render(parts,{...options,camera:{azimuth:-115,elevation:28,roll:0}});
};
