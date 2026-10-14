# Simplified transparent acrylic without dynamic screen-space refraction.
clear.blend_method='BLEND';clear.shadow_method='NONE';p=clear.node_tree.nodes['Principled BSDF'];p.inputs['Alpha'].default_value=.13;p.inputs['Transmission'].default_value=0
scene['quality_notes']='Normal neutral studio lighting; 1920px, 128-sample renders. Screen-space reflection/refraction disabled. Thin alpha acrylic with no refraction. Combined viewport-only meshes reduce draw calls; source components remain editable and render at full quality.'
# Batch static evaluated geometry into five viewport-only meshes, retaining
# original component geometry for editing and full-quality rendering.
preview=bpy.data.collections.new('10 Fast animation preview — viewport only');scene.collection.children.link(preview)
scene.frame_set(145);deps=bpy.context.evaluated_depsgraph_get();deps.update()
sources=[o for key in ['02 Chassis','03 Wheels and motors','04 Arduino electronics','05 Battery holder','06 Ultrasonic sensor','07 Wiring'] for o in collections[key].objects if o.type in {'MESH','CURVE','FONT'}]
def wheel_parent(o):
 p=o.parent
 while p:
  if p in wheel_roots:return p
  p=p.parent
 return None
groups={master:[]}
for r in wheel_roots:groups[r]=[]
for o in sources:groups[wheel_parent(o) or master].append(o)
for parent,objects in groups.items():
 verts=[];faces=[];materials=[];matindex=[];smooth=[];uvs=[];normals=[]
 for o in objects:
  ev=o.evaluated_get(deps);m=ev.to_mesh(preserve_all_data_layers=True,depsgraph=deps)
  if m is None:continue
  transform=parent.matrix_world.inverted()@o.matrix_world;normaltransform=transform.to_3x3().inverted().transposed();base=len(verts);verts.extend(transform@v.co for v in m.vertices);m.calc_normals_split()
  remap=[]
  for mat in m.materials:
   if mat not in materials:materials.append(mat)
   remap.append(materials.index(mat))
  layer=m.uv_layers.active
  for poly in m.polygons:
   faces.append(tuple(base+v for v in poly.vertices));matindex.append(remap[poly.material_index] if remap else 0);smooth.append(poly.use_smooth)
   for li in poly.loop_indices:
    uvs.append(tuple(layer.data[li].uv) if layer else (0,0));normals.append((normaltransform@m.loops[li].normal).normalized())
  ev.to_mesh_clear()
 mesh=bpy.data.meshes.new(parent.name+' preview mesh');mesh.from_pydata(verts,[],faces);mesh.update()
 for mat in materials:mesh.materials.append(mat)
 for poly,mi,sm in zip(mesh.polygons,matindex,smooth):poly.material_index=mi;poly.use_smooth=sm
 layer=mesh.uv_layers.new(name='Preserved labels')
 for loop,uv in zip(layer.data,uvs):loop.uv=uv
 mesh.use_auto_smooth=True;mesh.normals_split_custom_set(normals)
 o=bpy.data.objects.new(parent.name+' • fast viewport geometry',mesh);preview.objects.link(o);o.parent=parent;o.hide_render=True
for o in sources:o.hide_set(True)
scene.frame_set(1)
for screen in bpy.data.screens:
 for area in screen.areas:
  if area.type=='VIEW_3D':area.spaces.active.shading.type='MATERIAL';area.spaces.active.shading.use_scene_lights=True;area.spaces.active.shading.use_scene_world=True;area.tag_redraw()
bpy.ops.wm.save_as_mainfile(filepath=OUT+'/robot-white-room.blend')
print('Viewport batches:',len(groups),'instead of',len(sources),'separate component draws; original parts preserved for rendering and editing.')
if not bpy.context.screen.is_animation_playing:bpy.ops.screen.animation_play()
