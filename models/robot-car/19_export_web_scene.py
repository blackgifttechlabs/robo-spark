import sys
sys.path.append("/home/watchman-admin/.local/lib/python3.10/site-packages")
for obj in list(bpy.context.scene.objects):
 if "web label" in obj.name or "web mesh" in obj.name:bpy.data.objects.remove(obj,do_unlink=True)
if bpy.context.screen.is_animation_playing:bpy.ops.screen.animation_play()
scene.frame_set(1)
# Keep the native renderable originals intact; export the evaluated batches.
export_objects=[master]+wheel_roots+blocks
for key in ['02 Chassis','03 Wheels and motors','04 Arduino electronics','05 Battery holder','06 Ultrasonic sensor','07 Wiring']:
 export_objects.extend(o for o in collections[key].objects if o.type in {'MESH','EMPTY'})
export_objects += [bpy.data.objects[n] for n in ['White floor','White back wall','White left wall','White right wall']]
export_objects=list(dict.fromkeys(export_objects))
labels=[]
for obj in list(scene.objects):
 is_label=obj.name in ['Block %d number'%i for i in range(1,4)]
 is_robot_curve=obj.type in {'CURVE','FONT'} and any(obj.name in collections[key].objects for key in ['02 Chassis','03 Wheels and motors','04 Arduino electronics','05 Battery holder','06 Ultrasonic sensor','07 Wiring'])
 if not (is_label or is_robot_curve):continue
 ev=obj.evaluated_get(bpy.context.evaluated_depsgraph_get());mesh=bpy.data.meshes.new_from_object(ev);copy=bpy.data.objects.new(obj.name+' web mesh',mesh);scene.collection.objects.link(copy)
 copy.parent=obj.parent;copy.matrix_parent_inverse=obj.matrix_parent_inverse.copy();copy.matrix_basis=obj.matrix_basis.copy();labels.append(copy);export_objects.append(copy)
bpy.ops.object.select_all(action='DESELECT')
for o in export_objects:o.hide_set(False);o.select_set(True)
bpy.context.view_layer.objects.active=master
print('glTF options', [p.identifier for p in bpy.ops.export_scene.gltf.get_rna_type().properties if 'animation' in p.identifier or 'nla' in p.identifier])
bpy.ops.export_scene.gltf(filepath='/home/watchman-admin/Documents/tinashe/learn-robotics/assets/scene/robot-course.glb',export_format='GLB',use_selection=True,export_animations=True,export_nla_strips=False,export_frame_range=True,export_force_sampling=True,export_cameras=False,export_lights=False,export_yup=True,export_apply=True)
for o in labels:bpy.data.objects.remove(o,do_unlink=True)
bpy.ops.object.select_all(action='DESELECT')
bpy.ops.wm.save_as_mainfile(filepath=OUT+'/robot-white-room.blend')
meta={'duration':scene.frame_end/scene.render.fps,'fps':scene.render.fps,'frames':scene.frame_end,'detect':[]}
for i in range(1,4):
 frame=next(m.frame for m in scene.timeline_markers if m.name.startswith('DETECT BLOCK %d'%i));meta['detect'].append({'start':(frame-1)/24,'end':(frame+17)/24,'block':i})
open('/home/watchman-admin/Documents/tinashe/learn-robotics/assets/scene/animation.json','w').write(json.dumps(meta,indent=2))
print('Animated web GLB exported with white plastic chassis.')
