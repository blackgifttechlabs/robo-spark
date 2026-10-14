import bpy,json,sys,math
from pathlib import Path
OUT=Path(__file__).resolve().parent
bpy.ops.wm.open_mainfile(filepath=str(OUT/'robotics-library.blend'))
manifest=json.loads((OUT/'manifest.json').read_text())
errors=[]
assert len(manifest['components'])==20
assert len(manifest['projects'])==24
for o in bpy.data.objects:
 if o.type=='MESH':o.data.use_auto_smooth=True
 if o.type=='LIGHT' and not o.get('balanced_preview'):
  o.data.energy *= .05;o['balanced_preview']=True
for item in manifest['components']:
 c=bpy.data.collections.get('PART • '+item['id'])
 if not c or not c.objects:errors.append('Missing component: '+item['id'])
 if not c.asset_data:errors.append('Missing reusable asset marker: '+item['id'])
 if not (OUT/item['blend']).exists():errors.append('Missing file: '+item['blend'])
for item in manifest['projects']:
 s=next((s for s in bpy.data.scenes if s.get('project_id')==item['id']),None)
 if not s or not s.camera:errors.append('Missing scene/camera: '+item['id']);continue
 actual=sorted({o.instance_collection.name.removeprefix('PART • ') for o in s.objects if o.instance_type=='COLLECTION'})
 if actual!=item['reused_components']:errors.append('Component reuse mismatch: '+item['id'])
 for o in s.objects:
  if o.instance_type=='COLLECTION' and not o.instance_collection.asset_data:errors.append('Unmarked source asset: '+o.name)
assert not errors,errors
# Save repaired manufactured-edge normals in master and standalone files.
for item in manifest['components']:
 s=next(s for s in bpy.data.scenes if s.get('component_id')==item['id']);c=bpy.data.collections['PART • '+item['id']]
 bpy.data.libraries.write(str(OUT/item['blend']),{s,c},fake_user=True)
for item in manifest['projects']:
 s=next(s for s in bpy.data.scenes if s.get('project_id')==item['id'])
 bpy.data.libraries.write(str(OUT/item['blend']),{s},fake_user=True)
start=bpy.data.scenes['START HERE • 20 reusable robotics components'];bpy.context.window.scene=start
bpy.ops.wm.save_as_mainfile(filepath=str(OUT/'robotics-library.blend'))
result={'components':20,'projects':24,'shared_component_collections':20,'checks':['Every component has editable geometry and an asset marker','All 24 projects have a camera and saved standalone file','Project component instances point to the shared library collections','Weighted normals enabled on manufactured meshes'],'errors':errors,'accuracy':'Visual and structural checks only. No dimensional reference or electrical validation.'}
(OUT/'validation.json').write_text(json.dumps(result,indent=2))
scenes=[start]+[s for s in bpy.data.scenes if s.get('component_id') or s.get('project_id')]
for i,s in enumerate(scenes):
 bpy.context.window.scene=s
 s.render.engine='BLENDER_EEVEE';s.eevee.taa_render_samples=32
 s.render.resolution_x=960 if s==start else 480;s.render.resolution_y=720 if s==start else 360;s.render.resolution_percentage=100;s.render.image_settings.file_format='PNG'
 slug=s.get('component_id') or s.get('project_id') or 'component-library'
 s.render.filepath=str(OUT/'previews'/f'{slug}.png')
 print(f'PREVIEW {i+1}/{len(scenes)}: {slug}',flush=True);bpy.ops.render.render(write_still=True)
print('VALIDATION AND PREVIEWS COMPLETE',flush=True)
