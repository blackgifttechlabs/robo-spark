"""Check the kit, export real mesh GLBs and render Blender thumbnails."""
import sys
sys.path.append('/home/watchman-admin/.local/lib/python3.10/site-packages')
import bpy,json,struct,math
from pathlib import Path
from mathutils import Vector
OUT=Path(__file__).resolve().parent
bpy.ops.wm.open_mainfile(filepath=str(OUT/'robotics-kit.blend'))
manifest=json.loads((OUT/'manifest.json').read_text())
# Blender 3.0's exporter traverses every scene even for a selection export.
# Limit gathering to the disposable export scene to avoid unrelated library scenes.
from io_scene_gltf2.blender.exp import gltf2_blender_gather
_original_gather=gltf2_blender_gather.gather_gltf2
def gather_active(settings):
 return 0,[gltf2_blender_gather.__gather_scene(bpy.context.scene,settings)],[]
gltf2_blender_gather.gather_gltf2=gather_active
errors=[];results=[]
assert len(manifest['components'])==70
assert len({e['id'] for e in manifest['components']})==70
for e in manifest['components']:
 c=bpy.data.collections.get('PART • '+e['id'])
 if not c or not c.asset_data or not c.objects:errors.append('Missing editable marked collection '+e['id'])
 if not (OUT/e['blend']).exists():errors.append('Missing blend '+e['id'])
assert not errors,errors
for i,e in enumerate(manifest['components']):
 c=bpy.data.collections['PART • '+e['id']]
 source=next(s for s in bpy.data.scenes if s.get('component_id')==e['id'])
 bpy.context.window.scene=source;bpy.context.view_layer.update()
 # Export evaluated geometry, including curves and text. Keep named subparts.
 deps=bpy.context.evaluated_depsgraph_get();exp=bpy.data.scenes.new('EXPORT '+e['id'])
 batches={}
 moving=('Moving switch','Thumb cap','Joystick stalk','Fan blade','Fan motor hub','Output spline','Double arm','Servo horn','Moving finger','Parallel linkage','Rubber gripping','Scissor arm','Lift platform','Central pivot','Roller','Gear web','Gear tooth','Gear hub','Pinion','Pen barrel','Pen tip','Rotating shaft','Knurled knob','Track roller','Rubber tread','Curved end tread','Top conveyor','Belt surface')
 for o in c.objects:
  if o.type not in {'MESH','CURVE','FONT'}:continue
  mesh=bpy.data.meshes.new_from_object(o.evaluated_get(deps),depsgraph=deps)
  # Batch static geometry by material; keep moving subparts in named groups.
  group=o.name if o.name.startswith(moving) else 'Static body'
  for poly in mesh.polygons:
   material=mesh.materials[poly.material_index] if mesh.materials else bpy.data.materials['black']
   bucket=batches.setdefault((group,material.name),{'vertices':[],'faces':[],'smooth':[],'mat':material,'names':set()})
   n=len(bucket['vertices'])
   bucket['vertices'].extend([tuple(o.matrix_world @ mesh.vertices[j].co) for j in poly.vertices])
   bucket['faces'].append(tuple(range(n,n+len(poly.vertices))))
   bucket['smooth'].append(poly.use_smooth);bucket['names'].add(o.name)
  bpy.data.meshes.remove(mesh)
 for (group,material),bucket in batches.items():
  mesh=bpy.data.meshes.new(group+' • '+material);mesh.from_pydata(bucket['vertices'],[],bucket['faces']);mesh.materials.append(bucket['mat']);mesh.update()
  for f,smooth in zip(mesh.polygons,bucket['smooth']):f.use_smooth=smooth
  baked=bpy.data.objects.new(group+' • '+material,mesh);exp.collection.objects.link(baked)
  baked['part_id']=e['id'];baked['source_objects']=json.dumps(sorted(bucket['names']))
 bpy.context.window.scene=exp
 bpy.ops.object.select_all(action='SELECT')
 path=OUT/'web'/(e['id']+'.glb')
 bpy.ops.export_scene.gltf(filepath=str(path),export_format='GLB',use_selection=True,export_animations=False,export_cameras=False,export_lights=False,export_extras=True)
 data=path.read_bytes();assert data[:4]==b'glTF'
 length=struct.unpack_from('<I',data,12)[0];doc=json.loads(data[20:20+length])
 assert doc.get('meshes') and doc.get('materials'),e['id']
 results.append({'id':e['id'],'meshes':len(doc['meshes']),'bytes':len(data)})
 e['web']='web/'+e['id']+'.glb';e['preview']='previews/'+e['id']+'.png'
 for o in list(exp.objects):
  mesh=o.data;bpy.data.objects.remove(o,do_unlink=True)
  if mesh.users==0:bpy.data.meshes.remove(mesh)
 bpy.data.scenes.remove(exp);bpy.context.window.scene=source
 print('EXPORT',i+1,'/70',e['id'],flush=True)
(OUT/'manifest.json').write_text(json.dumps(manifest,indent=2))
(OUT/'validation.json').write_text(json.dumps({'parts':70,'unique_ids':True,'editable_asset_collections':70,'standalone_blend_files':70,'web_exports':results,'errors':errors,'limits':'Visual models; no manufacturing or electrical validation'},indent=2))
# Produce contact-sheet source renders using studio lighting and actual materials.
scenes=[bpy.data.scenes['START HERE • 70 robotics parts']]+[next(s for s in bpy.data.scenes if s.get('component_id')==e['id']) for e in manifest['components']]
for i,s in enumerate(scenes):
 bpy.context.window.scene=s
 s.render.engine='BLENDER_EEVEE';s.eevee.taa_render_samples=16
 s.render.resolution_x=1600 if i==0 else 320;s.render.resolution_y=1200 if i==0 else 240;s.render.resolution_percentage=100
 s.render.image_settings.file_format='PNG';s.render.filepath=str(OUT/'previews'/((s.get('component_id') or 'kit-overview')+'.png'))
 print('RENDER',i,'/70',s.name,flush=True);bpy.ops.render.render(write_still=True)
(OUT/'previews-complete.json').write_text(json.dumps({'renders':71}))
print('VALIDATED AND EXPORTED 70 PARTS, RENDERED 71 PREVIEWS',flush=True)
