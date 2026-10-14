"""Native editable Blender geometry; no image planes used as substitute models.
Run: blender --python build_library.py (staged live build), or -b --python ...
"""
import bpy, math, json, re, os, time
from pathlib import Path
from mathutils import Vector
ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/'models/robotics-library'
for p in ['components','projects','previews']: (OUT/p).mkdir(parents=True,exist_ok=True)
PROJECTS=json.loads(re.search(r'export const projects = (\[.*\])', (ROOT/'pages/home/projects.js').read_text(), re.S).group(1))
NAMES=['Ultrasonic distance sensor','Servo actuator','Geared DC motor','Microcontroller board','Breadboard','Motor driver','PIR motion sensor','Temperature and humidity sensor','Light sensor','Piezo buzzer','Stepper motor','Battery holder','LED','Potentiometer','Push button','Jumper wires','Robot wheel','Relay module','Infrared sensor','Linear actuator']
IDS=['ultrasonic-sensor','servo-actuator','geared-motor','microcontroller','breadboard','motor-driver','motion-sensor','temperature-sensor','light-sensor','buzzer','stepper-motor','battery-holder','led','potentiometer','push-button','jumper-wires','robot-wheel','relay','infrared-sensor','linear-actuator']
# These nominal visual dimensions are editable assumptions, not manufacturer CAD.
DIMENSIONS=[(45,20,15),(23,12,32),(70,23,22),(68.6,53.4,15),(85,55,10),(43,43,30),(32,24,28),(30,16,18),(32,14,17),(22,22,15),(42,42,45),(60,32,17),(5,5,27),(16,16,30),(25,20,14),(65,65,20),(65,26,65),(50,26,20),(32,14,14),(130,30,30)]
M={}; C=None

def mat(name,color,metal=0,rough=.4,trans=0,emit=0):
 m=bpy.data.materials.new(name);m.diffuse_color=(*color,1);m.use_nodes=True
 p=m.node_tree.nodes.get('Principled BSDF');p.inputs['Base Color'].default_value=(*color,1);p.inputs['Metallic'].default_value=metal;p.inputs['Roughness'].default_value=rough
 p.inputs['Transmission'].default_value=trans
 if emit:p.inputs['Emission'].default_value=(*color,1);p.inputs['Emission Strength'].default_value=emit
 M[name]=m;return m
MATERIAL_SPECS=[('blue',(.015,.17,.42)),('redPCB',(.56,.025,.025)),('greenPCB',(.025,.23,.12)),('black',(.012,.016,.024)),('rubber',(.022,.026,.032),0,.82),('silver',(.64,.69,.74),.85,.24),('gold',(.78,.53,.17),.8,.28),('white',(.88,.9,.92)),('yellow',(.98,.65,.012)),('red',(.72,.012,.022)),('green',(.01,.5,.13)),('cyan',(.01,.48,.85)),('orange',(.94,.24,.015)),('purple',(.39,.03,.7)),('wood',(.5,.28,.12),0,.65),('ceramic',(.62,.38,.22)),('soil',(.06,.025,.009),0,.95),('leaf',(.04,.25,.018),0,.55),('glass',(.8,.92,1),0,.16,.6),('servoBlue',(.015,.12,.6),0,.2,.25),('screen',(.006,.012,.027),0,.24),('light',(.95,.82,.42),0,.3,0,2)]

def move(o,name,material):
 o.name=name
 for c in list(o.users_collection):c.objects.unlink(o)
 C.objects.link(o)
 if material:o.data.materials.append(M[material] if isinstance(material,str) else material)
 return o

def box(name,p,d,m='black',edge=.25):
 bpy.ops.mesh.primitive_cube_add(size=1,location=p);o=move(bpy.context.object,name,m);o.scale=d;bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
 if edge:
  mod=o.modifiers.new('Manufactured edge radius','BEVEL');mod.width=edge;mod.segments=2;o.data.use_auto_smooth=True;o.modifiers.new('Weighted corner normals','WEIGHTED_NORMAL')
 return o

def cyl(name,p,r,h,m='silver',axis='Z',vertices=32):
 bpy.ops.mesh.primitive_cylinder_add(vertices=vertices,radius=r,depth=h,location=p);o=move(bpy.context.object,name,m)
 o.rotation_euler=Vector({'X':(1,0,0),'Y':(0,1,0),'Z':(0,0,1)}[axis]).to_track_quat('Z','Y').to_euler()
 for f in o.data.polygons:f.use_smooth=True
 return o

def sphere(name,p,s,m='white',segments=24):
 bpy.ops.mesh.primitive_uv_sphere_add(segments=segments,ring_count=12,location=p);o=move(bpy.context.object,name,m);o.scale=s
 for f in o.data.polygons:f.use_smooth=True
 return o

def torus(name,p,r,t,m='silver',axis='Z'):
 bpy.ops.mesh.primitive_torus_add(major_radius=r,minor_radius=t,major_segments=32,minor_segments=8,location=p);o=move(bpy.context.object,name,m);o.rotation_euler=Vector({'X':(1,0,0),'Y':(0,1,0),'Z':(0,0,1)}[axis]).to_track_quat('Z','Y').to_euler();return o

