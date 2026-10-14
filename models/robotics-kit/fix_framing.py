import bpy,json,math,bmesh
from pathlib import Path
from mathutils import Vector
out=Path('/home/watchman-admin/Documents/tinashe/learn-robotics/models/robotics-kit')
m=json.loads((out/'manifest.json').read_text())
c=bpy.data.collections['PART • beam']
for o in list(c.objects):bpy.data.objects.remove(o,do_unlink=True)
verts=[];faces=[];n=32
for cx in range(-45,46,10):
 start=len(verts)
 for z in [.5,5.5]:
  for inner in [False,True]:
   for i in range(n):
    a=i*math.tau/n;co=math.cos(a);si=math.sin(a);r=2.5 if inner else min(5/max(abs(co),1e-9),7.5/max(abs(si),1e-9))
    verts.append((cx+r*co,r*si,z))
 for i in range(n):
  j=(i+1)%n
  for a,b in [(0,1),(2,3),(0,2),(1,3)]:faces.append((start+a*n+i,start+a*n+j,start+b*n+j,start+b*n+i))
mesh=bpy.data.meshes.new('Beam with ten real through bores');mesh.from_pydata(verts,[],faces);mesh.update()
bm=bmesh.new();bm.from_mesh(mesh);bmesh.ops.remove_doubles(bm,verts=list(bm.verts),dist=.001);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(mesh);bm.free()
o=bpy.data.objects.new('Perforated aluminium beam',mesh);c.objects.link(o);mesh.materials.append(bpy.data.materials['aluminium']);o['part_id']='beam'
for e in m['components']:
 c=bpy.data.collections['PART • '+e['id']];s=next(s for s in bpy.data.scenes if s.get('component_id')==e['id'])
 bpy.context.window.scene=s;bpy.context.view_layer.update();deps=bpy.context.evaluated_depsgraph_get()
 pts=[o.evaluated_get(deps).matrix_world @ Vector(corner) for o in c.objects for corner in o.evaluated_get(deps).bound_box]
 lo=Vector(tuple(min(p[i] for p in pts) for i in range(3)));hi=Vector(tuple(max(p[i] for p in pts) for i in range(3)));center=(lo+hi)/2
 direction=Vector((.7,-1,.9)).normalized();s.camera.location=center+direction*max(hi-lo)*3;s.camera.rotation_euler=(-direction).to_track_quat('-Z','Y').to_euler()
 rot=s.camera.rotation_euler.to_matrix().transposed();projected=[rot@(p-center) for p in pts]
 width=max(p.x for p in projected)-min(p.x for p in projected);height=max(p.y for p in projected)-min(p.y for p in projected)
 s.camera.data.ortho_scale=max(width,height*s.render.resolution_x/s.render.resolution_y)*1.22
 target=out/'components'/(e['id']+'.blend');bpy.data.libraries.write(str(target),{s,c},fake_user=True)
 e['blend']='components/'+e['id']+'.blend';e['objects']=len(c.objects)
(out/'manifest.json').write_text(json.dumps(m,indent=2))
bpy.context.window.scene=bpy.data.scenes['BROWSE • Mechanisms'];bpy.ops.wm.save_as_mainfile(filepath=str(out/'robotics-kit.blend'))
print('Rebuilt beam with explicit through-hole mesh; fitted all 70 cameras; saved 70 standalone files.')
