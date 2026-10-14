# Neutral studio illumination: readable colours without blown highlights.
for name,power in [('Large softbox',48),('Soft fill',24),('Back edge light',32)]:bpy.data.objects[name].data.energy=power
scene.view_settings.exposure=0
scene.world.node_tree.nodes['Background'].inputs[0].default_value=(.7,.7,.7,1)
scene.world.node_tree.nodes['Background'].inputs[1].default_value=.35
scene.eevee.taa_samples=32;scene.eevee.taa_render_samples=128
scene.eevee.use_ssr=False;scene.eevee.use_ssr_refraction=False
scene.eevee.use_gtao=True;scene.eevee.gtao_distance=.10;scene.eevee.gtao_factor=1.0
scene.eevee.use_soft_shadows=True;scene.eevee.shadow_cube_size='2048';scene.eevee.shadow_cascade_size='2048'
# Alpha blending sorts entire objects and can pop between overlapping plates.
# Hashed transparency avoids that object-order flicker, with high sample counts.
clear.blend_method='HASHED';clear.use_screen_refraction=False;clear.shadow_method='NONE';clear.use_nodes=True
p=clear.node_tree.nodes['Principled BSDF'];p.inputs['Transmission'].default_value=0;p.inputs['Alpha'].default_value=.20;p.inputs['Base Color'].default_value=(.68,.86,.91,1);p.inputs['Roughness'].default_value=.22
scene.render.resolution_x=1920;scene.render.resolution_y=1620;scene.render.resolution_percentage=100
scene.render.image_settings.color_mode='RGB';scene.render.film_transparent=False
scene.sync_mode='FRAME_DROP';scene.render.use_motion_blur=False
for l in collections['08 Cameras and lighting'].objects:
 if l.type=='LIGHT':l.data.use_shadow=True;l.data.use_contact_shadow=True;l.data.contact_shadow_distance=.2
# Hash transparency also needs convergence in a paused material preview.
scene.frame_set(145)
for screen in bpy.data.screens:
 for area in screen.areas:
  if area.type=='VIEW_3D':area.spaces.active.shading.type='MATERIAL';area.spaces.active.shading.use_scene_lights=True;area.spaces.active.shading.use_scene_world=True;area.tag_redraw()
scene['quality_notes']='Normal neutral lighting. 128 render samples, 1920px output, soft 2048px shadows. Hashed acrylic transparency replaces alpha-sort blending; SSR disabled to avoid moving reflection/refraction artifacts. Rendered animation provides fixed 24 fps independent of viewport performance.'
bpy.ops.wm.save_as_mainfile(filepath=OUT+'/robot-white-room.blend')
print('Normal lighting, high quality output and stable acrylic transparency saved.')
