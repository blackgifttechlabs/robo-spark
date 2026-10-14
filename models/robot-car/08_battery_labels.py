# Rotate the printed sleeve around each cell so its branding faces upward.
for i in range(1,5):
 o=bpy.data.objects['HUATAI battery %d red sleeve'%i]
 for loop in o.data.uv_layers.active.data:loop.uv.x+=.28
bpy.ops.wm.save_as_mainfile(filepath=OUT+'/robot-white-room.blend')
print('Battery branding rotated into view and saved.')
