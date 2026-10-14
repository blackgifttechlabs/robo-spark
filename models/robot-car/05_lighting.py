# Balance light for the Standard colour profile on this Blender installation.
for name,energy in [('Large softbox',3),('Soft fill',1.5),('Back edge light',2.5)]:bpy.data.objects[name].data.energy=energy
clear.node_tree.nodes['Principled BSDF'].inputs['Alpha'].default_value=.45
# Use a deeper blue PCB and warm saturated moulded plastic.
blue.node_tree.nodes['Principled BSDF'].inputs['Base Color'].default_value=(.008,.10,.22,1)
yellow.node_tree.nodes['Principled BSDF'].inputs['Base Color'].default_value=(.85,.43,.005,1)
for screen in bpy.data.screens:
 for area in screen.areas:
  if area.type=='VIEW_3D':area.spaces.active.overlay.show_overlays=False;area.tag_redraw()
bpy.ops.wm.save_as_mainfile(filepath=OUT+'/robot-white-room.blend')
print('Balanced white studio lighting; scene saved.')
