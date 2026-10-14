# Set a useful starting view and save the native, fully editable scene.
scene['reference']='Four-view robot reference generated from the supplied robot photograph.'
scene['front_direction']='Negative Y; wheels rotate around local X.'
scene['dimensions_note']='Approximate visual proportions, not a measured engineering CAD model.'
for root in wheel_roots:root['rotate_axis']='X'
active=collections['08 Cameras and lighting']
for name,loc in [('Front',(0,-.55,.13)),('Rear',(0,.55,.13)),('Left',(-.55,0,.13)),('Right',(.55,0,.13)),('Top',(0,0,.55))]:
 bpy.ops.object.camera_add(location=loc);o=move(bpy.context.object);o.name=name+' orthographic camera';o.rotation_euler=(Vector((0,0,.07))-o.location).to_track_quat('-Z','Y').to_euler();o.data.type='ORTHO';o.data.ortho_scale=.30;o.data.clip_start=.001
scene.camera=camera
scene.render.image_settings.file_format='PNG';scene.render.filepath=OUT+'/robot-white-room.png'
bpy.ops.object.select_all(action='DESELECT')
for screen in bpy.data.screens:
 for area in screen.areas:
  if area.type=='VIEW_3D':
   area.spaces.active.region_3d.view_perspective='CAMERA';area.spaces.active.region_3d.view_camera_zoom=12;area.spaces.active.overlay.show_overlays=False
bpy.ops.wm.save_as_mainfile(filepath=OUT+'/robot-white-room.blend')
assert len(wheel_roots)==4
assert all(len(o.data.vertices)>0 for o in scene.objects if o.type=='MESH')
print('Saved robot-white-room.blend with',len(scene.objects),'editable objects and six cameras.')
