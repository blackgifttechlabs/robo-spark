import bpy,os,math,json
from mathutils import Vector
scene=bpy.data.scenes['Robot • White Studio'];bpy.context.window.scene=scene
OUT='/home/watchman-admin/Documents/tinashe/learn-robotics/models/robot-car'
master=bpy.data.objects['Robot assembly • move whole robot'];wheel_roots=[bpy.data.objects[n+' wheel rotation'] for n in ['Left Front','Left Rear','Right Front','Right Rear']]
collections={c.name:c for c in scene.collection.children};camera=bpy.data.objects['Hero camera'];blocks=[bpy.data.objects['Obstacle block %d'%i] for i in range(1,4)]
clear=bpy.data.materials['Clear acrylic'];clear.name='White molded chassis plastic';clear.blend_method='OPAQUE';clear.use_screen_refraction=False;clear.shadow_method='OPAQUE'
p=clear.node_tree.nodes['Principled BSDF'];p.inputs['Base Color'].default_value=(.78,.80,.82,1);p.inputs['Roughness'].default_value=.38;p.inputs['Transmission'].default_value=0;p.inputs['Alpha'].default_value=1;clear.diffuse_color=(.78,.80,.82,1)
scene.render.resolution_x=1920;scene.render.resolution_y=1080;scene.eevee.taa_render_samples=128;scene.eevee.taa_samples=16;scene.eevee.use_ssr=False;scene.eevee.use_ssr_refraction=False
camera.data.shift_x=-.12
scene.frame_set(145)
# Open with a stable, responsive solid viewport; final render lighting stays saved.
for m in bpy.data.materials:
 if m.use_nodes and m.node_tree.nodes.get('Principled BSDF'):
  m.diffuse_color=m.node_tree.nodes['Principled BSDF'].inputs['Base Color'].default_value
 if 'HUATAI' in m.name:m.diffuse_color=(.8,.01,.02,1)
for screen in bpy.data.screens:
 for area in screen.areas:
  if area.type=='VIEW_3D':area.spaces.active.shading.type='SOLID';area.spaces.active.shading.color_type='MATERIAL';area.spaces.active.overlay.show_overlays=False;area.tag_redraw()
scene['chassis_material']='Solid white plastic.'
scene['recovery_notes']='Recovered from the last stable saved version. Experimental combined viewport meshes omitted. Playback is paused; native animation and high-quality render settings preserved.'
bpy.ops.wm.save_as_mainfile(filepath=OUT+'/robot-white-room.blend')
bpy.app.driver_namespace['robot_build']={k:v for k,v in locals().copy().items() if not k.startswith('__')}
print('Recovered animated robot, batteries, blocks and white plastic; saved safely.')
try:bpy.ops.blendermcp.start_server()
except Exception as e:print('Bridge startup:',e)
