"""Bake evaluated component geometry into material meshes, preserve assembly groups."""
import sys
sys.path.append("/home/watchman-admin/.local/lib/python3.10/site-packages")
import bpy,json,struct
from pathlib import Path
from mathutils import Matrix
ROOT=Path(__file__).resolve().parents[2];OUT=ROOT/'assets/assemblies';OUT.mkdir(exist_ok=True)
bpy.ops.wm.open_mainfile(filepath=str(ROOT/'models/robotics-library/robotics-library.blend'))
manifest=json.loads((ROOT/'models/robotics-library/manifest.json').read_text());web={}

def bake(objects,root,scene,transform=None):
 deps=bpy.context.evaluated_depsgraph_get();batches={}
 for obj in objects:
  if obj.type not in {'MESH','CURVE','FONT'}:continue
  ev=obj.evaluated_get(deps);mesh=bpy.data.meshes.new_from_object(ev,depsgraph=deps)
  matrix=(transform or Matrix.Identity(4)) @ obj.matrix_world
  for poly in mesh.polygons:
   m=mesh.materials[poly.material_index] if mesh.materials else bpy.data.materials['black']
   batch=batches.setdefault(m.name,{'verts':[],'faces':[],'mat':m})
   n=len(batch['verts']);batch['verts'].extend([tuple(matrix @ mesh.vertices[j].co) for j in poly.vertices]);batch['faces'].append(tuple(range(n,n+len(poly.vertices))))
  bpy.data.meshes.remove(mesh)
 for name,b in batches.items():
  d=bpy.data.meshes.new(name);d.from_pydata(b['verts'],[],b['faces']);d.materials.append(b['mat']);d.update()
  o=bpy.data.objects.new(root.name+' • '+name,d);scene.collection.objects.link(o);o.parent=root
  for f in d.polygons:f.use_smooth=True

for idx,item in enumerate(manifest['projects']):
 existing=OUT/(item['id']+'.glb')
 if existing.exists() and '--force' not in sys.argv:
  data=existing.read_bytes();length=struct.unpack_from('<I',data,12)[0];doc=json.loads(data[20:20+length]);nodes=sorted([n for n in doc['nodes'] if 'assembly_step' in n.get('extras',{})],key=lambda n:n['extras']['assembly_step']);groups=[{'label':n['extras'].get('component_id','').replace('-',' ').title() or n['name'],'component':n['extras'].get('component_id')} for n in nodes];web[item['id']]={'model':'assets/assemblies/'+item['id']+'.glb','stages':groups};continue
 source=next(s for s in bpy.data.scenes if s.get('project_id')==item['id']);bpy.context.window.scene=source;source.frame_set(1)
 assembly=bpy.data.collections['ASSEMBLY • '+item['id']]
 exp=bpy.data.scenes.new('Web export '+item['id']);groups=[]
 instances=[o for o in assembly.objects if o.instance_type=='COLLECTION']
 instances.sort(key=lambda o:0 if o.get('component_id')=='breadboard' else 1 if o.get('component_id')=='microcontroller' else 2)
 for j,o in enumerate(instances):
  root=bpy.data.objects.new(o.get('component_id'),None);exp.collection.objects.link(root);root['assembly_step']=j;root['component_id']=o.get('component_id');bake(o.instance_collection.objects,root,exp,o.matrix_world);groups.append({'label':o.get('component_id').replace('-',' ').title(),'component':o.get('component_id')})
 props=[o for o in assembly.objects if o.type in {'MESH','CURVE','FONT'}]
 wires=[o for o in props if o.name.startswith(('Jumper','Dupont'))];other=[o for o in props if o not in wires]
 for label,objs in [('Project structure',other),('Jumper connections',wires)]:
  if not objs:continue
  root=bpy.data.objects.new(label,None);exp.collection.objects.link(root);root['assembly_step']=len(groups);bake(objs,root,exp);groups.append({'label':label,'component':None})
 bpy.context.window.scene=exp;bpy.ops.object.select_all(action='SELECT')
 bpy.ops.export_scene.gltf(filepath=str(OUT/(item['id']+'.glb')),export_format='GLB',use_selection=True,export_animations=False,export_cameras=False,export_lights=False,export_extras=True,export_yup=True)
 web[item['id']]={'model':'assets/assemblies/'+item['id']+'.glb','stages':groups}
 for o in list(exp.objects):
  d=o.data;bpy.data.objects.remove(o,do_unlink=True)
  if d and d.users==0:bpy.data.meshes.remove(d)
 bpy.data.scenes.remove(exp)
 print('EXPORTED',idx+1,item['id'],flush=True)
(OUT/'index.json').write_text(json.dumps(web,indent=2))
