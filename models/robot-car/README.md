# Robot car in a white studio

Open `robot-white-room.blend`. The active scene is `Robot • White Studio`; the original Blender startup scene is preserved separately.

The robot has four wheels with tread and spokes, yellow motors, clear acrylic chassis plates, metal spacers, an Arduino-style board with individual electronic components, a four-cell battery holder with springs and four red HUATAI reference-style batteries, a twin ultrasonic sensor with grille geometry, and coloured jumper wires. Dimensions are approximate visual proportions inferred from the supplied image, not measured CAD specifications.

Collections separate the room, chassis, wheels/motors, board, battery, sensor, wiring and cameras/lights. Move the `Robot assembly • move whole robot` empty to move the full robot. Rotate each named wheel control around X to spin its wheel.

Six cameras are available: Hero, Front, Rear, Left, Right and Top. Numpad 0 toggles the camera view. Middle mouse orbits the scene. Viewport overlays are initially hidden; Use the viewport overlay button to show overlays when needed.

`robot-white-room.png` is the inspected hero render. The numbered Python scripts record the live build stages; `live_bridge.py` executes those stages through the locally installed Blender bridge. They are not required to open or edit the model.

## Three-block avoidance animation

The white room is enlarged to 8 metres. Press Space in Blender to play or pause the 518-frame animation (21.58 seconds at 24 fps). The robot stops briefly before each of three timber blocks; a cyan line indicates the detection moment. It then steers around the block and continues. This is a choreographed demonstration rather than autonomous sensor or physics simulation.

Wheel spin is calculated from travel distance and steering angle, so the inner and outer wheels turn at different speeds during turns and stop when the robot stops. Every frame was checked against all three blocks using a conservative robot footprint with 18 mm of extra clearance.

The Hero camera starts wide and moves into a tracking view. `Obstacle course overview camera` provides a fixed view of all three blocks. Timeline markers identify each detection pause. All robot parts follow the assembly control, and collections group the individual components. Studio lighting is reduced to keep colours and details visible.

`obstacle-course.mp4` is the rendered animation preview; `animation-validation.json` records route and clearance checks.