def wire(name,points,m='red',r=.6):
 data=bpy.data.curves.new(name,'CURVE');data.dimensions='3D';data.resolution_u=12;data.bevel_depth=r;data.bevel_resolution=2
 sp=data.splines.new('BEZIER');sp.bezier_points.add(len(points)-1)
 for b,p in zip(sp.bezier_points,points):b.co=p;b.handle_left_type='AUTO';b.handle_right_type='AUTO'
 o=bpy.data.objects.new(name,data);C.objects.link(o);o.data.materials.append(M[m]);return o

def text(body,p,size=3,m='white',rot=None):
 d=bpy.data.curves.new(body,'FONT');d.body=body;d.size=size;d.align_x='CENTER';d.extrude=.005;o=bpy.data.objects.new('Marking • '+body,d);C.objects.link(o);o.location=p;o.data.materials.append(M[m]);
 if rot:o.rotation_euler=rot
 return o

def screw(p,r=1.4,axis='Z'):
 cyl('Steel screw head',p,r,.7,'silver',axis)
 if axis=='Z':box('Screw slot',(p[0],p[1],p[2]+.37),(r*1.4,.25,.05),'black',0)

def ring(p,r=1.6):
 torus('Plated mounting hole',p,r,.35,'gold');cyl('Mounting bore',p,r-.4,.12,'black')

def header(p,n,axis='X',female=False):
 x,y,z=p
 for i in range(n):
  a=x+(i*2.54 if axis=='X' else 0);b=y+(i*2.54 if axis=='Y' else 0)
  box('Header insulator',(a,b,z+1.2),(2.5,2.5,2.4),'black',.1)
  if female:box('Female socket recess',(a,b,z+2.42),(1.1,1.1,.08),'silver',.05);box('Socket aperture',(a,b,z+2.48),(.7,.7,.08),'black',0)
  else:box('Square gold pin',(a,b,z+4),(.64,.64,7),'gold',.05)

