for i in range(1,5):
 o=bpy.data.objects['HUATAI battery %d red sleeve'%i]
 for loop in o.data.uv_layers.active.data:loop.uv.y=1-loop.uv.y
bpy.ops.wm.save_as_mainfile(filepath=OUT+'/robot-white-room.blend')
print('Label reading direction corrected.')
