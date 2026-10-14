"""Expanded editable robotics kit. Run in Blender GUI for a staged visible build."""
import bpy, math, json, time, traceback
from pathlib import Path
from mathutils import Vector
ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/'models/robotics-kit'
for folder in ['components','web','previews']: (OUT/folder).mkdir(exist_ok=True)
# Reuse the existing library's mesh construction tools without running its rebuild.
source=(ROOT/'models/robotics-library/build_library.py').read_text()
exec(compile(source.split('# A timer yields back')[0],str(ROOT/'models/robotics-library/build_library.py'),'exec'),globals())
OUT=ROOT/'models/robotics-kit'
M={}
for args in MATERIAL_SPECS:
    M[args[0]]=bpy.data.materials.get(args[0]) or mat(*args)
mat('aluminium',(.46,.49,.53),.9,.28)
mat('acrylic',(.25,.65,.8),0,.18,.35)
mat('ledGlass',(.85,.12,.08),0,.18,.45)
mat('brass',(.65,.43,.14),.8,.3)
mat('silicone',(.8,.9,.94),0,.38,.35)
mat('pcbPurple',(.23,.035,.39))
mat('resistorBlue',(.12,.46,.64))
# name, category, nominal presentation span, explanation; dimensions are visual assumptions.
SPECS=[
('aa-battery','AA battery','Power',60,'Stores energy to power a small circuit.'),
('battery-pack','Rechargeable battery pack','Power',85,'Supplies energy for a moving robot.'),
('usb-cable','USB cable','Power',110,'Connects a controller to a computer.'),
('resistor','Resistor','Circuits',38,'Limits current through a circuit.'),
('slide-switch','Slide switch','Circuits',30,'Opens or closes an electrical path.'),
('nano-controller','Nano-style controller','Controllers',60,'Runs instructions on a compact board.'),
('microbit','micro:bit-style board','Controllers',70,'Combines buttons, lights and a programmable controller.'),
('esp32','ESP32-style controller','Controllers',70,'Runs instructions and supports wireless projects.'),
('servo-driver','16-channel servo driver','Controllers',80,'Sends position commands to several servos.'),
('rgb-led','RGB LED','Lights and sound',35,'Combines red, green and blue light.'),
('led-strip','Addressable LED strip','Lights and sound',105,'Contains a row of individually controlled lights.'),
('led-matrix','8 x 8 LED matrix','Lights and sound',60,'Displays pictures using a grid of lights.'),
('speaker','Small speaker','Lights and sound',55,'Turns an electrical signal into sound.'),
('line-sensor','Line-tracking sensor array','Sensors',75,'Detects dark and light patches under a rover.'),
('soil-probe','Soil moisture probe','Sensors',95,'Measures changes related to soil moisture.'),
('rain-sensor','Rain sensor plate','Sensors',65,'Detects water bridging conductive tracks.'),
('touch-sensor','Capacitive touch sensor','Sensors',40,'Detects a finger touching its sensing area.'),
('tilt-sensor','Tilt sensor module','Sensors',45,'Detects a change in orientation.'),
('hall-sensor','Magnetic sensor','Sensors',45,'Detects a nearby magnet.'),
('sound-sensor','Microphone sensor','Sensors',50,'Measures sound level.'),
('colour-sensor','Colour sensor','Sensors',45,'Measures the colour of reflected light.'),
('rotary-encoder','Rotary encoder','Sensors',40,'Measures steps as a knob or shaft turns.'),
('imu-sensor','Motion and orientation sensor','Sensors',40,'Measures acceleration and rotation.'),
('large-servo','Metal-gear servo','Movement',70,'Moves an arm to a chosen position.'),
('water-pump','Mini water pump','Movement',65,'Moves water through tubing.'),
('fan','Small cooling fan','Movement',65,'Spins blades to move air.'),
('caster','Ball caster','Structures',40,'Supports a rover while allowing it to turn.'),
('robot-tracks','Robot track assembly','Structures',125,'Uses a continuous tread to move a rover.'),
('chassis','Rover chassis plate','Structures',160,'Supports the robot parts.'),
('bracket','Motor mounting bracket','Structures',55,'Holds a motor on the chassis.'),
('beam','Perforated construction beam','Structures',110,'Joins parts into a strong structure.'),
('axle','Steel axle','Structures',90,'Carries a wheel or gear.'),
('bearing','Ball bearing','Structures',40,'Supports a rotating shaft with less friction.'),
('fastener-set','Screw, nut and spacer set','Structures',50,'Fastens robot parts together.'),
('spur-gear','Spur gear','Mechanisms',60,'Transfers rotation through matching teeth.'),
('pulley','Grooved pulley','Mechanisms',50,'Transfers movement using a belt.'),
('drive-belt','Drive belt','Mechanisms',100,'Carries motion between pulleys.'),
('gripper','Robot gripper','Mechanisms',105,'Opens and closes to hold an object.'),
('arm-link','Robot arm link','Mechanisms',110,'Connects two robot joints.'),
('hinge','Hinge','Mechanisms',55,'Lets two parts pivot.'),
('rack-pinion','Rack and pinion','Mechanisms',110,'Changes rotation into straight movement.'),
('lifting-platform','Scissor lifting platform','Mechanisms',110,'Raises a platform through linked arms.'),
('oled-display','Small OLED display','Controls',55,'Shows words and numbers.'),
('seven-segment','Seven-segment display','Controls',55,'Shows a digit using seven light segments.'),
('joystick','Joystick module','Controls',65,'Lets you choose direction with a thumb.'),
('keypad','4 x 4 keypad','Controls',80,'Lets you enter commands using buttons.'),
('remote-control','Infrared remote','Controls',105,'Sends button commands using infrared light.'),
('water-tubing','Flexible water tubing','Accessories',100,'Carries water from a pump.'),
('conveyor','Mini conveyor','Accessories',150,'Carries objects on a moving belt.'),
('pen-holder','Drawing robot pen holder','Accessories',65,'Holds a pen above the drawing surface.'),
]
OLD=json.loads((ROOT/'models/robotics-library/manifest.json').read_text())
CATALOG={'units':'mm','accuracy':'Representative educational models. Nominal proportions; not manufacturer CAD or validated wiring diagrams.',
'references':{'nano-controller':'https://docs.arduino.cc/resources/datasheets/A000005-datasheet.pdf','microbit':'https://tech.microbit.org/docs/hardware/assets/Microbit_V2_Assembly.pdf','servo-driver':'https://learn.adafruit.com/16-channel-pwm-servo-driver/downloads'},'components':[]}
LIB={}
for entry in OLD['components']:
    col=bpy.data.collections.get('PART • '+entry['id'])
    if col:
        LIB[entry['id']]=col
        CATALOG['components'].append({**entry,'category':'Existing library','blend':'../robotics-library/'+entry['blend'],'provenance':'Existing approximate reconstruction'})

