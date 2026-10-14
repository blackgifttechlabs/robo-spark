import * as THREE from 'three';
import { GLTFLoader } from '../../assets/vendor/three/addons/loaders/GLTFLoader.js';
export async function createStoryStage(host,parts){
 const renderer=new THREE.WebGLRenderer({antialias:true,alpha:true});renderer.setPixelRatio(Math.min(devicePixelRatio,1.5));renderer.outputColorSpace=THREE.SRGBColorSpace;renderer.toneMapping=THREE.ACESFilmicToneMapping;
 const scene=new THREE.Scene(),camera=new THREE.PerspectiveCamera(38,1,.01,100);camera.position.set(0,4.4,7.8);camera.lookAt(0,0,0);
 scene.add(new THREE.HemisphereLight(0xffffff,0x8facc3,2.8));const key=new THREE.DirectionalLight(0xffffff,3);key.position.set(-3,5,5);scene.add(key);
 const floor=new THREE.Mesh(new THREE.CylinderGeometry(3,3,.08,64),new THREE.MeshStandardMaterial({color:0xeaf2f7,roughness:.9}));floor.position.y=-.45;scene.add(floor);
 const loader=new GLTFLoader(),models=new Map(),positions=new Map(),placed=new Set();let alive=true,frame,focus=null,fraction=0,wireFraction=0,connected=false,azimuth=0,spinTime=0,lastFrame=0,running=false,dragging=false,lastX=0;
 const count=parts.length;parts.forEach((id,i)=>{const angle=i/count*Math.PI*2-Math.PI/2;positions.set(id,new THREE.Vector3(Math.cos(angle)*1.9,-.25,Math.sin(angle)*1.35))});
 const lines=new THREE.Group();scene.add(lines);let activeLines=[];
 function makeLines(){for(let i=0;i<count;i++){const a=positions.get(parts[i]),b=positions.get(parts[(i+1)%count]);const mid=a.clone().lerp(b,.5);mid.y=.05;const curve=new THREE.CatmullRomCurve3([a.clone().add(new THREE.Vector3(0,.15,0)),mid,b.clone().add(new THREE.Vector3(0,.15,0))]);const geometry=new THREE.TubeGeometry(curve,24,.024,6,false),material=new THREE.MeshStandardMaterial({color:0x06a6d9,emissive:0x00658a,emissiveIntensity:.5});const line=new THREE.Mesh(geometry,material);line.visible=false;lines.add(line);activeLines.push(line)}}makeLines();
 const canvas=renderer.domElement;canvas.setAttribute('role','img');canvas.setAttribute('aria-label','Animated 3D robotics lesson. Parts turn, move into place and connect as Sparks explains.');host.append(canvas);
 const observer=new ResizeObserver(()=>{renderer.setSize(host.clientWidth,host.clientHeight,false);camera.aspect=host.clientWidth/Math.max(host.clientHeight,1);camera.updateProjectionMatrix()});observer.observe(host);
 canvas.addEventListener('pointerdown',e=>{dragging=true;lastX=e.clientX;canvas.setPointerCapture(e.pointerId)});canvas.addEventListener('pointermove',e=>{if(dragging){azimuth+=(e.clientX-lastX)*.008;lastX=e.clientX}});canvas.addEventListener('pointerup',()=>dragging=false);canvas.addEventListener('pointercancel',()=>dragging=false);
 function release(object){object.traverse(o=>{o.geometry?.dispose();if(o.material)for(const m of Array.isArray(o.material)?o.material:[o.material])m.dispose()})}
 function dispose(){alive=false;cancelAnimationFrame(frame);observer.disconnect();release(scene);renderer.dispose();canvas.remove()}
 host.disposeViewer=dispose;
 const loading=parts.map(async id=>{
  try{const gltf=await loader.loadAsync(`models/robotics-kit/web/${id}.glb`);if(!alive){release(gltf.scene);return}
   const model=gltf.scene,bounds=new THREE.Box3().setFromObject(model),center=bounds.getCenter(new THREE.Vector3()),size=bounds.getSize(new THREE.Vector3()),span=Math.max(size.x,size.y,size.z);if(!span)return;
   const normalizer=new THREE.Group();normalizer.scale.setScalar(1.2/span);normalizer.position.copy(center).multiplyScalar(-1.2/span);normalizer.add(model);const group=new THREE.Group();group.add(normalizer);group.visible=false;scene.add(group);models.set(id,group);
  }catch{host.dispatchEvent(new CustomEvent('part-model-error',{detail:id}))}
 });
 const reduced=matchMedia('(prefers-reduced-motion: reduce)').matches;
 function draw(time){if(!alive)return;const delta=Math.min(.05,(time-lastFrame)/1000);lastFrame=time;if(running)spinTime+=Math.max(0,delta);
  for(const [id,model] of models){const dest=positions.get(id);model.visible=placed.has(id)||focus===id;if(!model.visible)continue;
   if(focus===id){const move=THREE.MathUtils.smoothstep(fraction,.53,.93);const inspection=new THREE.Vector3(0,.65,.3);model.position.copy(inspection).lerp(dest,move);model.rotation.y=reduced?0:spinTime*.5*(1-move);model.scale.setScalar(1.5-.5*move)}else{model.position.copy(dest);model.rotation.y=0;model.scale.setScalar(1)}
  }
  activeLines.forEach((line,i)=>line.visible=connected||wireFraction>(i+1)/count);
  camera.position.set(Math.sin(azimuth)*8,4.4,Math.cos(azimuth)*8);camera.lookAt(0,0,0);renderer.render(scene,camera);frame=requestAnimationFrame(draw)
 }draw(0);
 await Promise.allSettled(loading);
 return {setPlaying(value){running=value},focus(id){focus=id;fraction=0;spinTime=0},progress(value){fraction=value},place(id){placed.add(id);focus=null;fraction=0},connections(value){wireFraction=value;connected=value>=1},reset(){placed.clear();focus=null;connected=false;wireFraction=0},dispose};
}
