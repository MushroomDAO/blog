const $=id=>document.getElementById(id);
let socket=null,ctx=null,stream=null,capture=null,source=null,micOn=false,timer=null,connecting=null;
let nextPlay=0,players=[],pending=0,utterance=null,delegations=0,finished=false,mathRunning=false,audioQueue=[];
let outputEpoch=0,lastPlaybackReport=0,lastPlaybackPlaying=false,lastPlaybackEpoch=-1,inputSequence=0,duplexProtocol=false;
const traces=new Map();
function activity(text,error=false){$('activity').textContent=text;$('activity').classList.toggle('error',error);}
function bubble(text,kind='assistant'){
  $('welcome')?.remove();const el=document.createElement('div');el.className=`bubble ${kind}`;
  if(kind==='assistant'){const label=document.createElement('label');label.textContent='sage-interaction';el.append(label);}
  const body=document.createElement('span');body.textContent=text;el.append(body);$('messages').append(el);
  $('messages').scrollTop=$('messages').scrollHeight;return body;
}
function playbackState(){
  const queued=ctx?Math.max(0,nextPlay-ctx.currentTime):0;
  return {playing:players.length>0&&queued>0,queued_seconds:Math.round(queued*1000)/1000,epoch:outputEpoch};
}
function reportPlayback(force=false){
  const state=playbackState(),now=Date.now();
  const changed=state.playing!==lastPlaybackPlaying||state.epoch!==lastPlaybackEpoch;
  if(duplexProtocol&&socket?.readyState===WebSocket.OPEN&&(force||changed||(state.playing&&now-lastPlaybackReport>=250))){
    socket.send(JSON.stringify({type:'playback_state',playback:state}));
    lastPlaybackReport=now;lastPlaybackPlaying=state.playing;lastPlaybackEpoch=state.epoch;
  }else{}
}
function stopPlayback(){
  const stopped=players;players=[];nextPlay=0;
  for(const player of stopped){player.onended=null;player.stop();}
  reportPlayback(true);
}
function pcm64(samples){let text='';const bytes=new Uint8Array(samples.buffer,samples.byteOffset,samples.byteLength);for(let n=0;n<bytes.length;n+=8192)text+=String.fromCharCode(...bytes.subarray(n,n+8192));return btoa(text);}
function send(message){
  if(socket?.readyState===WebSocket.OPEN){
    const payload=message.type==='audio'?{...message,playback:playbackState()}:message;
    socket.send(JSON.stringify(payload));pending++;return true;
  }else{return false;}
}
function play(message){
  const epoch=message.output_epoch??outputEpoch;
  if(epoch<outputEpoch){return;}else if(epoch>outputEpoch){outputEpoch=epoch;stopPlayback();}else{}
  const bytes=Uint8Array.from(atob(message.data),c=>c.charCodeAt(0));const samples=new Float32Array(bytes.buffer);
  const buffer=ctx.createBuffer(1,samples.length,message.sample_rate);buffer.copyToChannel(samples,0);
  const player=ctx.createBufferSource();player.buffer=buffer;player.connect(ctx.destination);
  nextPlay=Math.max(nextPlay,ctx.currentTime+.08);player.start(nextPlay);nextPlay+=buffer.duration;players.push(player);
  player.onended=()=>{
    players=players.filter(row=>row!==player);nextPlay=players.length?nextPlay:0;
    reportPlayback(true);
  };
  reportPlayback(true);
}
async function audioContext(){if(!ctx)ctx=new AudioContext();await ctx.resume();}
function startSilence(){clearInterval(timer);let lastSilence=Date.now();timer=setInterval(()=>{
  reportPlayback();
  if(audioQueue.length&&pending<2){
    const chunk=audioQueue.shift();
    send({type:'audio',data:pcm64(chunk.samples),input_sequence:chunk.sequence,
      input_queue_seconds:Math.max(0,(Date.now()-chunk.capturedAt)/1000)});
  }
  else if(!micOn&&!mathRunning&&!audioQueue.length&&pending<2&&Date.now()-lastSilence>=1000&&socket?.readyState===WebSocket.OPEN){send({type:'drain'});lastSilence=Date.now();}
  else{}
},100);}
async function connect(){
  if(socket?.readyState===WebSocket.OPEN)return;
  if(connecting)return connecting;
  connecting=(async()=>{
  await audioContext();finished=false;audioQueue=[];activity('正在建立语音会话…');
  await new Promise((resolve,reject)=>{
    const endpoint=new URL('ws',location.href);endpoint.protocol=location.protocol==='https:'?'wss:':'ws:';
    const connection=new WebSocket(endpoint);socket=connection;
    const wait=setTimeout(()=>{connection.close();reject(new Error('会话启动超时，请重试'));},90000);
    connection.onmessage=event=>{
      if(socket!==connection)return;
      const message=JSON.parse(event.data);
      if(message.type==='ready'){
        clearTimeout(wait);$('sessionLabel').textContent=`${Number.isInteger(message.output_epoch)?'全双工 · ':''}会话 ${message.session_id.slice(0,6)}`;
        duplexProtocol=Number.isInteger(message.output_epoch);
        outputEpoch=message.output_epoch??0;inputSequence=0;lastPlaybackEpoch=-1;
        $('stop').disabled=false;pending=0;startSilence();reportPlayback(true);activity('已连接，随时开口');resolve();
      }else if(message.type==='action'){
        if(message.action==='speak'&&message.text){if(!utterance)utterance=bubble('');utterance.textContent+=message.text;$('messages').scrollTop=$('messages').scrollHeight;activity(micOn?'sage-interaction 正在说话，仍在听你':'sage-interaction 正在说话');}
        if(message.end_of_turn)utterance=null;
        if(message.action==='listen')activity(micOn?'正在倾听…':'等待下一句话');
      }else if(message.type==='audio'){play(message);
      }else if(message.type==='interrupt'){
        const epoch=message.output_epoch??outputEpoch+1;
        if(epoch>=outputEpoch){outputEpoch=epoch;stopPlayback();utterance=null;activity(micOn?'已停下回复，正在听你说…':'已停止上一段回复');}else{}
      }else if(message.type==='delegate_request'){
        if(delegations===0)$('trace').textContent='';delegations++;$('delegateCount').textContent=delegations;
        const item=document.createElement('div');item.className='trace-item';const title=document.createElement('strong');title.textContent='DEEPSEEK · 处理中';item.append(title);$('trace').prepend(item);traces.set(message.task_id,{item,title});activity('已委托 DeepSeek，仍可继续交流');
      }else if(message.type==='delegate_result'){
        const row=traces.get(message.payload.task_id);
        if(row){row.title.textContent=message.payload.status==='ok'?'DEEPSEEK · 已返回':'DEEPSEEK · 请求失败';const result=document.createElement('p');result.textContent=message.payload.content;const time=document.createElement('small');time.textContent=`${message.backend_seconds?.toFixed(2)||'—'} 秒`;row.item.append(result,time);}
        activity('结果已交回 sage-interaction');
      }else if(message.type==='consumed'){pending=Math.max(0,pending-1);
      }else if(message.type==='error'){clearTimeout(wait);activity(message.message,true);reject(new Error(message.message));}
    };
    connection.onerror=()=>{clearTimeout(wait);reject(new Error('连接失败，请检查服务状态'));};
    connection.onclose=()=>{clearTimeout(wait);if(socket===connection){socket=null;pending=0;audioQueue=[];clearInterval(timer);disableMic();stopPlayback();$('stop').disabled=true;if(!finished)activity('会话已断开，可重新开始',true);}reject(new Error('连接已关闭'));};
  });
  })();
  try{return await connecting;}finally{connecting=null;}
}
function disableMic(){micOn=false;capture?.disconnect();source?.disconnect();stream?.getTracks().forEach(track=>track.stop());capture=null;source=null;stream=null;$('micLabel').textContent='开始语音对话';$('mic').classList.remove('active');document.body.classList.remove('listening');}
$('mic').onclick=async()=>{
  if(micOn){disableMic();activity('麦克风已暂停，会话继续');return;}
  try{
    if(!window.isSecureContext||!navigator.mediaDevices)throw new Error('麦克风需要 HTTPS；请使用当前站点的 HTTPS 地址并信任内网证书。');
    await connect();stream=await navigator.mediaDevices.getUserMedia({audio:{echoCancellation:true,noiseSuppression:true,autoGainControl:true},video:false});
    await ctx.audioWorklet.addModule(new URL('static/capture.js',location.href));source=ctx.createMediaStreamSource(stream);capture=new AudioWorkletNode(ctx,'voice-capture');
    capture.port.onmessage=event=>{
      audioQueue.push({samples:event.data,capturedAt:Date.now(),sequence:++inputSequence});
      if(audioQueue.length>12){disableMic();activity('语音处理暂时落后，麦克风已暂停；已录入的语音会继续处理。',true);}else{}
    };
    const mute=ctx.createGain();mute.gain.value=0;source.connect(capture);capture.connect(mute);mute.connect(ctx.destination);
    micOn=true;$('micLabel').textContent='持续倾听 · 暂停麦克风';$('mic').classList.add('active');document.body.classList.add('listening');activity('正在倾听，你可以随时插话');
  }catch(error){disableMic();activity(error.message,true);}
};
$('stop').onclick=()=>{finished=true;mathRunning=false;audioQueue=[];disableMic();stopPlayback();clearInterval(timer);if(socket?.readyState===WebSocket.OPEN)socket.send(JSON.stringify({type:'stop'}));socket?.close();socket=null;$('stop').disabled=true;activity('会话已结束，音频与委托记录已保存到本机');};
$('textForm').onsubmit=async event=>{event.preventDefault();const text=$('textInput').value.trim();if(!text)return;try{await connect();stopPlayback();utterance=null;bubble(text,'user');send({type:'text',text});$('textInput').value='';}catch(error){activity(error.message,true);}};
$('math').onclick=async()=>{
  if(mathRunning)return;
  mathRunning=true;$('math').disabled=true;
  try{
    await connect();
    const text='Can you evaluate the integral of (exp(p*x) - exp(q*x)) / (1 - exp(x)) from minus infinity to infinity, where 0 < p, q < 1?';
    bubble(text,'user');send({type:'text',text});
  }catch(error){activity(error.message,true);}
  finally{mathRunning=false;$('math').disabled=false;}
};
async function health(){
  try{const result=await(await fetch('api/health')).json();const front=result.workers.some(row=>row.ready);$('backendName').textContent=result.backend.model;$('frontLed').classList.toggle('ready',front);$('backLed').classList.toggle('ready',result.backend.ready);$('statusDot').classList.toggle('online',result.ready);$('status').textContent=result.ready?'服务在线':'服务准备中';$('capacity').textContent=`${result.workers.filter(row=>row.ready).length} / ${result.workers.length} 语音单元就绪 · ${result.available_sessions} 个空闲会话`;$('mic').disabled=!result.ready||mathRunning;$('send').disabled=!result.ready;if(!mathRunning)$('math').disabled=!result.ready;
    if(!socket&&result.workers.some(row=>row.ready&&row.system_barge_in&&row.duplex_protocol==='native_duplex_v1')){$('sessionLabel').textContent='全双工语音';}else{}
  }
  catch{$('status').textContent='服务暂不可达';$('mic').disabled=true;$('send').disabled=true;$('math').disabled=true;}
}
health();setInterval(health,10000);window.addEventListener('beforeunload',()=>{disableMic();socket?.close();});
