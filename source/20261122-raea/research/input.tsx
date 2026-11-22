import { AbsoluteFill,Composition,registerRoot,useGameState } from 'raea';
function step(x:number,input:{keys:string[]}):number{return x+(input.keys.includes('ArrowRight')?5:0);}
function Scene(){const x=useGameState(100,step);return <AbsoluteFill style={{background:'#eeeeee'}}><div style={{position:'absolute',left:x,top:300,width:80,height:80,background:'#ff8844'}}/></AbsoluteFill>;}
registerRoot(()=><Composition id="input" component={Scene} width={640} height={480} fps={30} durationInFrames={90}/>);
