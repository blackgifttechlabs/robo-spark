if bpy.context.screen.is_animation_playing:bpy.ops.screen.animation_play()
plastic=bpy.data.materials.get('White molded chassis plastic') or material('White molded chassis plastic',(.78,.80,.82),rough=.38)
p=plastic.node_tree.nodes['Principled BSDF'];p.inputs['Transmission'].default_value=0;p.inputs['Alpha'].default_value=1
plastic.blend_method='OPAQUE';plastic.diffuse_color=(.85,.87,.89,1)
# Apply to original editable parts and the combined viewport geometry.
for o in scene.objects:
 if o.type=='MESH':
  for slot in o.material_slots:
   if slot.material==clear:slot.material=plastic
scene.render.resolution_x=1920;scene.render.resolution_y=1080;scene.render.resolution_percentage=100
camera.data.shift_x=-.12
scene.frame_set(145)
scene['chassis_material']='Solid white molded plastic; glass removed.'
bpy.ops.wm.save_as_mainfile(filepath=OUT+'/robot-white-room.blend')
print('Chassis changed to solid white plastic in both editable parts and live viewport; widescreen hero framing saved.')
