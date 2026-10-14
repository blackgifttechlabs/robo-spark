import * as THREE from 'three';
import { GLTFLoader } from '../../assets/vendor/three/addons/loaders/GLTFLoader.js';

export async function createAssemblyPlayer(host, modelURL, onProgress) {
  const renderer = new THREE.WebGLRenderer({ antialias: true });
  renderer.setPixelRatio(Math.min(devicePixelRatio, 1.5));
  renderer.outputColorSpace = THREE.SRGBColorSpace;
  renderer.toneMapping = THREE.ACESFilmicToneMapping;
  renderer.toneMappingExposure = 1;
  const scene = new THREE.Scene();
  scene.background = new THREE.Color('#ffffff');
  scene.add(new THREE.HemisphereLight(0xffffff, 0x8c9dac, 2.4));
  for (const [x, y, z, energy] of [[-3, 5, 3, 2.3], [3, 3, -2, 1.3]]) {
    const light = new THREE.DirectionalLight(0xffffff, energy);
    light.position.set(x, y, z);
    scene.add(light);
  }
  const camera = new THREE.PerspectiveCamera(35, 1, .01, 100);
  let gltf;
  try { gltf = await new GLTFLoader().loadAsync(modelURL); }
  catch (error) { renderer.dispose(); throw error; }
  const model = gltf.scene;
  const bounds = new THREE.Box3().setFromObject(model);
  const size = bounds.getSize(new THREE.Vector3());
  const center = bounds.getCenter(new THREE.Vector3());
  const rawSize = Math.max(size.x, size.y, size.z);
  if (!Number.isFinite(rawSize) || rawSize <= 0) { renderer.dispose(); throw Error('Empty assembly model'); }
  const scale = 2.7 / rawSize;
  const normalizer = new THREE.Group();
  normalizer.scale.setScalar(scale);
  normalizer.position.set(-center.x * scale, -bounds.min.y * scale, -center.z * scale);
  normalizer.add(model); scene.add(normalizer);
  const stages = [];
  model.traverse(node => { if (Number.isFinite(node.userData.assembly_step)) stages.push(node); });
  stages.sort((a, b) => a.userData.assembly_step - b.userData.assembly_step);
  if (!stages.length) { renderer.dispose(); throw Error('Assembly stages missing'); }
  const originals = stages.map(node => node.position.clone());
  const origQuats = stages.map(node => node.quaternion.clone());
  scene.updateMatrixWorld(true);
  // Per-part pivot (its own centre) so parts spin and scale in place, plus clone materials so glow pulses stay per part.
  const pivots = stages.map(part => part.worldToLocal(new THREE.Box3().setFromObject(part).getCenter(new THREE.Vector3())));
  const worldCenters = stages.map((part, i) => part.localToWorld(pivots[i].clone()));
  const glowMats = stages.map(part => {
    const mats = [];
    part.traverse(node => { if (node.isMesh && node.material?.emissive) { node.material = node.material.clone(); mats.push(node.material); } });
    return mats;
  });
  const easeOutCubic = t => 1 - Math.pow(1 - t, 3);
  const easeOutBack = t => 1 + 2.70158 * Math.pow(t - 1, 3) + 1.70158 * Math.pow(t - 1, 2);
  const tmpQ = new THREE.Quaternion(), tmpE = new THREE.Euler(), tmpV = new THREE.Vector3();
  let progress = 0, playing = false, speed = 1, alive = true, stopAt = null;
  let azimuth = .65, elevation = .55, radius = 5.7;
  const target = new THREE.Vector3(0, size.y * scale * .45, 0);
  const defaultTarget = target.clone();
  const duration = Math.max(12, stages.length * 2.4);
  let last = performance.now(), dragging = false, pointerX = 0, pointerY = 0;
  function resize() {
    const { width, height } = host.getBoundingClientRect();
    camera.aspect = width / Math.max(1, height); camera.updateProjectionMatrix();
    renderer.setSize(width, height, false);
  }
  const observer = new ResizeObserver(resize); observer.observe(host);
  host.append(renderer.domElement); renderer.domElement.setAttribute('aria-label', 'Interactive 3D assembly. Drag to orbit.');
  renderer.domElement.setAttribute('role', 'img'); resize();
  let focusIndex = -1;
  function placeParts() {
    stages.forEach((part, index) => {
      const fraction = THREE.MathUtils.clamp(progress * stages.length - index, 0, 1);
      part.visible = fraction > 0;
      // Flight takes the first 75% of the stage; the last 25% is the settle: a small bounce and a glow pulse.
      const flight = THREE.MathUtils.clamp(fraction / .75, 0, 1);
      const settle = THREE.MathUtils.clamp((fraction - .75) / .25, 0, 1);
      const travel = 1 - easeOutCubic(flight);
      const angle = index * 2.4 + .6;
      const dir = tmpV.set(Math.cos(angle) * .75, .8, Math.sin(angle) * .75).multiplyScalar(rawSize * .7 * travel);
      const arc = Math.sin(Math.PI * flight) * rawSize * .22;
      const spin = (1 - easeOutBack(flight)) * (index % 2 ? 1 : -1) * Math.PI * 1.1;
      const tilt = travel * .5 * (index % 2 ? -1 : 1);
      const grow = THREE.MathUtils.lerp(.45, 1, easeOutBack(Math.min(1, flight * 1.1))) + Math.sin(Math.PI * settle) * .04;
      tmpQ.setFromEuler(tmpE.set(tilt, spin, 0));
      const u = pivots[index].clone().applyQuaternion(origQuats[index]);
      const centre = u.clone().multiplyScalar(grow).applyQuaternion(tmpQ);
      part.quaternion.copy(tmpQ).multiply(origQuats[index]);
      part.scale.setScalar(grow);
      part.position.copy(originals[index]).add(u).add(dir).add(new THREE.Vector3(0, arc, 0)).sub(centre);
      const pulse = Math.sin(Math.PI * settle);
      for (const m of glowMats[index]) m.emissive.setRGB(0, .32 * pulse, .55 * pulse);
      if (fraction > 0 && fraction < 1) focusIndex = index;
    });
    if (progress === 0 || progress === 1) focusIndex = -1;
    onProgress({ progress, playing, stage: Math.max(0, Math.min(stages.length - 1, Math.ceil(progress * stages.length) - 1)), count: stages.length });
  }
  function cameraPosition() {
    camera.position.set(target.x + radius * Math.cos(elevation) * Math.sin(azimuth), target.y + radius * Math.sin(elevation), target.z + radius * Math.cos(elevation) * Math.cos(azimuth));
    camera.lookAt(target);
  }
  function draw(now) {
    if (!alive) return;
    const dt = Math.min((now - last) / 1000, .05); last = now;
    if (playing && !document.hidden) {
      progress = Math.min(stopAt ?? 1, progress + dt * speed / duration);
      if (progress === 1 || progress === stopAt) { playing = false; stopAt = null; }
      placeParts();
    }
    if (playing && !dragging) {
      // Cinematic drift: a slow orbit that eases its focus toward the part currently arriving.
      azimuth += dt * .12 * speed;
      const want = focusIndex >= 0 ? defaultTarget.clone().lerp(worldCenters[focusIndex], .45) : defaultTarget;
      target.lerp(want, 1 - Math.exp(-dt * 2.5));
    } else if (!playing && !dragging && focusIndex < 0) target.lerp(defaultTarget, 1 - Math.exp(-dt * 3));
    cameraPosition(); renderer.render(scene, camera); requestAnimationFrame(draw);
  }
  const canvas = renderer.domElement;
  const down = e => { dragging = true; pointerX = e.clientX; pointerY = e.clientY; canvas.setPointerCapture(e.pointerId); };
  const move = e => { if (!dragging) return; azimuth -= (e.clientX - pointerX) * .007; elevation = THREE.MathUtils.clamp(elevation + (e.clientY - pointerY) * .005, .12, 1.3); pointerX = e.clientX; pointerY = e.clientY; };
  const up = () => { dragging = false; };
  const zoom = e => { e.preventDefault(); radius = THREE.MathUtils.clamp(radius * Math.exp(e.deltaY * .001), 2.7, 10); };
  canvas.addEventListener('pointerdown', down); canvas.addEventListener('pointermove', move); canvas.addEventListener('pointerup', up); canvas.addEventListener('pointercancel', up); canvas.addEventListener('wheel', zoom, { passive: false });
  placeParts(); host.classList.add('is-ready'); requestAnimationFrame(draw);
  const api = {
    toggle() { stopAt = null; if (progress === 1) progress = 0; playing = !playing; placeParts(); },
    playTo(value) { stopAt = THREE.MathUtils.clamp(value, 0, 1); playing = progress < stopAt; placeParts(); },
    replay() { stopAt = null; progress = 0; playing = true; placeParts(); },
    seek(value) { stopAt = null; progress = THREE.MathUtils.clamp(value, 0, 1); playing = false; placeParts(); },
    setSpeed(value) { speed = value; },
    resetView() { azimuth = .65; elevation = .55; radius = 5.7; target.copy(defaultTarget); },
    get progress() { return progress; },
    get playing() { return playing; },
    dispose() { alive = false; observer.disconnect(); renderer.dispose(); scene.traverse(o => { o.geometry?.dispose(); if (o.material) for (const m of Array.isArray(o.material) ? o.material : [o.material]) m.dispose(); }); },
  };
  return api;
}
