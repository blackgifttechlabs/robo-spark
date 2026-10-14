import * as THREE from 'three';
import { GLTFLoader } from '../../assets/vendor/three/addons/loaders/GLTFLoader.js';
export async function showPart(host,url){
 const renderer=new THREE.WebGLRenderer({antialias:true,alpha:true});renderer.setPixelRatio(Math.min(devicePixelRatio,1.5));renderer.outputColorSpace=THREE.SRGBColorSpace;renderer.toneMapping=THREE.ACESFilmicToneMapping;
 const scene=new THREE.Scene();scene.add(new THREE.HemisphereLight(0xffffff,0x6b8297,2.5));
 const light=new THREE.DirectionalLight(0xffffff,3);light.position.set(3,5,4);scene.add(light);
 const camera=new THREE.PerspectiveCamera(38,1,.01,100);let alive=true,model=null,frame,dragging=false,lastX=0,lastY=0,azimuth=.7,elevation=.5,radius=5;
 const observer=new ResizeObserver(()=>{const w=host.clientWidth,h=host.clientHeight;renderer.setSize(w,h,false);camera.aspect=w/Math.max(h,1);camera.updateProjectionMatrix()});observer.observe(host);
 const canvas=renderer.domElement;canvas.setAttribute('role','img');canvas.setAttribute('aria-label','Interactive 3D part. Drag to turn it and scroll to zoom.');canvas.tabIndex=0;
 host.append(canvas);
 function pointerDown(e){dragging=true;lastX=e.clientX;lastY=e.clientY;canvas.setPointerCapture(e.pointerId)}
 function pointerMove(e){if(!dragging)return;azimuth-=(e.clientX-lastX)*.008;elevation=THREE.MathUtils.clamp(elevation+(e.clientY-lastY)*.008,-1.2,1.2);lastX=e.clientX;lastY=e.clientY}
 function stop(){dragging=false}
 function wheel(e){e.preventDefault();radius=THREE.MathUtils.clamp(radius+e.deltaY*.004,2.5,9)}
 function key(e){if(!['ArrowLeft','ArrowRight','ArrowUp','ArrowDown','+','-'].includes(e.key))return;e.preventDefault();if(e.key==='ArrowLeft')azimuth-=.15;if(e.key==='ArrowRight')azimuth+=.15;if(e.key==='ArrowUp')elevation=Math.min(1.2,elevation+.1);if(e.key==='ArrowDown')elevation=Math.max(-1.2,elevation-.1);if(e.key==='+')radius=Math.max(2.5,radius-.3);if(e.key==='-')radius=Math.min(9,radius+.3)}
 canvas.addEventListener('pointerdown',pointerDown);canvas.addEventListener('pointermove',pointerMove);canvas.addEventListener('pointerup',stop);canvas.addEventListener('pointercancel',stop);canvas.addEventListener('wheel',wheel,{passive:false});canvas.addEventListener('keydown',key);
 function dispose(){alive=false;cancelAnimationFrame(frame);observer.disconnect();scene.traverse(o=>{o.geometry?.dispose();if(o.material){for(const m of Array.isArray(o.material)?o.material:[o.material])m.dispose()}});renderer.dispose();canvas.remove()}
 host.disposeViewer=dispose;
 try{
  const gltf=await new GLTFLoader().loadAsync(url);if(!alive){gltf.scene.traverse(o=>{o.geometry?.dispose();o.material?.dispose?.()});return dispose}
  model=gltf.scene;const bounds=new THREE.Box3().setFromObject(model),center=bounds.getCenter(new THREE.Vector3()),size=bounds.getSize(new THREE.Vector3());const span=Math.max(size.x,size.y,size.z);if(!Number.isFinite(span)||span<=0)throw Error('Empty model');
  const group=new THREE.Group();group.scale.setScalar(2.5/span);group.position.copy(center).multiplyScalar(-2.5/span);group.add(model);scene.add(group);host.querySelector('img')?.setAttribute('hidden','');
  function draw(){if(!alive)return;camera.position.set(radius*Math.cos(elevation)*Math.sin(azimuth),radius*Math.sin(elevation),radius*Math.cos(elevation)*Math.cos(azimuth));camera.lookAt(0,0,0);renderer.render(scene,camera);frame=requestAnimationFrame(draw)}draw();
  return dispose;
 }catch(error){dispose();throw error}
}
