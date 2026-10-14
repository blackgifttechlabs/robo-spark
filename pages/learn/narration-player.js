import { readRecording } from './audio-store.js';
const published=fetch('assets/audio/narration/index.json').then(r=>r.ok?r.json():{}).catch(()=>({}));
export async function createNarrationPlayer(clip,callbacks,startFraction=0){
 let alive=true,paused=true,finished=false,frame,url,audio,utterance,elapsed=0,anchor=0,progress=startFraction,captionPreview=false,captionElapsed=0;
 const duration=Math.max(3,clip.spoken.split(/\s+/).length/2.15),speechAvailable='speechSynthesis' in window;
 const report=f=>{progress=Math.max(0,Math.min(1,f));callbacks.progress?.(progress)};
 const done=()=>{if(!alive||finished)return;finished=true;paused=true;cancelAnimationFrame(frame);report(1);callbacks.done?.()};
 let recording;try{recording=await readRecording(clip.id)}catch{}
 const manifest=await published;
 if(recording){url=URL.createObjectURL(recording);audio=new Audio(url)}else if(manifest[clip.id]){audio=new Audio(manifest[clip.id])}
 if(audio){
  audio.preload='auto';audio.onended=done;audio.onloadedmetadata=()=>{if(Number.isFinite(audio.duration))audio.currentTime=startFraction*audio.duration};
  audio.onerror=()=>{if(alive){callbacks.status?.('Recording unavailable · captions preview');audio=null;startCaptions()}};
 }
 function draw(now){if(!alive||paused)return;if(audio){if(Number.isFinite(audio.duration)&&audio.duration>0)report(audio.currentTime/audio.duration)}else{elapsed=(now-anchor)/1000;report(startFraction+(1-startFraction)*Math.min(.97,elapsed/(duration*(1-startFraction))))}frame=requestAnimationFrame(draw)}
 function startCaptions(){audio=null;paused=false;captionPreview=true;anchor=performance.now()-captionElapsed*1000;callbacks.status?.('Captions preview · no voice available');function tick(now){if(!alive||paused)return;captionElapsed=(now-anchor)/1000;report(startFraction+captionElapsed/duration);if(progress>=1)done();else frame=requestAnimationFrame(tick)}frame=requestAnimationFrame(tick)}
 function speech(){
  const voices=window.speechSynthesis.getVoices();
  if(!voices.length){startCaptions();return}
  const words=clip.spoken.split(/\s+/),skip=Math.floor(startFraction*words.length),text=words.slice(skip).join(' ');
  utterance=new SpeechSynthesisUtterance(text);utterance.rate=.88;utterance.pitch=1.1;utterance.lang='en-GB';utterance.voice=voices.find(v=>v.lang==='en-GB')||voices.find(v=>v.lang.startsWith('en'))||voices[0];
  utterance.onboundary=e=>{if(!alive||paused||!e.charIndex)return;const fraction=startFraction+(1-startFraction)*e.charIndex/Math.max(1,text.length);report(fraction);anchor=performance.now()-(fraction-startFraction)*duration*1000};
  utterance.onend=done;utterance.onerror=e=>{if(alive&&e.error!=='canceled'&&e.error!=='interrupted')startCaptions()};
  callbacks.status?.('Device voice preview · AI recordings can be added in the narration studio');window.speechSynthesis.speak(utterance);
 }
 async function play(){if(!alive||finished)return;paused=false;
  if(captionPreview&&!audio){startCaptions();return}
  if(audio){callbacks.status?.('Recorded voice · animation follows the audio');try{await audio.play()}catch{paused=true;callbacks.blocked?.();return}}
  else if(utterance){window.speechSynthesis.resume();anchor=performance.now()-elapsed*1000}
  else if(speechAvailable){speech();if(!utterance)return}
  else{startCaptions();return}
  anchor=performance.now()-elapsed*1000;cancelAnimationFrame(frame);frame=requestAnimationFrame(draw)
 }
 function pause(){paused=true;cancelAnimationFrame(frame);if(audio)audio.pause();else if(utterance)window.speechSynthesis.pause()}
 function dispose(){alive=false;paused=true;cancelAnimationFrame(frame);if(audio){audio.pause();audio.onended=null;audio.onerror=null;audio.src=''}if(utterance){utterance.onend=null;utterance.onerror=null;window.speechSynthesis.cancel()}if(url)URL.revokeObjectURL(url)}
 return{play,pause,dispose,get paused(){return paused},get progress(){return progress}};
}
