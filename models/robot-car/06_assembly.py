active=collections['02 Chassis']
bpy.ops.object.empty_add(type='PLAIN_AXES',location=(0,0,0));master=move(bpy.context.object);master.name='Robot assembly • move whole robot';master.empty_display_size=.04
for key in ['02 Chassis','03 Wheels and motors','04 Arduino electronics','05 Battery holder','06 Ultrasonic sensor','07 Wiring']:
 for o in list(collections[key].objects):
  if o!=master and o.parent is None:world=o.matrix_world.copy();o.parent=master;o.matrix_world=world
bpy.ops.object.select_all(action='DESELECT');master.select_set(True);bpy.context.view_layer.objects.active=master
bpy.ops.wm.save_as_mainfile(filepath=OUT+'/robot-white-room.blend')
print('Master assembly control saved. Robot remains open in Blender.')
