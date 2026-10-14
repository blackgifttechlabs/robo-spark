from mathutils import Matrix
# Ensure every model component follows the master; keep wheel/battery hierarchies.
excluded={'White floor','White back wall','White left wall','White right wall','Ultrasonic detection indicator'}
fixed=0
for o in scene.objects:
 if o==master or o.type in {'LIGHT','CAMERA'} or o.name in excluded or o.name.startswith(('Obstacle block','Block ')):continue
 if o.parent is None:
  rest=o.matrix_world.copy();o.parent=master;o.matrix_parent_inverse=Matrix.Identity(4);o.matrix_basis=rest;fixed+=1
# Correct collection organisation for the separately editable robot parts.
for o in scene.objects:
 if o==master or o.name in excluded or o.name.startswith(('Obstacle block','Block ')) or o.type in {'LIGHT','CAMERA'}:continue
 n=o.name
 if n.startswith(('Left Front','Left Rear','Right Front','Right Rear')):key='03 Wheels and motors'
 elif n.startswith(('Clear acrylic','M3 ','Chassis screw','Screw slot')):key='02 Chassis'
 elif 'lead' in n or n.startswith(('Jumper','Motor red','Motor black')):key='07 Wiring'
 elif n.startswith(('Battery','HUATAI')):key='05 Battery holder'
 elif n.startswith(('Ultrasonic','Sensor','White ultrasonic','HC-SR04')):key='06 Ultrasonic sensor'
 else:key='04 Arduino electronics'
 for c in list(o.users_collection):c.objects.unlink(o)
 collections[key].objects.link(o)
bpy.data.objects['White back wall'].location.y=3
bpy.data.objects['White left wall'].location.x=-3
bpy.data.objects['White right wall'].location.x=3
for name,power in [('Large softbox',75),('Soft fill',40),('Back edge light',60)]:bpy.data.objects[name].data.energy=power
camera.data.ortho_scale=2.9
scene.frame_set(1);bpy.context.view_layer.update()
# Verify the wheels, board and holder actually move with the robot.
for name in ['Left Front wheel rotation','Arduino Uno blue PCB','Battery tray base']:
 o=bpy.data.objects[name];assert o.parent==master,name;assert o.matrix_world.translation.y>.9,name
scene.render.resolution_x=1280;scene.render.resolution_y=1080;scene.eevee.taa_render_samples=24
bpy.ops.wm.save_as_mainfile(filepath=OUT+'/robot-white-room.blend')
print('Fixed',fixed,'assembly parents; wheel, board and holder movement verified.')
