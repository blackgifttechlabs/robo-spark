for name,power in [('Large softbox',35),('Soft fill',18),('Back edge light',24)]:bpy.data.objects[name].data.energy=power
scene.view_settings.exposure=-.15
scene.frame_set(1)
bpy.ops.wm.save_as_mainfile(filepath=OUT+'/robot-white-room.blend')
print('Softer light balance saved, with visible colour and shadow detail.')
if not bpy.context.screen.is_animation_playing:bpy.ops.screen.animation_play()
