import { AbsoluteFill, Composition, interpolate, registerRoot, useCurrentFrame } from "raea";
function Hello() {
  const f = useCurrentFrame();
  return <AbsoluteFill style={{background:'#112238',color:'#ffffff',fontSize:120,justifyContent:'center',alignItems:'center'}}>
    <div style={{opacity:interpolate(f,[0,20],[0,1],{extrapolateRight:'clamp'})}}>Hello raea</div>
    <div style={{position:'absolute',left:100+f*8,top:750,width:100,height:100,background:'#ff8844',borderRadius:50}} />
  </AbsoluteFill>;
}
registerRoot(()=><Composition id="hello" component={Hello} width={1920} height={1080} fps={30} durationInFrames={90}/>);
