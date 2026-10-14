export const projects = [
  {
    "id": "led-traffic-light",
    "title": "LED Traffic Light",
    "category": "Circuits",
    "description": "Sequence red, amber and green lights like a real junction.",
    "parts": "LEDs, resistors, breadboard, controller",
    "rule": "Change one light at a time, then repeat the sequence.",
    "question": "What controls the order of the lights?",
    "answer": "The program",
    "options": [
      "The program",
      "The wire colour"
    ],
    "image": "assets/projects/led-traffic-light.webp"
  },
  {
    "id": "plant-soil-moisture-sensor",
    "title": "Plant Soil Moisture Sensor",
    "category": "Sensors",
    "description": "Discover when a plant\u2019s soil is dry or damp.",
    "parts": "Soil moisture probe, plant pot, controller",
    "rule": "Compare readings in dry and damp soil to choose a useful threshold.",
    "question": "What does the probe measure?",
    "answer": "Soil moisture",
    "options": [
      "Soil moisture",
      "Plant height"
    ],
    "image": "assets/projects/plant-soil-moisture-sensor.webp"
  },
  {
    "id": "laser-tripwire-alarm",
    "title": "Laser Tripwire Alarm",
    "category": "Sensors",
    "description": "Detect when an object interrupts a beam of light.",
    "parts": "Low-power light source, light sensor, buzzer, controller",
    "rule": "Watch the sensor reading change when the light path is blocked.",
    "question": "What triggers the alarm?",
    "answer": "A blocked beam",
    "options": [
      "A blocked beam",
      "A louder sound"
    ],
    "image": "assets/projects/laser-tripwire-alarm.webp"
  },
  {
    "id": "sweeping-radar",
    "title": "Sweeping Radar",
    "category": "Movement",
    "description": "Scan nearby objects with a rotating distance sensor.",
    "parts": "Ultrasonic sensor, servo, controller",
    "rule": "Turn the servo a little, measure distance, then repeat across the scan.",
    "question": "Which part rotates the sensor?",
    "answer": "The servo",
    "options": [
      "The servo",
      "The buzzer"
    ],
    "image": "assets/projects/sweeping-radar.webp"
  },
  {
    "id": "automatic-night-light",
    "title": "Automatic Night Light",
    "category": "Sensors",
    "description": "Make a lamp switch on as the room gets darker.",
    "parts": "Light sensor, LED, resistor, controller",
    "rule": "Read the light level and turn on the LED below a chosen threshold.",
    "question": "When should the lamp turn on?",
    "answer": "When it is dark",
    "options": [
      "When it is dark",
      "When it is bright"
    ],
    "image": "assets/projects/automatic-night-light.webp"
  },
  {
    "id": "auto-plant-waterer",
    "title": "Auto Plant Waterer",
    "category": "Automation",
    "description": "Use soil readings to give a plant water when it needs it.",
    "parts": "Moisture probe, low-voltage pump, motor driver, tubing",
    "rule": "Read the soil, run the pump briefly if dry, then pause before measuring again.",
    "question": "Why pause after watering?",
    "answer": "To let water soak in",
    "options": [
      "To let water soak in",
      "To dry the plant"
    ],
    "image": "assets/projects/auto-plant-waterer.webp"
  },
  {
    "id": "mood-lamp",
    "title": "Mood Lamp",
    "category": "Circuits",
    "description": "Mix red, green and blue light to create your own colours.",
    "parts": "RGB LED, resistors, controller",
    "rule": "Change the brightness of the three colour channels to mix a new colour.",
    "question": "How do you change the colour?",
    "answer": "Mix RGB brightness levels",
    "options": [
      "Mix RGB brightness levels",
      "Change the wire length"
    ],
    "image": "assets/projects/mood-lamp.webp"
  },
  {
    "id": "motion-activated-hallway-light",
    "title": "Motion-Activated Hallway Light",
    "category": "Sensors",
    "description": "Light up a miniature hallway when someone moves nearby.",
    "parts": "PIR motion sensor, LED, resistor, controller",
    "rule": "When motion is detected, light the LED and keep it on for a short time.",
    "question": "Which part detects motion?",
    "answer": "The PIR sensor",
    "options": [
      "The PIR sensor",
      "The LED"
    ],
    "image": "assets/projects/motion-activated-hallway-light.webp"
  },
  {
    "id": "countdown-timer",
    "title": "Countdown Timer",
    "category": "Coding",
    "description": "Count down the seconds and signal when time is up.",
    "parts": "Digit display, buttons, buzzer, controller",
    "rule": "Choose a starting time, subtract one each second, and buzz at zero.",
    "question": "When should the buzzer sound?",
    "answer": "At zero",
    "options": [
      "At zero",
      "At every number"
    ],
    "image": "assets/projects/countdown-timer.webp"
  },
  {
    "id": "desk-thermometer",
    "title": "Desk Thermometer",
    "category": "Sensors",
    "description": "Read the temperature and show it on a desk display.",
    "parts": "Temperature sensor, display, controller",
    "rule": "Read the sensor regularly and update the display with the temperature.",
    "question": "What provides the temperature reading?",
    "answer": "The sensor",
    "options": [
      "The sensor",
      "The display"
    ],
    "image": "assets/projects/desk-thermometer.webp"
  },
  {
    "id": "servo-turret",
    "title": "Servo Turret",
    "category": "Movement",
    "description": "Aim a small rotating platform with a servo motor.",
    "parts": "Servo, lightweight platform, controller",
    "rule": "Choose an angle within the servo range and move the platform to it.",
    "question": "What tells the servo where to turn?",
    "answer": "An angle command",
    "options": [
      "An angle command",
      "The LED colour"
    ],
    "image": "assets/projects/servo-turret.webp"
  },
  {
    "id": "tv-style-remote-lamp",
    "title": "TV-Style Remote Lamp",
    "category": "Communication",
    "description": "Switch a lamp using buttons on an infrared remote.",
    "parts": "IR remote, IR receiver, LED, controller",
    "rule": "Read the received button code and toggle the LED for your chosen button.",
    "question": "Which part receives the remote signal?",
    "answer": "The IR receiver",
    "options": [
      "The IR receiver",
      "The lamp"
    ],
    "image": "assets/projects/tv-style-remote-lamp.webp"
  },
  {
    "id": "camera-slider",
    "title": "Camera Slider",
    "category": "Movement",
    "description": "Move a small camera smoothly along a miniature track.",
    "parts": "Rails, carriage, stepper motor, motor driver, controller",
    "rule": "Move the motor in small steps and stop before the carriage reaches the rail end.",
    "question": "What makes the movement gradual?",
    "answer": "Small motor steps",
    "options": [
      "Small motor steps",
      "A brighter LED"
    ],
    "image": "assets/projects/camera-slider.webp"
  },
  {
    "id": "bluetooth-lamp-control",
    "title": "Bluetooth Lamp Control",
    "category": "Communication",
    "description": "Send a wireless command to control a small lamp.",
    "parts": "Bluetooth module, LED, controller, phone",
    "rule": "Send an on or off command and let the controller update the LED.",
    "question": "How does the command travel?",
    "answer": "Over Bluetooth",
    "options": [
      "Over Bluetooth",
      "Through the lamp shade"
    ],
    "image": "assets/projects/bluetooth-lamp-control.webp"
  },
  {
    "id": "pedestrian-crossing-lights",
    "title": "Pedestrian Crossing Lights",
    "category": "Circuits",
    "description": "Build a crossing that responds to a pedestrian button.",
    "parts": "Red and green LEDs, resistors, button, controller",
    "rule": "Wait for a button press, change the signals in order, then reset.",
    "question": "What starts the crossing sequence?",
    "answer": "A button press",
    "options": [
      "A button press",
      "A temperature change"
    ],
    "image": "assets/projects/pedestrian-crossing-lights.webp"
  },
  {
    "id": "temperature-warning-system",
    "title": "Temperature Warning System",
    "category": "Sensors",
    "description": "Sound an alert when a temperature crosses your limit.",
    "parts": "Temperature sensor, buzzer, warning LED, controller",
    "rule": "Compare the measured temperature with a threshold and alert above it.",
    "question": "When should the alert activate?",
    "answer": "Above the threshold",
    "options": [
      "Above the threshold",
      "At every reading"
    ],
    "image": "assets/projects/temperature-warning-system.webp"
  },
  {
    "id": "mini-musical-piano",
    "title": "Mini Musical Piano",
    "category": "Circuits",
    "description": "Turn button presses into a little electronic melody.",
    "parts": "Buttons, piezo buzzer, breadboard, controller",
    "rule": "Give each button a note and play that frequency while the button is pressed.",
    "question": "What changes a note\u2019s pitch?",
    "answer": "The sound frequency",
    "options": [
      "The sound frequency",
      "The button colour"
    ],
    "image": "assets/projects/mini-musical-piano.webp"
  },
  {
    "id": "smart-doorbell",
    "title": "Smart Doorbell",
    "category": "Automation",
    "description": "Make a button announce a visitor with a friendly chime.",
    "parts": "Push button, buzzer, controller",
    "rule": "Detect one press, play the chime, then wait for the next press.",
    "question": "Which component makes the chime?",
    "answer": "The buzzer",
    "options": [
      "The buzzer",
      "The button"
    ],
    "image": "assets/projects/smart-doorbell.webp"
  },
  {
    "id": "electronic-dice",
    "title": "Electronic Dice",
    "category": "Coding",
    "description": "Press a button to roll a number using a light-up dice.",
    "parts": "Seven LEDs, resistors, button, controller",
    "rule": "Pick a number from one to six and show its matching LED pattern.",
    "question": "Which numbers can the dice show?",
    "answer": "One to six",
    "options": [
      "One to six",
      "One to ten"
    ],
    "image": "assets/projects/electronic-dice.webp"
  },
  {
    "id": "rainbow-led-button-game",
    "title": "Rainbow LED Button Game",
    "category": "Coding",
    "description": "Match colourful lights with the right button presses.",
    "parts": "Coloured LEDs, buttons, resistors, controller",
    "rule": "Show a short light sequence and check whether the player repeats it.",
    "question": "What should the player repeat?",
    "answer": "The light sequence",
    "options": [
      "The light sequence",
      "The wire layout"
    ],
    "image": "assets/projects/rainbow-led-button-game.webp"
  },
  {
    "id": "mini-parking-sensor",
    "title": "Mini Parking Sensor",
    "category": "Sensors",
    "description": "Help a toy car detect when an obstacle is getting close.",
    "parts": "Ultrasonic sensor, buzzer, indicator LEDs, controller",
    "rule": "Measure the distance and make the warning faster as the object gets closer.",
    "question": "What does a faster warning mean?",
    "answer": "The obstacle is closer",
    "options": [
      "The obstacle is closer",
      "The battery is fuller"
    ],
    "image": "assets/projects/mini-parking-sensor.webp"
  },
  {
    "id": "electronic-reaction-game",
    "title": "Electronic Reaction Game",
    "category": "Coding",
    "description": "See how quickly you can press a button after a light.",
    "parts": "LED, buttons, display, controller",
    "rule": "Wait a random time, turn on the LED, then measure the delay until the press.",
    "question": "When does timing begin?",
    "answer": "When the light turns on",
    "options": [
      "When the light turns on",
      "Before the random wait"
    ],
    "image": "assets/projects/electronic-reaction-game.webp"
  },
  {
    "id": "rain-detector-alarm",
    "title": "Rain Detector Alarm",
    "category": "Sensors",
    "description": "Detect droplets landing on a small rain sensor plate.",
    "parts": "Rain sensor plate, buzzer, controller",
    "rule": "Compare dry and wet readings and trigger a buzzer when water is detected.",
    "question": "What changes the sensor reading?",
    "answer": "Water on the plate",
    "options": [
      "Water on the plate",
      "The buzzer volume"
    ],
    "image": "assets/projects/rain-detector-alarm.webp"
  },
  {
    "id": "mini-smart-house",
    "title": "Mini Smart House",
    "category": "Automation",
    "description": "Bring lights, sensors and a moving door into one tiny house.",
    "parts": "Miniature house, LEDs, sensors, servo, controller",
    "rule": "Create separate rules for the lights and door, then test how they work together.",
    "question": "What connects sensor readings to actions?",
    "answer": "Programmed rules",
    "options": [
      "Programmed rules",
      "The house paint"
    ],
    "image": "assets/projects/mini-smart-house.webp"
  }
];
