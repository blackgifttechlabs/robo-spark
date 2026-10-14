if bpy.context.screen.is_animation_playing:bpy.ops.screen.animation_play()
scene.frame_set(1)
bpy.data.objects['White floor'].dimensions=(8,8,.016)
bpy.data.objects['White back wall'].location.y=4;bpy.data.objects['White back wall'].dimensions=(8,.025,2.4)
bpy.data.objects['White left wall'].location.x=-4;bpy.data.objects['White left wall'].dimensions=(.025,8,2.4)
bpy.data.objects['White right wall'].location.x=4;bpy.data.objects['White right wall'].dimensions=(.025,8,2.4)
# Retain a fixed overview camera alongside a closer tracking hero camera.
overview=bpy.data.objects.new('Obstacle course overview camera',camera.data.copy());collections['08 Cameras and lighting'].objects.link(overview);overview.matrix_world=camera.matrix_world.copy()
start_target=Vector((0,-.10,.04));direction=(camera.location-start_target).normalized();start_offset=camera.location-start_target
camera.animation_data_clear();camera.data.animation_data_clear()
for f in range(1,scene.frame_end+1):
 scene.frame_set(f);u=max(0,min(1,(f-24)/48));u=u*u*(3-2*u)
 robot=master.location.copy();close_target=Vector((robot.x,robot.y-.25,.06));target=start_target.lerp(close_target,u);offset=start_offset.lerp(direction*1.65,u)
 camera.location=target+offset;camera.rotation_euler=(target-camera.location).to_track_quat('-Z','Y').to_euler();camera.data.ortho_scale=2.9*(1-u)+1.25*u;camera.keyframe_insert('location',frame=f);camera.keyframe_insert('rotation_euler',frame=f);camera.data.keyframe_insert('ortho_scale',frame=f)
for anim in [camera.animation_data,camera.data.animation_data]:
 for fc in anim.action.fcurves:
  for k in fc.keyframe_points:k.interpolation='LINEAR'
scene.frame_set(1);scene.camera=camera
bpy.ops.wm.save_as_mainfile(filepath=OUT+'/robot-white-room.blend')
print('Room expanded to 8 metres; overview and smooth tracking cameras saved.')
