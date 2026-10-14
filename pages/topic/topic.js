import { projects } from '../home/projects.js';
import { createAssemblyPlayer } from './assembly-player.js';
const $ = id => document.getElementById(id);
// The page uses <base href="/">, so an in-page #link would resolve to the home page; handle the skip link here.
document.querySelector('.skip-link')?.addEventListener('click', e => { e.preventDefault(); $('workbench').scrollIntoView(); });
// Clean URLs look like /topic/<id>/; ?topic=<id> still works as a fallback.
const id = location.pathname.match(/\/topic\/([^/]+)/)?.[1] || new URLSearchParams(location.search).get('topic');
const project = projects.find(p => p.id === id);
const guidance = {
  breadboard: ['Place the breadboard', 'Start with the base where the small circuit parts will sit.'],
  microcontroller: ['Add the controller', 'Place the board beside the breadboard. It will run the project’s instructions.'],
  'ultrasonic-sensor': ['Mount the distance sensor', 'Face the two round transducers toward the area you want to measure.'],
  'servo-actuator': ['Position the servo', 'Mount the servo firmly and keep room around its moving arm.'],
  'motor-driver': ['Add the motor driver', 'Place the driver near the motor. It controls the motor’s power.'],
  'temperature-sensor': ['Place the temperature sensor', 'Keep the sensor exposed to the air you want to measure.'],
  'motion-sensor': ['Position the motion sensor', 'Point the white lens toward the area where movement will happen.'],
  'light-sensor': ['Add the light sensor', 'Keep the round sensing surface clear so light can reach it.'],
  buzzer: ['Add the buzzer', 'Leave the sound opening uncovered so you can hear the signal.'],
  led: ['Place the indicator LED', 'Identify its two leads. A real LED circuit also needs a suitable resistor.'],
  'push-button': ['Add the push button', 'Keep the button within easy reach so you can trigger the project.'],
  'stepper-motor': ['Mount the stepper motor', 'Align the motor shaft with the part it needs to move.'],
};
// Clear sub-steps for every part (and the wiring / finishing stages), shown as a numbered timeline.
const substeps = {
  breadboard: ['Clear a flat, stable spot on your workbench.', 'Set the breadboard down with its long power rails along the edges.', 'Check the rows of holes are clean and facing up.'],
  microcontroller: ['Unplug the controller from any power source.', 'Place it next to the breadboard.', 'Turn it so the USB port faces the edge and the cable can reach.'],
  'ultrasonic-sensor': ['Hold the sensor with its two round “eyes” facing forward.', 'Line up its four pins: VCC, Trig, Echo and GND.', 'Mount it so nothing blocks the space it measures.'],
  'servo-actuator': ['Fix the servo base firmly in place.', 'Keep its arm free to swing all the way round.', 'Note the three wires: power, ground and signal.'],
  'motor-driver': ['Place the driver close to the motor it controls.', 'Find the power and motor terminal blocks.', 'Leave space around the board so it stays cool.'],
  'temperature-sensor': ['Position the sensor so air can flow around it.', 'Keep it away from warm parts like the controller.', 'Check which pin is signal, power and ground.'],
  'motion-sensor': ['Point the white dome toward where movement will happen.', 'Keep its view clear of walls and objects.', 'Check the three pins: power, signal and ground.'],
  'light-sensor': ['Set the sensor board where light can reach it.', 'Face the round sensing disc toward the light.', 'Check the three pins: power, signal and ground.'],
  buzzer: ['Place the buzzer where you can hear it.', 'Leave the sound opening uncovered.', 'Match the + mark to the positive side of the circuit.'],
  led: ['Find the two legs: the longer leg is positive.', 'Press the LED in with each leg in a separate row.', 'Remember a resistor is needed to protect it.'],
  'push-button': ['Place the button where your finger can reach it.', 'Press its pins firmly across the gap in the board.', 'Check it clicks without wobbling.'],
  'stepper-motor': ['Mount the motor on a firm base.', 'Line up the shaft with the part it will turn.', 'Keep the cable clear of the moving shaft.'],
  jumpers: ['Make sure the project is powered off before wiring.', 'Plug one end of each jumper into a sensor or module pin.', 'Plug the other end into the matching controller pin.', 'Match wire colours: red for power, black for ground.'],
  structure: ['Place the supporting parts around the electronics.', 'Check nothing blocks a sensor or a moving part.', 'Take a last look, then press play to watch it all work.'],
};
let player, stageData = [], previousStage = -1;
function update({ progress, playing, stage, count }) {
  $('assembly-progress').value = progress * 100;
  $('progress-label').textContent = `${Math.round(progress * 100)}%`;
  $('assembly-play').setAttribute('aria-label', playing ? 'Pause assembly' : progress === 1 ? 'Play again' : 'Play assembly');
  $('assembly-progress').style.setProperty('--p', `${progress * 100}%`);
  $('assembly-play').setAttribute('aria-pressed', String(playing));
  $('stage-count').textContent = `STEP ${String(stage + 1).padStart(2, '0')} / ${String(count).padStart(2, '0')}`;
  $('stage-title').textContent = stageData[stage]?.title || 'Prepare your workbench';
  $('view-status').textContent = progress === 1 ? 'Assembly complete · Explore your build' : playing ? 'Putting the parts together' : progress === 0 ? 'Ready when you are · Press play' : 'Paused · Look around your build';
  // Until the learner starts, show the finished project picture instead of the empty 3D scene.
  $('assembly-view').classList.toggle('is-intro', progress === 0 && !playing);
  renderStep(stage, count, progress);
}
// The sidebar shows one step at a time as a card; Next/Back move the 3D assembly a whole step.
function renderStep(stage, count, progress) {
  if (!stageData.length) return;
  // Show the step you are about to do: after k steps are built the card shows step k + 1.
  const finished = progress === 1;
  const idx = finished ? count - 1 : Math.min(count - 1, Math.floor(progress * count + 1e-6));
  const step = stageData[idx];
  if (!step) return;
  const card = $('step-card');
  if (idx !== previousStage) {
    $('step-title').textContent = step.title;
    $('step-label').textContent = `STEP ${idx + 1} OF ${count}`;
    $('step-text').textContent = step.description;
    const list = $('step-substeps'); list.textContent = '';
    step.steps.forEach((text, i) => {
      const li = document.createElement('li'); li.style.setProperty('--i', i);
      const dot = document.createElement('span'); dot.className = 'step-timeline__dot'; dot.textContent = i + 1;
      const copy = document.createElement('p'); copy.textContent = text;
      li.append(dot, copy); list.append(li);
    });
    card.classList.remove('is-swap'); void card.offsetWidth; card.classList.add('is-swap');
    previousStage = idx;
  }
  // Tick the sub-steps off as the 3D part for this step arrives.
  const frac = finished ? 1 : Math.min(1, Math.max(0, progress * count - idx));
  const total = step.steps.length, done = Math.floor(frac * total + 1e-6);
  $('step-substeps').querySelectorAll('li').forEach((li, i) => {
    li.classList.toggle('is-done', i < done);
    li.classList.toggle('is-current', i === done && !finished);
    li.querySelector('.step-timeline__dot').innerHTML = i < done ? '<i class="fi fi-rr-check" aria-hidden="true"></i>' : String(i + 1);
  });
  $('step-dots').querySelectorAll('button').forEach((dot, i) => {
    dot.classList.toggle('is-complete', i < idx || finished);
    dot.classList.toggle('is-current', i === idx && !finished);
  });
  $('step-prev').disabled = progress === 0;
  $('step-next').disabled = false;
  $('step-next').firstElementChild.textContent = finished ? 'Start over' : idx === count - 1 ? 'Finish' : 'Next step';
  $('step-next').lastElementChild.className = finished ? 'fi fi-rr-rotate-right' : idx === count - 1 ? 'fi fi-rr-check' : 'fi fi-rr-arrow-right';
}
async function init() {
  if (!project) {
    document.title = 'Topic not found — Robo Sparks';
    $('topic-content').innerHTML = '<div class="topic-error"><h1>Choose a learning topic.</h1><p>This topic could not be found.</p><a href="learn.html">Browse all topics →</a></div>';
    return;
  }
  document.title = `${project.title} — Robo Sparks`;
  $('topic-title').textContent = project.title;
  $('topic-category').textContent = `${project.category.toUpperCase()} · PROJECT ${String(projects.indexOf(project) + 1).padStart(2, '0')}`;
  $('topic-description').textContent = project.description;
  $('assembly-poster').src = project.image;
  $('assembly-poster').alt = `Assembled ${project.title}`;
  const next = projects[projects.indexOf(project) + 1];
  $('next-topic').href = next ? `topic/${next.id}/` : 'learn.html';
  if (!next) $('next-topic').textContent = 'All topics ↗';
  try {
    const response = await fetch('assets/assemblies/index.json');
    if (!response.ok) throw Error('Assembly index unavailable');
    const index = await response.json();
    const assembly = index[id];
    if (!assembly) throw Error('Assembly missing');
    stageData = assembly.stages.map(stage => {
      const [title, description] = guidance[stage.component] || (stage.label === 'Jumper connections' ? ['Connect the parts', 'Watch the leads join the modules. Use a circuit guide for the exact pins.'] : ['Add the project structure', 'Fit the supporting parts around the electronics to complete your project.']);
      const steps = substeps[stage.component] || (stage.label === 'Jumper connections' ? substeps.jumpers : substeps.structure);
      return { title, description, steps };
    });
    stageData.forEach((step, i) => {
      const dot = document.createElement('button'); dot.type = 'button'; dot.setAttribute('aria-label', `Go to step ${i + 1}: ${step.title}`);
      dot.addEventListener('click', () => player?.seek(i / stageData.length)); $('step-dots').append(dot);
    });
    $('step-next').addEventListener('click', () => {
      const n = stageData.length, p = player.progress;
      if (p === 1) return player.seek(0);
      player.playTo((Math.floor(p * n + 1e-6) + 1) / n);
    });
    $('step-prev').addEventListener('click', () => {
      const n = stageData.length, p = player.progress;
      player.seek(Math.max(0, ((p === 1 ? n : Math.floor(p * n + 1e-6)) - 1) / n));
    });
    player = await createAssemblyPlayer($('assembly-view'), assembly.model, update);
    for (const name of ['assembly-play', 'assembly-replay', 'assembly-progress']) $(name).disabled = false;
    $('assembly-play').addEventListener('click', () => player.toggle());
    $('assembly-replay').addEventListener('click', () => player.replay());
    $('assembly-progress').addEventListener('input', e => player.seek(Number(e.target.value) / 100));
    $('assembly-speed').addEventListener('change', e => player.setSpeed(Number(e.target.value)));
    $('reset-view').addEventListener('click', () => player.resetView());
    // Expose the player for browser checks without changing the page controls.
    $('assembly-view').assemblyPlayer = player;
    if (matchMedia('(prefers-reduced-motion: reduce)').matches) player.seek(1);
    addEventListener('pagehide', () => player.dispose(), { once: true });
  } catch (error) {
    console.warn('Assembly playback unavailable:', error);
    $('view-status').textContent = '3D playback could not load. The assembled project is shown below.';
    $('view-hint').textContent = 'Reload the page to try loading the 3D parts again.';
    $('reset-view').disabled = true;
    if (!stageData.length) {
      $('step-title').textContent = project.title; $('step-label').textContent = 'BUILD IT'; $('step-text').textContent = project.rule;
    }
  }
}
init();