def smd(p,n=8):
 for i in range(n):
  x=p[0]+(i%4)*4;y=p[1]+(i//4)*4;z=p[2]
  box('SMD resistor',(x,y,z),(2,1,.6),'black',.08)
  for dx in [-1.1,1.1]:box('Solder termination',(x+dx,y,z),(.55,1.1,.65),'silver',.04)

def pcb(w,h,m='blue'):
 box('FR4 board',(0,0,1),(w,h,1.6),m,.6)
 for x in [-w/2+3,w/2-3]:
  for y in [-h/2+3,h/2-3]:ring((x,y,1.88))

def terminals(p,n):
 x,y,z=p
 box('Screw terminal block',(x+(n-1)*2.5,y,z),(n*5,7,9),'blue',.3)
 for i in range(n):screw((x+i*5,y,z+4.6),1.6);box('Wire entry',(x+i*5,y-3.55,z),(3,.15,3),'black',.1)

def component(k):
 if k==0:
  pcb(45,20);text('HC-SR04',(0,-8,1.9),2.4)
  for x in [-13,13]:
   cyl('Transducer aluminium can',(x,0,8),8,12);cyl('Dark acoustic mesh',(x,0,14.03),6.8,.2,'black');torus('Rolled transducer lip',(x,0,14.3),7.3,.55)
   for j in range(-7,8):
    q=j*.8;reach=math.sqrt(6.3**2-q*q)
    wire('Mesh cross strand',[(x-reach,q,14.2),(x+reach,q,14.2)],'silver',.055);wire('Mesh cross strand',[(x+q,-reach,14.22),(x+q,reach,14.22)],'silver',.055)
  header((-3.81,-9,0),4);box('Quartz crystal',(0,5,3),(8,3,2),'silver',1);smd((-5,-4,2.2),4)
 elif k==1:
  box('SG90 servo body',(0,0,14),(23,12,25),'servoBlue',1);box('Mounting ears',(0,0,23),(32,12,2),'servoBlue',.4)
  for x in [-14,14]:ring((x,0,24.1),1.5)
  cyl('Gear housing',(5,0,28),5.5,5,'servoBlue');cyl('Output spline',(5,0,31),2.4,3,'white');box('Double arm servo horn',(5,0,33),(30,5,2),'white',2)
  screw((5,0,34.2))
  for x in [-7,-3,13,17]:cyl('Horn adjustment hole',(x,0,34.1),.6,.1,'black',vertices=12)
  text('SG90',(0,-6.05,13),3,'white',(math.pi/2,0,0))
  for i,m in enumerate(['orange','red','black']):wire('Servo cable',[(10,0,5),(23,i,5),(28,i,16),(18,i,20)],m,.45)
 elif k==2:
  box('TT gearbox',(7,0,12),(38,23,22),'yellow',2);cyl('DC motor steel shell',(-22,0,12),10,24,'silver','X');cyl('Motor end cap',(-35,0,12),9,3,'black','X');cyl('Gear output shaft',(15,-16,12),2.7,12,'white','Y')
  for x in [-4,22]:screw((x,-11.7,12),1.5,'Y')
  for z in [7,17]:box('Motor terminal',(-35,0,z),(4,5,.5),'gold',.1)
 elif k==3:
  pcb(68.6,53.4);box('ATmega328P DIP',(6,-8,4.5),(34,8,5),'black',.5)
  for j in range(14):
   for y in [-13,-3]:box('DIP leg',(-10+j*2.54,y,3),(1,3,1),'silver',.1)
  for y,n,x in [(23,8,-18),(23,10,5),(-23,8,-18),(-23,6,5)]:header((x,y,2),n,female=True)
  box('USB-B socket',(-27,13,7),(13,15,11),'silver',1);box('USB opening',(-33.6,13,7),(.1,10,7),'black',.3);box('USB inner tongue',(-33.7,13,6),(.15,7,3),'white',.2)
  box('DC jack',(-27,-17,7),(13,10,10),'black',1);cyl('DC jack aperture',(-33.6,-17,7),3,.1,'silver','X');cyl('Jack inner bore',(-33.7,-17,7),2.3,.1,'black','X')
  for x in [-17,-10]:cyl('Electrolytic capacitor',(x,-15,5),2.7,6);box('Capacitor vent',(x,-15,8.1),(3,.2,.1),'black',0)
  box('USB interface IC',(-13,9,3.2),(7,7,2),'black',.2);smd((-8,3,2.2),12);box('Reset switch',(-25,23,4),(5,4,3),'silver');cyl('Reset button',(-25,23,6),1.3,1,'red')
  text('UNO',(20,10,1.9),6);text('ARDUINO',(10,17,1.9),3);text('DIGITAL (PWM~)',(9,20,1.9),1.5);text('ANALOG IN',(12,-20,1.9),1.5)
  for i in range(14):text(str(i),(-19+i*3.5,18,1.91),1)
  for x in [-3,2]:box('Status LED',(x,10,2.6),(2,1,1),'yellow')
 elif k==4:
  box('Breadboard housing',(0,0,5),(85,55,10),'white',2);box('Central separation channel',(0,0,10.02),(76,3,.2),'black',.2)
  # Socket recesses modeled individually with dark openings and molded rims.
  for i in range(30):
   x=-36.83+i*2.54
   for y in [-17.8,-15.24,-12.7,-10.16,-7.62,7.62,10.16,12.7,15.24,17.8,-23,23]:box('Contact socket',(x,y,10.1),(1.15,1.15,.18),'black',.18)
  for y,m in [(-25,'blue'),(-20.5,'red'),(20.5,'blue'),(25,'red')]:box('Power rail stripe',(0,y,10.15),(77,.4,.08),m,0)
  for i in range(0,30,5):text(str(i+1),(-36.83+i*2.54,3.2,10.2),1.6,'black')
 elif k==5:
  pcb(43,43,'redPCB');box('L298N package',(0,3,11),(22,5,18),'black');box('Aluminium heat sink',(0,8,17),(25,12,25),'black')
  for x in range(-10,11,4):box('Heat sink fin',(x,8,20),(1,15,24),'black',.2)
  for x in [-12,12]:cyl('Filter capacitor',(x,-3,8),4,12);box('Capacitor vent',(x,-3,14.1),(4,.4,.1),'black',0)
  terminals((-5,-17,6),3);terminals((-17,10,6),2);terminals((12,10,6),2);header((-6,-8,2),6);smd((-15,-12,2.3),4);text('L298N',(0,18,2),2)
 elif k==6:
  pcb(32,24,'greenPCB');box('Fresnel lens square foot',(0,0,5),(24,24,5),'white',1)
  # A faceted hemispherical Fresnel lens matches the reference module silhouette.
  o=sphere('Faceted PIR Fresnel dome',(0,0,7),(12,12,17),'white',16)
  for f in o.data.polygons:f.use_smooth=False
  header((-2.54,-10,-5),3);text('PIR',(0,10,2),2)
 elif k==7:
  pcb(30,16);box('DHT11 sensor core',(2,0,9),(15,12,14),'blue',.8)
  for x in [-3,1,5,9]:
   for y in [-4,0,4]:box('Vent aperture',(x,y,16.1),(2.4,2.1,.15),'black',.2)
  for x in [-3,1,5,9]:box('Side vent',(x,-6.1,11),(2.3,.1,7),'black',.15)
  header((-12,-2.54,2),3,'Y');text('DHT11',(-4,6.4,2),1.8);smd((-9,3,2.3),2)
 elif k==8:
  pcb(32,14);cyl('CdS photoresistor',(7,0,12),4.5,2,'ceramic')
  for i in range(5):wire('Photoresistive serpentine',[ (4+i*1.2,-2.8,13.1),(4+i*1.2,2.8,13.1)],'silver',.2)
  for x in [5,9]:wire('LDR leg',[(x,0,11),(x,0,.3)],'silver',.3);cyl('LDR solder joint',(x,0,1.9),.9,.6,'silver')
  header((-13,-2.54,2),3,'Y');box('Comparator',(-4,0,3.2),(6,4,2),'black');smd((-8,4,2.2),2)
 elif k==9:
  cyl('Piezo enclosure',(0,0,8),11,14,'black');cyl('Sound port',(0,0,15.05),2,.15,'screen');text('+',(6,0,15.2),3)
  for x in [-7,7]:cyl('Solder lead',(x,0,-2),.5,7)
  for x in [-12,12]:box('Mounting tab',(x,0,2),(6,7,3),'black',2);ring((x,0,3.6),1.3)
 elif k==10:
  box('NEMA17 stator',(0,0,23),(42,42,30),'black',2);box('Front aluminium plate',(0,0,40),(42,42,5),'silver',2);box('Rear aluminium plate',(0,0,5),(42,42,5),'silver',2)
  for z in range(10,37,2):box('Lamination edge',(0,-21.05,z),(36,.2,.3),'silver',0)
  cyl('Motor register',(0,0,43),11,2);cyl('5mm output shaft',(0,0,54),2.5,22)
  for x in [-15.5,15.5]:
   for y in [-15.5,15.5]:screw((x,y,42.6),1.5)
  box('Motor connector',(0,23,9),(12,6,7),'white');header((-3.81,23,12),4)
 elif k==11:
  box('Two-AA tray',(0,0,2),(60,32,3),'black',1)
  for y in [-16,0,16]:box('Tray wall',(0,y,7),(60,1.5,12),'black',.5)
  for x in [-30,30]:box('Tray end',(x,0,8),(2,32,14),'black',.8)
  for i,y in enumerate([-8,8]):
   cyl('AA cell',(0,y,9),6.6,49,'black','X');cyl('Positive brass jacket',(17 if i==0 else -17,y,9),6.65,15,'gold','X');cyl('Positive button',(25 if i==0 else -25,y,9),2.5,1,'silver','X')
   pts=[]
   for j in range(61):a=j/60*math.tau*4;pts.append((-28+j/60*3,y+3*math.cos(a),9+3*math.sin(a)))
   wire('Battery contact spring',pts,'silver',.28)
  for i,m in enumerate(['red','black']):wire('Battery lead',[(30,-7+i*3,5),(42,-5+i*3,5),(38,17+i*3,8)],m,.55)
 elif k==12:
  cyl('LED flange',(0,0,22),2.8,1.5,'red');cyl('LED lens barrel',(0,0,24),2.5,3,'red');sphere('LED domed lens',(0,0,25.5),(2.5,2.5,2.5),'red')
  for x,h in [(-1.27,21),(1.27,18)]:box('LED lead',(x,0,22-h/2),(.5,.5,h),'silver',.05)
  box('LED cathode anvil',(-1,0,24),(1.4,1.5,1.3),'silver')
 elif k==13:
  box('Potentiometer body',(0,0,7),(16,16,12),'blue',1);cyl('Threaded bushing',(0,0,15),4,5);cyl('Hex fixing nut',(0,0,15),6,2,'silver',vertices=6);cyl('Knurled shaft',(0,0,25),3,17)
  for i in range(16):a=i*math.tau/16;cyl('Shaft knurl',(3*math.cos(a),3*math.sin(a),26),.25,12)
  box('Shaft slot',(0,0,33.6),(5,.7,.1),'black',0)
  for x in [-5,0,5]:box('Solder lug',(x,-8,-1),(1.3,1,8),'silver',.1)
 elif k==14:
  pcb(25,20,'greenPCB');box('Switch housing',(0,0,5),(12,12,5),'black');cyl('Green button cap',(0,0,10),6,6,'green')
  for x in [-5,5]:
   for y in [-5,5]:screw((x,y,7.7),.7)
  header((-2.54,-8,2),3)
 elif k==15:
  for i,m in enumerate(['red','orange','yellow','green','cyan','blue','purple','white','black','red']):
   y=(i-4.5)*2.5;wire('Dupont insulated wire',[(-25,y,5),(-25,y+35,12),(20,y+35,15),(25,y,5)],m,.55)
   for x in [-25,25]:box('Female Dupont housing',(x,y-4,4),(2.5,9,2.5),'black',.15);box('Connector socket',(x,y-8.6,4),(1,.1,1),'silver',.1)
 elif k==16:
  # Wheel axle is along Y, with tyre, inset hub and five spokes.
  torus('Molded rubber tyre',(0,0,33),26,6.5,'rubber','Y');torus('Yellow rim',(0,-10,33),23,2,'yellow','Y');cyl('Hub',(0,0,33),6,25,'yellow','Y');cyl('Axle bore',(0,-12.6,33),2.7,.2,'black','Y')
  for i in range(5):
   a=i*math.tau/5;o=box('Wheel spoke',(13*math.sin(a),-9,33+13*math.cos(a)),(6,4,22),'yellow',1);o.rotation_euler[1]=a
  for i in range(40):
   a=i*math.tau/40
   for y in [-6,6]:
    o=box('Tyre tread lug',(31.7*math.sin(a),y,33+31.7*math.cos(a)),(5,10,2),'rubber',.6);o.rotation_euler[1]=a;o.rotation_euler[2]=.22 if y<0 else -.22
 elif k==17:
  pcb(50,26);box('Relay case',(0,0,11),(20,16,18),'blue',.8);text('SRD-05VDC',(0,0,20.1),2);text('10A 250VAC',(0,-4,20.1),1.4);terminals((-20,-5,6),3);header((19,-2.54,2),3,'Y');smd((12,5,2.3),3);cyl('Indicator LED',(18,8,4),1.5,3,'red')
 elif k==18:
  pcb(32,14,'redPCB');cyl('IR emitter',(10,-3,5),2.5,7,'glass','X');cyl('IR receiver',(10,3,5),2.5,7,'black','X');box('Trimmer',(-2,0,5),(7,7,6),'blue');screw((-2,0,8.2),2);header((-13,-2.54,2),3,'Y');smd((-8,4,2.3),3)
 elif k==19:
  box('Actuator gearbox',(-36,0,16),(35,28,30),'silver',3);cyl('Actuator barrel',(0,0,16),10,48,'silver','X');cyl('Extension rod',(39,0,16),6,30,'silver','X');cyl('Wiper seal',(24,0,16),10.5,3,'black','X')
  for x in [-62,61]:box('Clevis eye',(x,0,16),(17,12,12),'silver',5);cyl('Clevis hole',(x,0,16),3.2,12.2,'black','Y')
  for y in [-9,9]:
   for z in [7,25]:screw((-54,y,z),1.4,'X')
  wire('Actuator supply cable',[(-40,14,8),(-42,25,6),(-20,27,2)],'black',1)

def studio(name,extent=230):
 global C
 s=bpy.data.scenes.new(name);bpy.context.window.scene=s;s.unit_settings.system='METRIC';s.unit_settings.scale_length=.001;s['geometry_units']='millimetres';s['accuracy']='Visual reconstruction from generated images; nominal dimensions, not certified CAD.'
 s.render.engine='BLENDER_EEVEE';s.eevee.taa_render_samples=32;s.eevee.use_gtao=True;s.eevee.gtao_distance=8;s.eevee.gtao_factor=1.25;s.eevee.use_soft_shadows=True;s.render.resolution_x=960;s.render.resolution_y=720;s.render.resolution_percentage=100
 s.world=bpy.data.worlds.new(name+' world');s.world.use_nodes=True;s.world.node_tree.nodes['Background'].inputs[0].default_value=(.65,.75,.85,1);s.world.node_tree.nodes['Background'].inputs[1].default_value=.65
 s.view_settings.view_transform='Standard';s.view_settings.look='None'
 C=bpy.data.collections.new(name+' • Studio');s.collection.children.link(C)
 box('Studio ground',(0,0,-2),(extent*8,extent*8,3),'white',0)
 for p,power,size in [((-extent,-extent,extent*2),extent*extent*4.75,extent*1.5),((extent,-extent*.3,extent),extent*extent*3,extent),((0,extent,extent*1.8),extent*extent*4,extent)]:
  bpy.ops.object.light_add(type='AREA',location=p);o=move(bpy.context.object,'Softbox',None);o.data.energy=power;o['balanced_preview']=True;o.data.size=size;o.rotation_euler=(Vector((0,0,30))-o.location).to_track_quat('-Z','Y').to_euler()
 bpy.ops.object.camera_add(location=(extent*.8,-extent,extent*.85));o=move(bpy.context.object,'Inspection camera',None);o.data.type='ORTHO';o.data.ortho_scale=extent;o.data.clip_start=.1;o.data.clip_end=10000;o.rotation_euler=(Vector((0,0,extent*.12))-o.location).to_track_quat('-Z','Y').to_euler();s.camera=o
 return s

LIB={};MANIFEST={'units':'mm','accuracy':'Visual reconstructions of generated references; nominal dimensions are assumptions. Not manufacturing CAD or validated electrical circuits.','components':[],'projects':[]}

def asset(k):
 global C
 slug=IDS[k];s=studio('Component • '+NAMES[k],max(DIMENSIONS[k])*1.65)
 C=bpy.data.collections.new('PART • '+slug);s.collection.children.link(C);component(k);C.asset_mark();C.asset_data.description=NAMES[k]+' — editable mesh/curve model; nominal visual dimensions in mm.';C['nominal_envelope_mm']=DIMENSIONS[k];C['reference']=str(ROOT/'assets/parts'/f'{slug}.webp');C['accuracy']='Approximate visual reconstruction';LIB[slug]=C
 s['component_id']=slug;bpy.data.libraries.write(str(OUT/'components'/f'{slug}.blend'),{s,C},fake_user=True)
 MANIFEST['components'].append({'id':slug,'name':NAMES[k],'nominal_envelope_mm':DIMENSIONS[k],'objects':len(C.objects),'blend':f'components/{slug}.blend','reference':f'assets/parts/{slug}.webp'})
 return s

def instance(slug,p=(0,0,0),rot=(0,0,0),name=None):
 o=bpy.data.objects.new(name or slug,None);C.objects.link(o);o.instance_type='COLLECTION';o.instance_collection=LIB[slug];o.location=p;o.rotation_euler=rot;o['component_id']=slug;return o

def jumper(a,b,m='red'):
 mid=((a[0]+b[0])/2,(a[1]+b[1])/2,max(a[2],b[2])+25)
 wire('Jumper • '+m,[a,mid,b],m,.5)
 for p in [a,b]:box('Dupont plug',p,(2.5,2.5,6),'black',.2)

def sensor_leads(origin,b):
 # Plug the Dupont jumpers onto the light-sensor board's 3-pin header (local x=-13, y=-2.54..2.54, pin tips at z=9.5).
 ox,oy,oz=origin
 for i,m in enumerate(['red','black','yellow']):jumper((ox-13,oy-2.54+i*2.54,oz+10),(b[0]+i*3,b[1],b[2]),m)

def display(p,body='24.6 C',w=48,h=30):
 x,y,z=p;box('Display PCB',(x,y,z),(w,h,2),'blue');box('Display bezel',(x,y-1,z+2),(w-5,h-5,3),'black');box('Display glass',(x,y-1,z+3.6),(w-10,h-10,.2),'screen');text(body,(x,y-3,z+3.8),h*.3,'light')
 for dx in [-w/2+3,w/2-3]:
  for dy in [-h/2+3,h/2-3]:screw((x+dx,y+dy,z+1.3),1)

def plant(p=(0,0,0)):
 x,y,z=p
 bpy.ops.mesh.primitive_cone_add(vertices=40,radius1=22,radius2=29,depth=42,location=(x,y,z+21));move(bpy.context.object,'Terracotta pot','ceramic');torus('Pot rolled lip',(x,y,z+42),28,2,'ceramic');cyl('Pot soil',(x,y,z+41),25,2,'soil')
 for i in range(10):
  a=i*2.4;end=(x+22*math.cos(a),y+22*math.sin(a),z+65+(i%3)*12);wire('Plant stem',[(x,y,z+42),end],'leaf',.6);o=sphere('Plant leaf',end,(6,16,1.1),'leaf');o.rotation_euler=(.4*math.sin(a),.5,a)
 # Moisture probe is a supplementary project asset.
 box('Moisture probe head',(x+13,y-15,z+45),(12,4,8),'black')
 for dx in [9,17]:box('Moisture probe tine',(x+dx,y-15,z+29),(3,1,30),'silver',.5)

def lamp(p=(0,0,0),mood=False):
 x,y,z=p;cyl('Lamp base',(x,y,z+4),18,8,'wood');cyl('Lamp stem',(x,y,z+25),3,36,'white')
 if mood:sphere('RGB diffuser',(x,y,z+24),(22,22,24),'glass');cyl('RGB light source',(x,y,z+10),10,3,'light')
 else:
  bpy.ops.mesh.primitive_cone_add(vertices=48,radius1=25,radius2=17,depth=32,location=(x,y,z+52));move(bpy.context.object,'Lamp shade','light')

def signal(p,colors=('red','yellow','green')):
 x,y,z=p;box('Signal foot',(x,y,z+2),(24,22,4),'black',2);cyl('Signal pole',(x,y,z+25),2.5,46,'silver');box('Traffic signal casing',(x,y,z+61),(17,10,len(colors)*15+4),'black',2)
 for i,m in enumerate(colors):
  zz=z+61+(len(colors)-1)*7.5-i*15;cyl('Signal LED lens',(x,y-5.2,zz),5.7,2,m,'Y');torus('Signal bezel',(x,y-6.2,zz),6.2,.7,'black','Y')

def door(p=(0,0,0)):
 x,y,z=p;box('Door',(x,y,z+47),(42,5,94),'blue',1)
 for dx in [-25,25]:box('Door jamb',(x+dx,y,z+50),(6,10,100),'wood',.5)
 box('Door lintel',(x,y,z+101),(56,10,6),'wood');cyl('Door knob',(x+14,y-4,z+45),2,4,'gold','Y')

def layout(idx):
 """Compose each project with shared collection instances and additional props."""
 global C
 p=PROJECTS[idx];s=studio('Project • '+p['title'],260 if idx not in [12,23] else 360)
 C=bpy.data.collections.new('ASSEMBLY • '+p['id']);s.collection.children.link(C);s['project_id']=p['id'];s['learning_rule']=p['rule'];s['electrical_status']='Illustrative leads; pin assignments and circuit operation have not been validated.'
 instance('microcontroller',(53,18,0));instance('breadboard',(43,-44,0))
 # Supply/ground routes to board rails. Other wires are illustrative.
 jumper((32,-5,6),(8,-66,13),'red');jumper((38,-5,6),(13,-66,13),'black')
 def part(slug,p,rot=(0,0,0)):return instance(slug,p,rot)
 def leads(a,b,n=3):
  for i,m in enumerate(['red','black','yellow','green'][:n]):jumper((a[0]+i*3,a[1],a[2]),(b[0]+i*3,b[1],b[2]),m)
 if idx==0:
  signal((-65,0,0));leads((-65,-5,42),(20,-45,14))
  for i,m in enumerate(['red','yellow','green']):box('Series resistor',(-5+i*8,-44,13),(6,2,2),'ceramic')
 elif idx in [1,5]:
  plant((-53,7,0));leads((-40,-8,45),(20,40,7))
  if idx==5:
   part('motor-driver',(12,-24,10));cyl('Water reservoir',(-74,-57,26),16,50,'glass');cyl('Water surface',(-74,-57,35),15,.3,'cyan');box('Low-voltage pump',(-74,-57,13),(13,10,17),'white');wire('Water tube',[(-74,-57,23),(-70,-45,85),(-48,0,85),(-48,5,47)],'glass',2)
 elif idx==2:
  part('light-sensor',(-55,35,0));part('buzzer',(12,-45,11))
  for x in [-75,-25]:box('Tripwire stand',(x,0,4),(18,18,8),'black');cyl('Stand stem',(x,0,25),2,38,'black');cyl('Optical module',(x,0,44),5,15,'black','X')
  wire('Illustrative beam',[(-67,0,44),(-33,0,44)],'red',.35);sensor_leads((-55,35,0),(20,40,7))
 elif idx in [3,10]:
  box('Servo platform base',(-55,0,3),(55,40,6),'black');part('servo-actuator',(-55,0,6));o=part('ultrasonic-sensor',(-50,0,53),(math.pi/2,0,0));leads((-45,0,33),(20,40,7))
  if idx==10:
   for x in [-76,-34]:box('Turret support',(x,0,25),(4,35,40),'wood');box('Turret deck',(-50,0,43),(45,30,4),'wood')
  # Choreographed sweep for inspection; geometry is reused from the component library.
  for frame,a in [(1,-.65),(60,.65),(120,-.65)]:o.rotation_euler[2]=a;o.keyframe_insert('rotation_euler',frame=frame)
  s.frame_end=120
 elif idx in [4,6,11,13]:
  lamp((-58,0,0),idx==6)
  if idx==4:part('light-sensor',(10,-42,11));sensor_leads((10,-42,11),(25,40,7))
  elif idx==11:
   # IR receiver and remote are supplementary assets, distinct from obstacle module.
   box('IR receiver module',(-8,8,4),(12,16,2),'blue');box('38kHz IR receiver',(-8,8,9),(6,5,9),'black');box('IR remote',(-56,-62,4),(28,60,8),'black',3)
   for j in range(12):cyl('Remote button',(-64+(j%3)*8,-80+(j//3)*9,8.5),2.5,1.5,'red' if j==0 else 'white')
  elif idx==13:
   box('Bluetooth PCB',(0,14,4),(18,34,2),'greenPCB');box('Bluetooth radio',(0,14,6),(12,18,2),'silver');wire('Printed antenna',[(-6,25,5),(-6,29,5),(-2,29,5),(-2,25,5),(2,25,5),(2,29,5),(6,29,5)],'gold',.4)
   box('Phone',(-60,-58,4),(35,65,7),'black',4);box('Phone glass',(-60,-58,7.7),(31,59,.2),'screen',2);text('ON',(-60,-59,8),8,'cyan')
  leads((-48,0,5),(20,40,7))
 elif idx==7:
  box('Hallway floor',(-56,12,2),(80,80,4),'wood');box('Hallway rear wall',(-56,49,46),(80,5,90),'white');box('Hallway side',(-94,12,46),(4,80,90),'white');door((-56,44,4));part('motion-sensor',(-20,25,42),(math.pi/2,0,0));cyl('Ceiling LED',(-56,8,94),9,3,'light');leads((-20,25,45),(20,40,7))
 elif idx in [8,9,21]:
  display((-42,2,18),'00:25' if idx==8 else '24.6 C' if idx==9 else '0.37')
  for x in [-61,-23]:cyl('Display brass standoff',(x,2,9),2,16,'gold')
  if idx==9:part('temperature-sensor',(-40,36,0))
  else:
   for x in [-58,-23]:part('push-button',(x,-48,0))
   part('buzzer',(18,-43,11))
  leads((-40,2,21),(20,40,7))
 elif idx==12:
  # Miniature camera slider with two rails, threaded lead screw and carriage.
  for y in [-24,24]:cyl('Slider rail',(-30,y,20),3,160,'silver','X')
  for x in [-110,50]:box('Rail end plate',(x,0,17),(6,62,34),'black')
  cyl('Lead screw',(-30,0,16),2.5,160,'silver','X')
  for i in range(65):torus('Lead screw thread',(-108+i*2.4,0,16),2.6,.35,'silver','X')
  box('Camera carriage',(-30,0,28),(38,65,8),'black');box('Camera body',(-30,0,48),(42,22,32),'black',3);cyl('Camera lens',(-30,-24,48),14,28,'black','Y');cyl('Lens glass',(-30,-38.2,48),11,.3,'glass','Y');part('stepper-motor',(-125,0,20),(0,math.pi/2,0));part('motor-driver',(56,50,0));leads((-123,22,12),(55,40,7))
 elif idx==14:
  signal((-70,15,0),('red','green'));signal((-20,15,0),('red','green'));part('push-button',(-45,-42,0))
  box('Crossing road',(-50,0,-.2),(110,115,2),'rubber')
  for y in range(-35,36,14):box('Zebra stripe',(-50,y,1),(48,6,.15),'white',0)
  leads((-45,-42,10),(20,40,7))
 elif idx==15:
  part('temperature-sensor',(-45,10,0));part('buzzer',(20,-44,11));part('led',(-15,-42,11));leads((-45,10,10),(20,40,7))
 elif idx==16:
  box('Piano key bed',(-48,0,3),(100,40,6),'wood')
  for i,m in enumerate(['red','orange','yellow','green','cyan','blue','purple','white']):
   x=-90+i*12;box('Piano key',(x,0,9),(10,35,7),'white',1);box('Colored key cap',(x,7,14),(10,16,3),m,1);jumper((x,16,10),(20+i*3,40,7),m if m!='white' else 'black')
  part('buzzer',(12,-45,11))
 elif idx==17:
  door((-58,24,0));part('push-button',(-23,21,48),(math.pi/2,0,0));part('buzzer',(13,-44,11));leads((-23,21,49),(20,40,7))
 elif idx==18:
  box('Dice housing',(-52,0,30),(42,42,60),'white',2);box('Dice face',(-52,-21.2,30),(38,.3,56),'black',1)
  for dx,dz in [(-11,-17),(-11,0),(-11,17),(0,0),(11,-17),(11,0),(11,17)]:cyl('Dice LED',(-52+dx,-22,30+dz),2.5,2,'red','Y')
  part('push-button',(-45,-51,0));leads((-45,-51,10),(20,40,7))
 elif idx==19:
  colors=['red','orange','yellow','green','cyan','purple']
  for i,m in enumerate(colors):
   x=-90+i*15;part('push-button',(x,-40,0));cyl('Button color cap',(x,-40,14),6,1,m);part('led',(x,0,0));sphere('Colored LED lens',(x,0,25),(2.55,2.55,3),m);jumper((x,0,4),(20+i*3,40,7),m)
 elif idx==20:
  box('Parking lot',(-50,0,1),(125,100,2),'rubber');box('Parking stop',(-65,39,10),(85,4,20),'white');part('ultrasonic-sensor',(-50,29,32),(math.pi/2,0,0));box('Toy car body',(-60,-15,13),(28,45,15),'yellow',5);box('Toy car roof',(-60,-10,24),(24,22,10),'yellow',4)
  for x in [-74,-46]:
   for y in [-30,2]:cyl('Toy car wheel',(x,y,8),6,4,'rubber','X')
  part('buzzer',(15,-44,11));leads((-50,29,31),(20,40,7))
 elif idx==22:
  box('Rain sensor FR4',(-55,0,2),(45,35,3),'black');
  for i in range(10):
   y=-14+i*3;box('Rain sensor conductive comb',(-55,y,3.6),(36,1,.15),'silver',0)
   box('Comb spine',(-73 if i%2==0 else -37,y,3.6),(1,3,.15),'silver',0)
  for x,y in [(-70,9),(-46,-8),(-60,-13)]:sphere('Water droplet',(x,y,4.6),(2,2,1),'glass')
  part('buzzer',(16,-43,11));leads((-55,17,5),(20,40,7))
 elif idx==23:
  box('House base',(-70,25,3),(115,90,6),'wood');box('House rear wall',(-70,66,70),(110,4,130),'white');box('House side',(-124,25,70),(4,85,130),'wood');box('Upper floor',(-70,25,67),(110,85,5),'wood')
  for x,a in [(-99,-.55),(-41,.55)]:o=box('Pitched roof',(x,25,152),(68,95,5),'wood');o.rotation_euler[1]=a
  door((-43,5,6));part('motion-sensor',(-17,43,77),(math.pi/2,0,0));part('temperature-sensor',(-17,45,37),(math.pi/2,0,0));part('servo-actuator',(-36,12,6))
  for z in [54,118]:cyl('Room light',(-90,25,z),7,3,'light');box('Miniature sofa',(-98,43,z-34),(35,22,15),'ceramic',3)
  plant((-100,-25,0));leads((-17,43,70),(20,40,7))
 used=sorted({o['component_id'] for o in C.objects if 'component_id' in o})
 s['reused_components']=json.dumps(used);bpy.data.libraries.write(str(OUT/'projects'/f"{p['id']}.blend"),{s},fake_user=True)
 MANIFEST['projects'].append({'id':p['id'],'title':p['title'],'blend':f"projects/{p['id']}.blend",'reused_components':used,'rule':p['rule'],'reference':p['image'],'circuit_status':'Illustrative, not electrically validated'})
 return s

def gallery():
 global C
 s=studio('START HERE • 20 reusable robotics components',590);C=bpy.data.collections.new('Component library overview');s.collection.children.link(C)
 for i,slug in enumerate(IDS):
  x=(i%5-2)*105;y=(1.5-i//5)*100;instance(slug,(x,y,0));text(f'{i+1:02d}  '+NAMES[i],(x,y-34,.1),4,'black')
 s.camera.location=(320,-540,560);s.camera.rotation_euler=(Vector((0,0,15))-s.camera.location).to_track_quat('-Z','Y').to_euler();s.camera.data.ortho_scale=620
 s.render.resolution_x=1600;s.render.resolution_y=1200
 return s

def finish():
 s=gallery();bpy.context.window.scene=s
 for screen in bpy.data.screens:
  for area in screen.areas:
   if area.type=='VIEW_3D':
    area.spaces.active.region_3d.view_perspective='CAMERA';area.spaces.active.clip_start=.1;area.spaces.active.clip_end=10000;area.spaces.active.shading.type='MATERIAL';area.spaces.active.overlay.show_overlays=False
 (OUT/'manifest.json').write_text(json.dumps(MANIFEST,indent=2))
 bpy.ops.wm.save_as_mainfile(filepath=str(OUT/'robotics-library.blend'))
 (OUT/'build-complete.json').write_text(json.dumps({'components':len(LIB),'projects':len(PROJECTS),'scenes':len(bpy.data.scenes),'finished':time.strftime('%Y-%m-%d %H:%M:%S')}))
 print('BUILD COMPLETE: 20 editable assets, 24 project scenes, shared collection geometry.',flush=True)

# A timer yields back to the Blender UI after every component/project, so the user
# can watch actual objects appear and can orbit/pause between build stages.
bpy.ops.wm.read_factory_settings(use_empty=True)
# Factory reset removes materials; preserve definitions by running material setup again.
M.clear()
for args in MATERIAL_SPECS:mat(*args)
step=0

def tick():
 global step
 try:
  if step<20:s=asset(step);label=NAMES[step]
  elif step<44:s=layout(step-20);label=PROJECTS[step-20]['title']
  else:finish();return None
  print(f'BUILD {step+1}/44: {label}',flush=True)
  (OUT/'progress.json').write_text(json.dumps({'step':step+1,'total':44,'name':label}))
  for screen in bpy.data.screens:
   for area in screen.areas:
    if area.type=='VIEW_3D':
     area.spaces.active.region_3d.view_perspective='CAMERA';area.spaces.active.shading.type='MATERIAL';area.spaces.active.clip_start=.1;area.spaces.active.clip_end=10000
  step+=1
  return 2.5
 except Exception:
  import traceback;traceback.print_exc();(OUT/'build-error.txt').write_text(traceback.format_exc());return None
if bpy.app.background:
 while step<44:
  if tick() is None:raise RuntimeError('Build failed')
 finish()
else:bpy.app.timers.register(tick,first_interval=2)
