if bpy.context.screen.is_animation_playing:bpy.ops.screen.animation_play()
for name,power in [('Large softbox',25),('Soft fill',12),('Back edge light',18)]:bpy.data.objects[name].data.energy=power
scene.world.node_tree.nodes['Background'].inputs[0].default_value=(.55,.55,.55,1)
scene.world.node_tree.nodes['Background'].inputs[1].default_value=.25
scene.view_settings.exposure=-.25
# Keep printed and metal detail from washing out in highlights.
for mname in ['Machined aluminium','Yellow injection molded ABS']:
 m=bpy.data.materials.get(mname)
 if m:m.node_tree.nodes['Principled BSDF'].inputs['Roughness'].default_value=.38
scene.frame_set(145)
for screen in bpy.data.screens:
 for area in screen.areas:
  if area.type=='VIEW_3D':
   area.spaces.active.shading.use_scene_lights=True;area.spaces.active.shading.use_scene_world=True;area.tag_redraw()
bpy.ops.wm.save_as_mainfile(filepath=OUT+'/robot-white-room.blend')
print('Lights reduced by about two thirds; lower environment brightness and exposure saved.')
