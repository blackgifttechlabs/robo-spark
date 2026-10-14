import * as THREE from 'three';
import { mergeGeometries } from '../../assets/vendor/three/addons/utils/BufferGeometryUtils.js';
import { GLTFLoader } from '../../assets/vendor/three/addons/loaders/GLTFLoader.js';

export async function startRobotScene(host, onState) {
  const reduce = matchMedia('(prefers-reduced-motion: reduce)').matches;
  let renderer;
  try {
    renderer = new THREE.WebGLRenderer({ antialias: true, alpha: false, powerPreference: 'high-performance' });
  } catch (_) {
    onState({ available: false, playing: false });
    return null;
  }
  renderer.setPixelRatio(Math.min(devicePixelRatio, 1.6));
  renderer.outputColorSpace = THREE.SRGBColorSpace;
  renderer.toneMapping = THREE.ACESFilmicToneMapping;
  renderer.toneMappingExposure = 1.1;
  renderer.shadowMap.enabled = true;
  renderer.shadowMap.type = THREE.PCFSoftShadowMap;
  const scene = new THREE.Scene();
  scene.background = new THREE.Color('#f7f8fa');
  const camera = new THREE.PerspectiveCamera(36, 1, 0.01, 30);
  const ambient = new THREE.HemisphereLight(0xffffff, 0x9daab5, 2.1);
  scene.add(ambient);
  const key = new THREE.DirectionalLight(0xffffff, 3.2);
  key.position.set(-1.5, 3.5, 1.5);
  key.castShadow = true;
  key.shadow.mapSize.set(2048, 2048);
  Object.assign(key.shadow.camera, { left: -2, right: 2, top: 2, bottom: -2, near: 0.1, far: 9 });
  key.shadow.bias = -0.00025;
  key.shadow.normalBias = 0.002;
  key.shadow.radius = 3;
  key.target.position.set(0, 0, 0);
  scene.add(key, key.target);
  const fill = new THREE.DirectionalLight(0xd9ecff, 1.1);
  fill.position.set(2, 2, -2);
  scene.add(fill);
  const [gltf, metadata] = await Promise.all([
    new GLTFLoader().loadAsync('assets/scene/robot-course.glb'),
    fetch('assets/scene/animation.json').then(r => { if (!r.ok) throw Error('Scene metadata'); return r.json(); }),
  ]).catch(error => { renderer.dispose(); throw error; });
  scene.add(gltf.scene);
  let robot = null;
  gltf.scene.traverse(o => {
    if (o.name.includes('Robot_assembly') || (o.name.includes('Robot') && o.name.includes('move_whole'))) robot = o;
    if (o.isMesh) {
      o.castShadow = !o.name.startsWith('White_');
      o.receiveShadow = true;
      const mats = Array.isArray(o.material) ? o.material : [o.material];
      mats.forEach(m => { if (m.name.includes('Warm timber')) { m.color.set('#b78a5c'); m.roughness = .8; } if (m.map) m.map.anisotropy = Math.min(8, renderer.capabilities.getMaxAnisotropy()); });
    }
  });
  if (!robot) robot = gltf.scene.children.find(o => o.name.includes('Robot'));
  if (!robot) throw Error('Robot assembly missing');
  // Bake static component transforms into material batches for smooth playback.
  // The five animated assembly controls remain separate, including all four wheels.
  scene.updateMatrixWorld(true);
  const batches = new Map();
  const originalMeshes = [];
  robot.traverse(o => {
    if (!o.isMesh || Array.isArray(o.material)) return;
    let parent = o.parent;
    while (parent && parent !== robot && !parent.name.includes('wheel_rotation')) parent = parent.parent;
    parent = parent || robot;
    const id = `${parent.uuid}:${o.material.uuid}`;
    if (!batches.has(id)) batches.set(id, { parent, material: o.material, geometry: [] });
    let g = o.geometry.clone();
    if (g.index) g = g.toNonIndexed();
    Object.keys(g.attributes).filter(k => !['position', 'normal', 'uv'].includes(k)).forEach(k => g.deleteAttribute(k));
    if (!g.attributes.normal) g.computeVertexNormals();
    if (!g.attributes.uv) g.setAttribute('uv', new THREE.BufferAttribute(new Float32Array(g.attributes.position.count * 2), 2));
    g.applyMatrix4(new THREE.Matrix4().copy(parent.matrixWorld).invert().multiply(o.matrixWorld));
    batches.get(id).geometry.push(g);
    originalMeshes.push(o);
  });
  for (const batch of batches.values()) {
    const g = mergeGeometries(batch.geometry, false);
    if (!g) continue;
    const mesh = new THREE.Mesh(g, batch.material);
    mesh.name = 'Optimized robot component batch';
    mesh.castShadow = mesh.receiveShadow = true;
    batch.parent.add(mesh);
  }
  originalMeshes.forEach(o => o.removeFromParent());
  const mixer = new THREE.AnimationMixer(gltf.scene);
  for (const clip of gltf.animations) mixer.clipAction(clip).setLoop(THREE.LoopRepeat, Infinity).play();
  const scanGeometry = new THREE.BufferGeometry().setFromPoints([new THREE.Vector3(0, .097, .13), new THREE.Vector3(0, .097, .31)]);
  const scan = new THREE.Line(scanGeometry, new THREE.LineBasicMaterial({ color: 0x00a7d6, transparent: true, opacity: .75 }));
  robot.add(scan);
  const clipEnd = Math.max(...gltf.animations.map(clip => clip.duration));
  let time = reduce ? 5 : 0;
  let playing = !reduce;
  let inView = true;
  let alive = true;
  let last = performance.now();
  const world = new THREE.Vector3();
  const target = new THREE.Vector3();
  const wide = new THREE.Vector3(0, .04, .10);
  function resize() {
    const w = host.clientWidth, h = host.clientHeight;
    camera.aspect = w / h;
    camera.updateProjectionMatrix();
    renderer.setSize(w, h, false);
    renderer.setPixelRatio(Math.min(devicePixelRatio, innerWidth < 700 ? 1.3 : 1.6));
  }
  const observer = new ResizeObserver(resize);
  observer.observe(host);
  host.appendChild(renderer.domElement);
  renderer.domElement.setAttribute('aria-hidden', 'true');
  resize();
  function draw() {
    if (!alive) return;
    const now = performance.now(), dt = Math.min((now - last) / 1000, .05);
    last = now;
    if (playing && inView && !document.hidden) time += dt;
    if (time > metadata.duration) time = 0;
    mixer.setTime(Math.min(time, clipEnd - .0001));
    robot.getWorldPosition(world);
    const u = THREE.MathUtils.smoothstep(time, 1, 3);
    target.copy(wide).lerp(new THREE.Vector3(world.x, .055, world.z + .20), u);
    const mobile = innerWidth < 700;
    // Wide establishing shot, then a stable close tracking camera.
    const distance = THREE.MathUtils.lerp(3.4, mobile ? 1.55 : 1.7, u);
    camera.position.copy(target).add(new THREE.Vector3(.55, .65, .82).normalize().multiplyScalar(distance));
    // Frame the robot to the right, leaving space for the headline.
    if (!mobile) target.x -= .19 * u;
    else target.y -= .12;
    camera.lookAt(target);
    scan.visible = metadata.detect.some(d => time >= d.start && time <= d.end);
    renderer.render(scene, camera);
    host.classList.add('is-ready');
    requestAnimationFrame(draw);
  }
  const visibility = new IntersectionObserver(entries => { inView = entries[0].isIntersecting; }, { threshold: .05 });
  visibility.observe(host);
  const api = {
    toggle() { playing = !playing; onState({ available: true, playing }); },
    replay() { time = 0; playing = true; onState({ available: true, playing }); },
    get playing() { return playing; },
    get time() { return time; },
    seek(t) { time = Math.max(0, Math.min(metadata.duration, t)); },
    dispose() { alive = false; observer.disconnect(); visibility.disconnect(); renderer.dispose(); },
  };
  onState({ available: true, playing });
  // Exposed for diagnostics and the sensor mission's "watch again" action.
  host.sceneController = api;
  requestAnimationFrame(draw);
  return api;
}