def hole(p,r=1.5):
    # Actual mounting bores cut through the current solid. Keep separate bevelled plate faces.
    cyl('Dark mounting recess',p,r,.15,'black')
    torus('Mounting rim',p,r+.25,.18,'silver')

def plate(name,p,d,holes=(),material='aluminium'):
    o=box(name,p,d,material,.5)
    for x,y,r in holes:
        bpy.ops.mesh.primitive_cylinder_add(vertices=24,radius=r,depth=d[2]+4,location=(x,y,p[2]))
        cutter=bpy.context.object
        mod=o.modifiers.new('Through bore','BOOLEAN');mod.operation='DIFFERENCE';mod.solver='FAST';mod.object=cutter
        bpy.context.view_layer.objects.active=o
        bpy.ops.object.modifier_apply(modifier=mod.name);bpy.data.objects.remove(cutter,do_unlink=True)
    return o

def chip(p=(0,0,3),size=(8,8,2),n=6):
    box('Integrated circuit',p,size,'black',.2)
    for i in range(n):
        for side in [-1,1]:box('IC solder leg',(p[0]-size[0]/2+1+i*(size[0]-2)/max(1,n-1),p[1]+side*(size[1]/2+.6),p[2]-.5),(.5,1.5,.4),'silver',.04)
    cyl('Pin one dot',(p[0]-size[0]/2+1,p[1]-size[1]/2+1,p[2]+size[2]/2+.05),.35,.08,'white',vertices=12)

def module(w,h,label,n=3,color='blue'):
    pcb(w,h,color);text(label,(0,h/2-4,1.95),2)
    header((-w/2+3,-(n-1)*1.27,2),n,'Y');smd((-w/2+8,-h/2+4,2.2),4)

def bar(name,a,b,width,depth,m='aluminium'):
    mid=(Vector(a)+Vector(b))/2;length=(Vector(b)-Vector(a)).length
    o=box(name,mid,(width,depth,length),m,.4);o.rotation_euler=(Vector(b)-Vector(a)).to_track_quat('Z','Y').to_euler();return o

def ring_mesh(name,p,outer,inner,height,m='silver',segments=64):
    verts=[];faces=[]
    for z in [-height/2,height/2]:
        for r in [outer,inner]:
            verts += [(p[0]+r*math.cos(i*math.tau/segments),p[1]+r*math.sin(i*math.tau/segments),p[2]+z) for i in range(segments)]
    for i in range(segments):
        j=(i+1)%segments
        for a,b in [(0,2),(1,3),(0,1),(2,3)]:faces.append((a*segments+i,a*segments+j,b*segments+j,b*segments+i))
    mesh=bpy.data.meshes.new(name);mesh.from_pydata(verts,[],faces);mesh.update();o=bpy.data.objects.new(name,mesh);C.objects.link(o);o.data.materials.append(M[m]);
    for f in mesh.polygons:f.use_smooth=True
    return o

