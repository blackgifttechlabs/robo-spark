let context,enabled=true;
export function setSoundEnabled(value){enabled=value}
export function unlockSound(){if(!context)context=new (window.AudioContext||window.webkitAudioContext)();if(context.state==='suspended')context.resume().catch(()=>{})}
export function playSound(kind){
 if(!enabled)return;try{unlockSound()}catch{return}
 const sounds={connect:[[650,0,.06],[1000,.07,.09]],success:[[520,0,.09],[660,.1,.09],[780,.2,.15]],dodge:[[300,0,.08],[220,.09,.1]],scan:[[880,0,.05],[1200,.08,.05],[760,.16,.06]],pickup:[[440,0,.07],[600,.06,.07]]};
 for(const [frequency,offset,duration] of sounds[kind]||sounds.connect){const oscillator=context.createOscillator(),gain=context.createGain();oscillator.type=kind==='scan'?'sine':'triangle';oscillator.frequency.value=frequency;gain.gain.setValueAtTime(0,context.currentTime+offset);gain.gain.linearRampToValueAtTime(.035,context.currentTime+offset+.008);gain.gain.exponentialRampToValueAtTime(.0001,context.currentTime+offset+duration);oscillator.connect(gain);gain.connect(context.destination);oscillator.start(context.currentTime+offset);oscillator.stop(context.currentTime+offset+duration+.02)}
}
export function botHello(){if(!enabled)return;const sound=new Audio('assets/audio/robot-beeps-jofae.mp3');sound.volume=.13;sound.play().catch(()=>playSound('scan'))}
