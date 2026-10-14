import { startRobotScene } from './robot-scene.js';

const host = document.getElementById('robot-scene');
const status = document.getElementById('scene-status');
let controller;
startRobotScene(host, ({ available, playing }) => {
  status.textContent = available ? 'Robot scene ready. The robot avoids three blocks.' : 'Still image preview. Animated 3D is unavailable on this device.';
}).then(api => { controller = api; }).catch(error => {
  console.warn('Robot scene fallback:', error);
  status.textContent = 'Still image preview. The interactive robot scene could not load.';
});


// Topic links navigate to a dedicated assembly page.
