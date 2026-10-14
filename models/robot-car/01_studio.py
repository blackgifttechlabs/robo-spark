import bpy, math, os
from mathutils import Vector,Quaternion
OUT='/home/watchman-admin/Documents/tinashe/learn-robotics/models/robot-car'
scene=bpy.data.scenes.get('Robot • White Studio')
if scene is None:scene=bpy.data.scenes.new('Robot • White Studio')
bpy.context.window.scene=scene
scene.unit_settings.system='METRIC';scene.unit_settings.scale_length=1
scene.render.engine='BLENDER_EEVEE';scene.eevee.taa_render_samples=64;scene.eevee.use_gtao=True;scene.eevee.gtao_distance=.2;scene.eevee.gtao_factor=1.3;scene.eevee.use_soft_shadows=True;scene.eevee.use_ssr=True;scene.eevee.use_ssr_refraction=True
scene.render.resolution_x=1600;scene.render.resolution_y=1200;scene.render.resolution_percentage=100
scene.world=bpy.data.worlds.new('White studio environment');scene.world.use_nodes=True;scene.world.node_tree.nodes['Background'].inputs[0].default_value=(.8,.8,.8,1);scene.world.node_tree.nodes['Background'].inputs[1].default_value=.7
scene.view_settings.view_transform='Standard';scene.view_settings.look='None';scene.view_settings.exposure=0
# Keep all parts organised and editable.
collections={}
for name in ['01 White room','02 Chassis','03 Wheels and motors','04 Arduino electronics','05 Battery holder','06 Ultrasonic sensor','07 Wiring','08 Cameras and lighting']:
 c=bpy.data.collections.new(name);scene.collection.children.link(c);collections[name]=c
active=collections['01 White room']
def move(o):
 for c in list(o.users_collection):c.objects.unlink(o)
 active.objects.link(o);return o

def material(name,c,metal=0,rough=.4):
 m=bpy.data.materials.new(name);m.use_nodes=True;p=m.node_tree.nodes.get('Principled BSDF');p.inputs['Base Color'].default_value=(*c,1);p.inputs['Metallic'].default_value=metal;p.inputs['Roughness'].default_value=rough;return m
white=material('White studio matte',(.92,.92,.92),rough=.78)
rubber=material('Black molded tyre rubber',(.018,.021,.025),rough=.72)
yellow=material('Yellow injection molded ABS',(.98,.66,.014),rough=.3)
black=material('Black electronics plastic',(.018,.022,.028),rough=.4)
metal=material('Machined aluminium',(.65,.70,.73),.8,.24)
gold=material('Gold plated pins',(.74,.49,.12),.75,.27)
blue=material('Blue solder mask',(.016,.23,.38),.1,.36)
ink=material('White silkscreen',(.94,.96,.98),rough=.65)
red=material('Red insulated wire',(.62,.008,.018),rough=.35)
wireblue=material('Blue insulated wire',(.006,.19,.60),rough=.35)
wireyellow=material('Yellow insulated wire',(.95,.60,.01),rough=.35)
clear=material('Clear acrylic',(.83,.96,1),rough=.08);p=clear.node_tree.nodes['Principled BSDF'];p.inputs['Transmission'].default_value=1;p.inputs['IOR'].default_value=1.46;p.inputs['Alpha'].default_value=.28;clear.blend_method='BLEND';clear.use_screen_refraction=True;clear.show_transparent_back=False

def bevel(o,width=.001,segments=3):
 b=o.modifiers.new('Manufactured edge radius','BEVEL');b.width=width;b.segments=segments;o.data.use_auto_smooth=True;o.modifiers.new('Weighted normals','WEIGHTED_NORMAL');return o

def box(name,loc,size,mat,r=.001):
 bpy.ops.mesh.primitive_cube_add(size=1,location=loc);o=move(bpy.context.object);o.name=name;o.scale=size;bpy.ops.object.transform_apply(location=False,rotation=False,scale=True);o.data.materials.append(mat)
 if r:bevel(o,r)
 return o

def cylinder(name,loc,radius,depth,mat,axis='Z',vertices=48):
 bpy.ops.mesh.primitive_cylinder_add(vertices=vertices,radius=radius,depth=depth,location=loc);o=move(bpy.context.object);o.name=name;o.rotation_euler=Vector({'X':(1,0,0),'Y':(0,1,0),'Z':(0,0,1)}[axis]).to_track_quat('Z','Y').to_euler();o.data.materials.append(mat)
 for p in o.data.polygons:p.use_smooth=True
 bevel(o,min(.0005,depth/5),2);return o

def sphere(name,loc,size,mat):
 bpy.ops.mesh.primitive_uv_sphere_add(segments=24,ring_count=12,location=loc);o=move(bpy.context.object);o.name=name;o.scale=size;o.data.materials.append(mat)
 for p in o.data.polygons:p.use_smooth=True
 return o

def curve(name,points,r,mat):
 c=bpy.data.curves.new(name,'CURVE');c.dimensions='3D';c.resolution_u=16;c.bevel_depth=r;c.bevel_resolution=3;sp=c.splines.new('BEZIER');sp.bezier_points.add(len(points)-1)
 for p,co in zip(sp.bezier_points,points):p.co=co;p.handle_left_type='AUTO';p.handle_right_type='AUTO'
 o=bpy.data.objects.new(name,c);active.objects.link(o);o.data.materials.append(mat);return o

def text(name,body,loc,size,mat,rotation=None):
 c=bpy.data.curves.new(name,'FONT');c.body=body;c.size=size;c.extrude=.000015;c.align_x='CENTER';o=bpy.data.objects.new(name,c);active.objects.link(o);o.location=loc;o.data.materials.append(mat)
 if rotation:o.rotation_euler=rotation
 return o
box('White floor',(0,0,-.009),(3,3,.016),white,.006)
box('White back wall',(0,.65,.50),(3,.025,1),white,.02)
box('White left wall',(-.75,0,.50),(.025,1.3,1),white,.02)
box('White right wall',(.75,0,.50),(.025,1.3,1),white,.02)
active=collections['08 Cameras and lighting']
def light(name,loc,power,size):
 bpy.ops.object.light_add(type='AREA',location=loc);o=move(bpy.context.object);o.name=name;o.data.energy=power;o.data.size=size;o.rotation_euler=(Vector((0,0,.06))-o.location).to_track_quat('-Z','Y').to_euler()
light('Large softbox',(-.35,-.35,.55),12,.45);light('Soft fill',(.35,-.15,.35),7,.35);light('Back edge light',(.05,.35,.5),10,.3)
bpy.ops.object.camera_add(location=(.36,-.43,.30));camera=move(bpy.context.object);camera.name='Hero camera';camera.rotation_euler=(Vector((0,0,.065))-camera.location).to_track_quat('-Z','Y').to_euler();camera.data.type='ORTHO';camera.data.ortho_scale=.43;camera.data.lens=70;camera.data.clip_start=.001;scene.camera=camera
for screen in bpy.data.screens:
 for area in screen.areas:
  if area.type=='VIEW_3D':
   area.spaces.active.region_3d.view_perspective='CAMERA';area.spaces.active.clip_start=.001;area.spaces.active.shading.type='MATERIAL';area.spaces.active.shading.use_scene_world=True;area.spaces.active.shading.use_scene_lights=True
# Keep functions and materials across live bridge commands.
namespace={k:v for k,v in locals().copy().items() if not k.startswith('__')}
bpy.app.driver_namespace['robot_build']=namespace
print('White studio ready; original scene preserved.')
