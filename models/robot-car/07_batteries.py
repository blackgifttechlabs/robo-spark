# Four reference-style red HUATAI cells, placed inside the existing slots.
active=collections['05 Battery holder']
label=bpy.data.materials.get('HUATAI red printed battery sleeve') or material('HUATAI red printed battery sleeve',(.8,.005,.02),rough=.32)
nt=label.node_tree;tex=nt.nodes.new('ShaderNodeTexImage');tex.image=bpy.data.images.load(OUT+'/huatai-battery-label.png',check_existing=True);tex.image.pack();nt.links.new(tex.outputs['Color'],nt.nodes['Principled BSDF'].inputs['Base Color'])
# Slot positions and available length match the existing holder.
for i,x in enumerate([-.035,-.0117,.0117,.035]):
 before=set(bpy.data.objects);z=.090;y0=.035;y1=.082;r=.0098;N=96
 verts=[];faces=[]
 for y in [y0,y1]:
  for j in range(N):
   a=j*math.tau/N;verts.append((x+r*math.cos(a),y,z+r*math.sin(a)))
 for j in range(N):faces.append((j,(j+1)%N,(j+1)%N+N,j+N))
 mesh=bpy.data.meshes.new('Battery %d printed sleeve mesh'%(i+1));mesh.from_pydata(verts,[],faces);mesh.update();o=bpy.data.objects.new('HUATAI battery %d red sleeve'%(i+1),mesh);active.objects.link(o);o.data.materials.append(label)
 uv=mesh.uv_layers.new(name='Label wrap')
 for poly in mesh.polygons:
  j=poly.index;poly.use_smooth=True
  for li,co in zip(poly.loop_indices,[(j/N,0),((j+1)/N,0),((j+1)/N,1),(j/N,1)]):uv.data[li].uv=co
 # Sleeve graphics are aligned with the camera-facing upper surface.
 cylinder('Battery %d negative metal cap'%(i+1),(x,y1+.00035,z),r,.0007,metal,'Y',64)
 cylinder('Battery %d positive cap'%(i+1),(x,y0-.00035,z),r,.0007,metal,'Y',64)
 cylinder('Battery %d positive button'%(i+1),(x,y0-.00105,z),.0035,.001,metal,'Y',48)
 # Raised insulating rims at both ends.
 for y in [y0+.0003,y1-.0003]:
  bpy.ops.mesh.primitive_torus_add(major_segments=64,minor_segments=8,location=(x,y,z),rotation=(math.pi/2,0,0),major_radius=r-.00035,minor_radius=.00035);rim=move(bpy.context.object);rim.name='Battery %d red insulating rim'%(i+1);rim.data.materials.append(red)
 bpy.ops.object.empty_add(type='PLAIN_AXES',location=(x,(y0+y1)/2,z));root=move(bpy.context.object);root.name='HUATAI battery %d assembly'%(i+1);root.empty_display_size=.008
 for p in set(bpy.data.objects)-before:
  if p!=root:world=p.matrix_world.copy();p.parent=root;p.matrix_world=world
 root.parent=bpy.data.objects['Robot assembly • move whole robot'];root['cell_type']='Reference-style cylindrical dry cell; dimensions fitted to existing holder.'
bpy.ops.object.select_all(action='DESELECT')
for screen in bpy.data.screens:
 for area in screen.areas:
  if area.type=='VIEW_3D':area.tag_redraw()
bpy.ops.wm.save_as_mainfile(filepath=OUT+'/robot-white-room.blend')
print('Four red HUATAI batteries inserted; label texture packed into the blend file.')