def build(slug):
    if slug=='aa-battery':
        cyl('AA steel cell',(0,0,8),7.2,50,'silver','X');cyl('Printed battery sleeve',(0,0,8),7.25,43,'blue','X')
        cyl('Positive contact',(25.8,0,8),2.4,1.5,'silver','X');cyl('Negative contact',(-25.1,0,8),5,.4,'silver','X')
        text('AA  1.5 V',(0,-2,15.3),4);text('+',(19,-2,15.3),4)
    elif slug=='battery-pack':
        box('Protected battery enclosure',(0,0,13),(66,38,26),'black',3);box('Battery label',(0,0,26.1),(48,28,.15),'blue',1)
        text('ROVER POWER',(0,4,26.3),3);text('RECHARGEABLE',(0,-3,26.3),2)
        for i,m in enumerate(['red','black']):wire('Power lead',[(33,-3+i*5,12),(48,-3+i*5,14),(45,20+i*3,9)],m,.85)
        box('Power connector',(45,24,9),(12,9,7),'yellow',1)
    elif slug=='usb-cable':
        wire('USB flexible cable',[(-40,-12,4),(-15,-24,4),(20,-10,4),(28,25,4),(0,32,4),(-20,15,4)],'black',1.6)
        box('USB A moulded grip',(-44,-12,4),(16,12,7),'black',1);box('USB A metal shell',(-57,-12,4),(12,12,5),'silver',.4)
        box('USB contact tongue',(-63.1,-12,4),(.2,8,2),'white',.1)
        for y in [-15,-13,-11,-9]:box('USB contact',(-63.3,y,4.9),(.2,1,.3),'gold',0)
        box('USB B grip',(-22,15,4),(12,12,9),'black',1);box('USB B metal shell',(-32,15,4),(8,9,8),'silver',1)
    elif slug=='resistor':
        cyl('Resistor body',(0,0,3),1.8,7,'resistorBlue','X')
        for x,m in [(-2,'orange'),(-.5,'orange'),(1,'black'),(2.8,'gold')]:cyl('Resistance colour band',(x,0,3),1.84,.55,m,'X')
        for side in [-1,1]:wire('Tinned resistor lead',[(side*3.5,0,3),(side*9,0,3),(side*12,0,0)],'silver',.28)
    elif slug=='slide-switch':
        box('Switch housing',(0,0,5),(16,8,8),'silver',.7);box('Slider opening',(0,0,9.1),(12,4,.2),'black',.2)
        slider=box('Moving switch slider',(-4,0,11),(4,3,4),'black',.4);slider['interaction']='Slide along X to open or close'
        for x in [-5,0,5]:box('Switch contact',(x,0,-1),(1,.6,5),'silver',.1)
        for x in [-10,10]:box('Mounting tab',(x,0,5),(5,8,1),'silver');hole((x,0,5.6),1)
        text('ON',(4,-3,9.2),1.5,'black')
    elif slug in ['nano-controller','esp32']:
        w,h=(45,18) if slug=='nano-controller' else (52,28)
        pcb(w,h,'blue' if slug=='nano-controller' else 'greenPCB')
        for y in [-h/2+1.5,h/2-1.5]:header((-w/2+5,y,0),15 if slug=='nano-controller' else 19)
        box('USB port',(-w/2+4,0,4),(9,8,5),'silver',.4);box('USB aperture',(-w/2-.55,0,4),(.1,6,3),'black',.2)
        if slug=='nano-controller':chip((0,0,3),(8,8,2),8);smd((9,-3,2.2),4);text('NANO',(10,4,2),2)
        else:
            box('RF shield',(4,0,4),(19,16,4),'silver',.4);text('ESP32',(4,-1,6.1),3,'black')
            for i in range(4):box('Antenna track',(18+i*1.2,(-1)**i*3,2),(1,9,.1),'gold',0)
    elif slug=='microbit':
        pcb(52,42,'black')
        for x in [-10,-5,0,5,10]:
            for y in [-6,-1,4,9,14]:box('Matrix LED',(x,y,2.5),(2,2,1),'red',.2)
        for x in [-20,20]:box('Button metal frame',(x,3,3),(7,7,2),'silver',.3);cyl('Button cap',(x,3,5),2,2,'black');text('A' if x<0 else 'B',(x,-5,2),2)
        for i,x in enumerate([-20,-10,0,10,20]):ring_mesh('Gold edge pad',(x,-16,2),3.8,2, .3,'gold');text(['0','1','2','3V','GND'][i],(x,-11,2),1.4)
    elif slug=='servo-driver':
        pcb(62,25,'pcbPurple');chip((0,0,3),(8,8,2),8)
        for i in range(16):
            for j,m in enumerate(['yellow','red','black']):
                box('Servo row insulator',(-27+i*3.5,-7+j*2.54,3),(3,2.5,2),m,.1);box('Servo header pin',(-27+i*3.5,-7+j*2.54,6),(.64,.64,5),'gold',.05)
            text(str(i),(-27+i*3.5,-11,2),1)
        terminals((-21,8,6),2);cyl('Power capacitor',(21,5,6),3.5,8,'black');text('PCA9685',(4,8,2),2)
    elif slug=='rgb-led':
        cyl('Clear LED flange',(0,0,21),3,1,'glass');cyl('Clear lens',(0,0,23),2.5,3,'glass');sphere('Domed lens',(0,0,24.5),(2.5,2.5,2.5),'glass')
        for i,m in enumerate(['red','green','blue']):box('Colour die',(-1+i,0,23),(.6,.6,.5),m,.1)
        for i in range(4):box('LED lead',(-1.9+i*1.27,0,10),( .45,.45,22 if i==1 else 19),'silver',.03)
    elif slug=='led-strip':
        box('Flexible circuit strip',(0,0,1),(95,10,1),'white',.3)
        for x in range(-40,41,16):
            box('RGB LED package',(x,0,2.2),(5,5,2),'white',.2);cyl('LED window',(x,0,3.3),1.8,.2,'glass')
            for dx,m in [(-.7,'red'),(0,'green'),(.7,'blue')]:box('LED die',(x+dx,0,3.5),(.4,.4,.1),m,0)
            box('SMD resistor',(x+6,0,1.7),(2,1,.7),'black',.1)
        for x in [-46,46]:
            for y in [-3,0,3]:box('Copper connection pad',(x,y,1.6),(2,2,.1),'gold',0)
    elif slug=='led-matrix':
        pcb(42,42,'greenPCB');box('Matrix enclosure',(0,0,5),(38,38,6),'black',1)
        for x in range(8):
            for y in range(8):cyl('LED pixel',(-15.75+x*4.5,-15.75+y*4.5,8.1),1.6,.5,'red',vertices=16)
        header((-7.62,-20,0),7)
    elif slug=='speaker':
        cyl('Speaker magnet',(0,0,4),12,7,'black');ring_mesh('Stamped steel rim',(0,0,9),23,19,3,'silver');torus('Rubber surround',(0,0,10),18,2,'rubber')
        bpy.ops.mesh.primitive_cone_add(vertices=48,radius1=7,radius2=18,depth=5,location=(0,0,7));move(bpy.context.object,'Paper diaphragm','black');sphere('Dust cap',(0,0,8),(7,7,3),'black')
        for x in [-8,8]:box('Speaker terminal',(x,23,3),(4,6,.6),'gold',.2)
    elif slug=='line-sensor':
        pcb(65,16,'black')
        for x in [-24,-12,0,12,24]:
            box('Reflectance sensor housing',(x,0,4),(8,10,4),'black',.5)
            for y,m in [(-2,'blue'),(2,'glass')]:sphere('Infrared optical lens',(x,y,6),(2,2,1.5),m)
        header((-8,-6,0),7);text('LINE ARRAY',(0,5,2),2)
    elif slug=='soil-probe':
        box('Capacitive probe PCB',(0,0,1),(16,74,1.6),'black',1)
        for x in [-4,4]:box('Moisture sensing electrode',(x,-8,1.85),(3,48,.08),'gold',.1)
        chip((0,22,3),(5,5,2),4);header((-2.54,31,2),3);text('SOIL',(0,11,1.9),2)
    elif slug=='rain-sensor':
        pcb(50,36,'black')
        for i in range(12):
            y=-14+i*2.5;box('Interleaved rain electrode',(0,y,1.9),(40,1,.15),'silver',0)
            box('Comb connection',(-20 if i%2 else 20,y,1.9),(1,3,.15),'silver',0)
        header((-1.27,16,2),2)
    elif slug in ['touch-sensor','tilt-sensor','hall-sensor','sound-sensor','colour-sensor','imu-sensor']:
        label={'touch-sensor':'TOUCH','tilt-sensor':'TILT','hall-sensor':'HALL','sound-sensor':'SOUND','colour-sensor':'COLOUR','imu-sensor':'IMU'}[slug]
        module(28,22,label,4 if slug in ['colour-sensor','imu-sensor'] else 3)
        if slug=='touch-sensor':cyl('Copper touch electrode',(5,0,2),6,.2,'gold');text('TOUCH',(5,-1,2.2),1.8,'black')
        elif slug=='tilt-sensor':cyl('Tilt switch can',(5,0,6),3,12,'silver','Y');wire('Switch lead',[(5,-6,6),(5,-8,2)],'silver',.3)
        elif slug=='hall-sensor':box('Hall sensing package',(6,0,6),(4,2,5),'black',.4);header((3.46,0,0),3)
        elif slug=='sound-sensor':cyl('Electret microphone',(5,0,6),5,8,'silver');cyl('Microphone mesh',(5,0,10.1),4,.1,'black');
        elif slug=='colour-sensor':
            box('Colour sensor',(4,0,3),(5,5,2),'black',.2);box('Optical window',(4,0,4.1),(2,2,.1),'glass',.1)
            for x in [-1,9]:box('Illumination LED',(x,0,3),(2,3,2),'white',.2)
        else:chip((4,0,3),(4,4,1.5),4);text('X >',(5,-6,2),1.4)
    elif slug=='rotary-encoder':
        module(28,22,'ENCODER',5);box('Encoder body',(4,0,5),(12,12,7),'silver',.6);cyl('Rotating shaft',(4,0,15),3,15,'silver');cyl('Knurled knob',(4,0,24),8,9,'black')
        for i in range(24):a=i*math.tau/24;cyl('Knob grip rib',(4+7.8*math.cos(a),7.8*math.sin(a),24),.45,8,'black',vertices=8)
    elif slug=='large-servo':
        box('Servo body',(0,0,22),(40,20,38),'black',1.5);box('Mounting flange',(0,0,32),(54,20,3),'black',.5)
        for x in [-24,24]:
            for y in [-6,6]:hole((x,y,33.6),1.6)
        cyl('Output boss',(10,0,43),6,5,'black');cyl('Metal spline',(10,0,47),2.8,5,'brass');box('Servo horn',(10,0,50),(35,6,3),'aluminium',2)
        screw((10,0,52));text('METAL GEAR',(0,-10.1,18),3,'gold',(math.pi/2,0,0))
        for i,m in enumerate(['orange','red','black']):wire('Servo lead',[(-20,i*1.4,7),(-32,i*1.4,7),(-36,15+i*1.4,9)],m,.5)
    elif slug=='water-pump':
        cyl('Motor shell',(-10,0,15),12,28,'silver','X');cyl('Pump head',(10,0,15),15,18,'white','X');cyl('Outlet tube',(12,15,15),3,15,'white','Y');cyl('Inlet tube',(23,0,15),3,12,'white','X')
        box('Pump foot',(0,0,2),(45,25,4),'black',1)
        for i,m in enumerate(['red','black']):wire('Motor lead',[(-25,0,10+i*6),(-33,0,10+i*6),(-35,15,8+i*3)],m,.5)
    elif slug=='fan':
        plate('Fan square frame',(0,0,8),(50,50,12),[(0,0,21),(-21,-21,2),(21,-21,2),(-21,21,2),(21,21,2)],'black')
        cyl('Fan motor hub',(0,0,8),7,9,'black')
        for i in range(7):
            a=i*math.tau/7;o=box('Fan blade',(12*math.cos(a),12*math.sin(a),8),(16,7,1.4),'black',2);o.rotation_euler=(.3,0,a+.5)
        for a in [0,math.pi/2,math.pi,math.pi*1.5]:bar('Rear support',(0,0,2),(22*math.cos(a),22*math.sin(a),2),2,2,'black')
    elif slug=='caster':
        plate('Caster mounting plate',(0,0,23),(30,24,3),[(-11,-8,2),(11,-8,2),(-11,8,2),(11,8,2)])
        cyl('Ball cup',(0,0,17),11,10,'silver');sphere('Rolling steel ball',(0,0,9),(9,9,9),'silver')
    elif slug=='robot-tracks':
        for x in [-35,35]:cyl('Track roller',(x,0,18),17,20,'black','Y');cyl('Roller hub',(x,-11,18),6,2,'silver','Y')
        for top in [0,1]:
            for x in range(-35,36,7):box('Rubber tread',(x,0,37 if top else 0),(6.5,25,4),'rubber',.6)
        for side in [-1,1]:
            for i in range(1,9):
                a=-math.pi/2+i*math.pi/9;o=box('Curved end tread',(side*(35+18*math.cos(a)),0,18+18*math.sin(a)),(6.5,25,4),'rubber',.5);o.rotation_euler[1]=-side*a
        box('Track side support',(0,0,18),(70,8,8),'aluminium')
    elif slug=='chassis':
        holes=[(x,y,2) for x in [-55,-35,0,35,55] for y in [-30,30]]+[(x,y,1.6) for x in [-15,15] for y in [-15,15]]
        plate('Aluminium rover chassis',(0,0,3),(140,85,3),holes)
        for x in [-50,50]:box('Raised chassis edge',(x,0,9),(3,85,12),'aluminium',.5)
        text('ROBO SPARKS',(0,0,4.6),7,'black')
    elif slug=='bracket':
        plate('Bracket foot',(0,0,2),(36,28,3),[(-12,0,2),(12,0,2)])
        o=plate('Bracket upright',(0,0,0),(36,32,3),[(0,0,6),(-12,8,2),(12,8,2)]);o.rotation_euler[0]=math.pi/2;o.location=(0,12,17)
    elif slug=='beam':plate('Perforated aluminium beam',(0,0,3),(100,15,5),[(x,0,2.5) for x in range(-40,41,10)])
    elif slug=='axle':cyl('Steel axle',(0,0,3),3,80,'silver','X');cyl('Axle collar',(-27,0,3),5,7,'aluminium','X');box('Collar grub screw',(-27,0,8),(3,3,2),'black',.4)
    elif slug=='bearing':
        ring_mesh('Outer bearing race',(0,0,5),11,8,7);ring_mesh('Inner bearing race',(0,0,5),6,4,7)
        for i in range(10):a=i*math.tau/10;sphere('Bearing ball',(7*math.cos(a),7*math.sin(a),5),(1.5,1.5,1.5),'silver')
        ring_mesh('Bearing dust seal',(0,0,8.6),10,4.2,.4,'black')
    elif slug=='fastener-set':
        cyl('M3 screw shank',(-12,0,7),1.5,12,'silver');cyl('Socket screw head',(-12,0,14),3,3,'silver');cyl('Hex socket',(-12,0,15.6),1.4,.1,'black',vertices=6)
        for i in range(15):torus('Thread crest',(-12,0,1+i*.7),1.5,.16)
        ring_mesh('M3 nut',(0,0,3),3.2,1.5,2.5,'silver',6);ring_mesh('Brass spacer',(12,0,8),3,1.6,14,'brass',6)
        ring_mesh('Washer',(0,10,1),3.5,1.6,.8)
    elif slug=='spur-gear':
        ring_mesh('Gear web',(0,0,5),20,3,6,'white');ring_mesh('Gear hub',(0,0,9),7,3,12,'white')
        for i in range(24):a=i*math.tau/24;o=box('Gear tooth',(21*math.cos(a),21*math.sin(a),5),(4.2,3.8,6),'white',.3);o.rotation_euler[2]=a
    elif slug=='pulley':
        ring_mesh('Pulley core',(0,0,7),14,3,10);ring_mesh('Lower pulley flange',(0,0,2),18,3,2);ring_mesh('Upper pulley flange',(0,0,12),18,3,2)
    elif slug=='drive-belt':
        pts=[]
        for i in range(81):a=i*math.tau/80;pts.append((38*math.cos(a),19*math.sin(a),3))
        wire('Continuous rubber belt',pts,'rubber',2)
        for i in range(48):a=i*math.tau/48;o=box('Inner belt tooth',(35.5*math.cos(a),16.5*math.sin(a),3),(3,2,4),'rubber',.2);o.rotation_euler[2]=a
    elif slug=='gripper':
        plate('Gripper base',(0,-20,5),(48,35,4),[(-17,-20,2),(17,-20,2)])
        for side in [-1,1]:
            bar('Moving finger',(side*12,-10,8),(side*30,20,8),8,4,'aluminium');bar('Parallel linkage',(side*6,-9,8),(side*24,21,8),3,4,'aluminium')
            box('Rubber gripping pad',(side*25,30,8),(7,20,10),'rubber',1)
            for x,y in [(side*12,-10),(side*30,20)]:screw((x,y,11),2)
        box('Servo mount',(0,-23,14),(25,15,14),'black',1)
    elif slug=='arm-link':
        plate('Arm link',(0,0,5),(90,18,6),[(-35,0,4),(35,0,4)])
        for x in [-35,35]:ring_mesh('Joint boss',(x,0,7),11,4,8,'aluminium')
    elif slug=='hinge':
        for side in [-1,1]:plate('Hinge leaf',(side*12,0,2),(20,30,2),[(side*14,-9,2),(side*14,9,2)])
        for i in range(5):cyl('Hinge knuckle',(0,-12+i*6,4),3,5.8,'silver','Y')
        cyl('Hinge pin',(0,0,4),1.2,34,'silver','Y')
    elif slug=='rack-pinion':
        box('Linear rack',(0,0,3),(95,10,5),'white',.3)
        for x in range(-44,45,4):box('Rack tooth',(x,6,5),(2,4,4),'white',.2)
        ring_mesh('Pinion',(0,19,6),9,2,7,'white')
        for i in range(14):a=i*math.tau/14;o=box('Pinion tooth',(10*math.cos(a),19+10*math.sin(a),6),(3,2.6,7),'white',.2);o.rotation_euler[2]=a
    elif slug=='lifting-platform':
        plate('Lift base',(0,0,3),(85,55,4),[(-35,-20,2),(35,-20,2),(-35,20,2),(35,20,2)])
        plate('Lift platform',(0,0,57),(85,55,4))
        for y in [-18,18]:
            for a,b in [((-32,y,7),(32,y,53)),((32,y,7),(-32,y,53))]:bar('Scissor arm',a,b,6,3)
            cyl('Central pivot',(0,y,30),3,6,'brass','Y');cyl('Roller',(32,y,52),4,7,'black','Y')
        cyl('Lead screw',(0,0,8),2,65,'silver','X')
    elif slug=='oled-display':display((0,0,2),'HELLO!',36,30);header((-3.81,13,0),4)
    elif slug=='seven-segment':
        box('Display housing',(0,0,7),(26,38,12),'black',1)
        for y in [-12,0,12]:box('Horizontal LED segment',(-2,y,13.1),(13,3,.3),'red',1)
        for x in [-10,6]:
            for y in [-6,6]:box('Vertical LED segment',(x,y,13.1),(3,10,.3),'red',1)
        cyl('Decimal point',(10,-12,13.2),1.5,.2,'red');
        for x in [-10,-5,0,5,10]:
            for y in [-16,16]:box('Display pin',(x,y,-2),(.6,.6,8),'silver',.05)
    elif slug=='joystick':
        module(35,30,'JOYSTICK',5);box('Joystick gimbal',(0,0,8),(18,18,12),'silver',1);cyl('Joystick stalk',(0,0,19),3,14,'black');sphere('Thumb cap',(0,0,26),(12,12,5),'rubber');torus('Thumb cap ridge',(0,0,29),7,.8,'black')
    elif slug=='keypad':
        box('Keypad body',(0,0,3),(62,62,5),'black',2)
        chars=['1','2','3','A','4','5','6','B','7','8','9','C','*','0','#','D']
        for i,ch in enumerate(chars):
            x=-22.5+(i%4)*15;y=22.5-(i//4)*15;box('Key '+ch,(x,y,6),(12,12,3),'blue' if i%4==3 else 'white',2);text(ch,(x,y-2,7.6),5,'white' if i%4==3 else 'black')
        box('Ribbon cable',(0,39,1),(18,22,.5),'orange',.2);header((-8.89,48,0),8)
    elif slug=='remote-control':
        box('Remote enclosure',(0,0,7),(38,88,12),'black',4);sphere('IR emitter',(0,44,8),(3,3,2),'glass')
        for i in range(15):
            x=-11+(i%3)*11;y=25-(i//3)*12;cyl('Remote button',(x,y,13.5),3.8,2,'red' if i==0 else 'white');text(str(i) if i else 'O',(x,y-1.2,14.6),2.5,'black')
        text('ROBO',(0,-34,13.2),4)
    elif slug=='water-tubing':
        pts=[(-40,-10,4),(-25,-25,4),(5,-23,4),(30,-5,4),(20,20,4),(-10,20,4),(-15,4,4),(5,0,4)]
        wire('Silicone tube',pts,'silicone',3)
        for p in [pts[0],pts[-1]]:cyl('Tube opening',p,1.6,.1,'black')
    elif slug=='conveyor':
        for y in [-28,28]:box('Conveyor side frame',(0,y,18),(125,4,12),'aluminium',.6)
        for x in [-54,54]:cyl('Belt roller',(x,0,18),10,55,'silver','Y')
        box('Top conveyor belt',(0,0,28),(108,52,2),'rubber',.5);box('Bottom conveyor belt',(0,0,8),(108,52,2),'rubber',.5)
        for x in range(-48,49,8):box('Belt surface rib',(x,0,29.1),(1,52,.4),'black',.1)
        for x in [-45,45]:
            for y in [-25,25]:box('Support leg',(x,y,8),(5,5,16),'aluminium');box('Rubber foot',(x,y,1),(12,12,2),'rubber')
        cyl('Drive motor',(54,40,18),9,20,'silver','Y')
    elif slug=='pen-holder':
        plate('Pen carriage',(0,0,3),(35,30,4),[(-12,-9,2),(12,-9,2)])
        ring_mesh('Pen clamp',(0,0,17),10,5,20,'blue');box('Clamp tightening screw',(12,0,17),(8,3,3),'silver',.4)
        cyl('Pen barrel',(0,0,31),4,42,'yellow');bpy.ops.mesh.primitive_cone_add(vertices=24,radius1=.4,radius2=4,depth=10,location=(0,0,5));move(bpy.context.object,'Pen tip','silver')

def view(scene):
    bpy.context.window.scene=scene
    for screen in bpy.data.screens:
        for area in screen.areas:
            if area.type=='VIEW_3D':
                sp=area.spaces.active;sp.region_3d.view_perspective='CAMERA';sp.clip_start=.1;sp.clip_end=10000;sp.overlay.show_overlays=False
                sp.shading.type='SOLID';sp.shading.color_type='MATERIAL';sp.shading.light='STUDIO';sp.shading.show_shadows=True;sp.shading.show_cavity=True
                area.tag_redraw()

def make_asset(spec):
    global C
    slug,name,category,span,lesson=spec
    s=studio('KIT • '+category+' • '+name,span*1.5)
    C=bpy.data.collections.new('PART • '+slug);s.collection.children.link(C)
    build(slug)
    C.asset_mark();C.asset_data.description=name+'. '+lesson;C['part_id']=slug;C['category']=category;C['lesson']=lesson;C['accuracy']='Representative educational model; approximate dimensions'
    for o in C.objects:o['part_id']=slug
    LIB[slug]=C
    # Fit the camera to the true geometry, including long leads.
    bpy.context.view_layer.update()
    pts=[o.matrix_world @ Vector(corner) for o in C.objects for corner in o.bound_box]
    if pts:
        lo=Vector(tuple(min(p[i] for p in pts) for i in range(3)));hi=Vector(tuple(max(p[i] for p in pts) for i in range(3)));center=(lo+hi)/2
        radius=max(hi-lo)*1.5;s.camera.location=center+Vector((radius*.7,-radius,radius*.9));s.camera.rotation_euler=(center-s.camera.location).to_track_quat('-Z','Y').to_euler();s.camera.data.ortho_scale=radius
    s['component_id']=slug;s['category']=category
    bpy.data.libraries.write(str(OUT/'components'/f'{slug}.blend'),{s,C},fake_user=True)
    entry={'id':slug,'name':name,'category':category,'lesson':lesson,'objects':len(C.objects),'blend':f'components/{slug}.blend','reference':CATALOG['references'].get(slug),'accuracy':'Representative proportions'}
    CATALOG['components'].append(entry);view(s)

index=0

def finish():
    global C
    s=studio('START HERE • 70 robotics parts',1500)
    C=bpy.data.collections.new('Kit overview');s.collection.children.link(C)
    entries=CATALOG['components']
    for i,e in enumerate(entries):
        x=(i%10-4.5)*150;y=(3-i//10)*150
        instance(e['id'],(x,y,0));text(f'{i+1:02d} '+e['name'],(x,y-57,0),5,'black')
    s.camera.location=(550,-1600,1700);s.camera.rotation_euler=(Vector((0,0,0))-s.camera.location).to_track_quat('-Z','Y').to_euler();s.camera.data.ortho_scale=1800
    s.render.resolution_x=2000;s.render.resolution_y=1500
    view(s)
    (OUT/'manifest.json').write_text(json.dumps(CATALOG,indent=2))
    bpy.ops.wm.save_as_mainfile(filepath=str(OUT/'robotics-kit.blend'))
    # Add browsing scenes, repair beam bores and fit all cameras before completion.
    for helper in ['add_browse_scenes.py','fix_framing.py']:
        path=OUT/helper
        exec(compile(path.read_text(),str(path),'exec'),{'__file__':str(path),'__name__':'__main__'})
    (OUT/'build-complete.json').write_text(json.dumps({'total_parts':len(entries),'new_parts':len(SPECS),'existing_parts':len(entries)-len(SPECS),'saved':True},indent=2))
    print('KIT COMPLETE: '+str(len(entries))+' reusable parts',flush=True)

def tick():
    global index
    try:
        if index>=len(SPECS):finish();return None
        spec=SPECS[index];make_asset(spec);index+=1
        (OUT/'progress.json').write_text(json.dumps({'step':index,'total':len(SPECS),'name':spec[1]}))
        print(f'BUILD {index}/{len(SPECS)}: {spec[1]}',flush=True)
        return 1.5
    except Exception:
        (OUT/'build-error.txt').write_text(traceback.format_exc());traceback.print_exc();return None
if bpy.app.background:
    while index<len(SPECS):
        if tick() is None:raise RuntimeError('Kit build failed')
    finish()
else:bpy.app.timers.register(tick,first_interval=1)
