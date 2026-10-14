import bpy,json,math
from pathlib import Path
from mathutils import Vector
out=Path('/home/watchman-admin/Documents/tinashe/learn-robotics/models/robotics-kit')
manifest=json.loads((out/'manifest.json').read_text())
base=bpy.data.scenes['START HERE • 70 robotics parts']
for category in sorted({e['category'] for e in manifest['components']}):
    entries=[e for e in manifest['components'] if e['category']==category]
    name='BROWSE • '+category
    if bpy.data.scenes.get(name):continue
    s=bpy.data.scenes.new(name);s.world=base.world;s.unit_settings.system='METRIC';s.unit_settings.scale_length=.001
    for original in base.objects:
        if original.type in {'LIGHT','CAMERA'} or original.name.startswith('Studio ground'):
            obj=original.copy();obj.data=original.data.copy();s.collection.objects.link(obj)
            if obj.type=='CAMERA':s.camera=obj
    cols=min(4,len(entries));rows=math.ceil(len(entries)/cols)
    for i,e in enumerate(entries):
        x=(i%cols-(cols-1)/2)*155;y=((rows-1)/2-i//cols)*145
        o=bpy.data.objects.new(e['name'],None);s.collection.objects.link(o);o.instance_type='COLLECTION';o.instance_collection=bpy.data.collections['PART • '+e['id']];o.location=(x,y,0)
        d=bpy.data.curves.new(e['name'],'FONT');d.body=e['name'];d.size=6;d.align_x='CENTER';d.materials.append(bpy.data.materials['black'])
        t=bpy.data.objects.new('Label '+e['name'],d);s.collection.objects.link(t);t.location=(x,y-58,0)
    span=max(cols*155,rows*145)*1.25
    s.camera.location=(span*.25,-span*.9,span);s.camera.rotation_euler=(Vector((0,0,10))-s.camera.location).to_track_quat('-Z','Y').to_euler();s.camera.data.ortho_scale=span
    s.render.engine='BLENDER_EEVEE';s.render.resolution_x=1200;s.render.resolution_y=900
bpy.context.window.scene=bpy.data.scenes['BROWSE • Mechanisms']
for screen in bpy.data.screens:
 for area in screen.areas:
  if area.type=='VIEW_3D':area.spaces.active.region_3d.view_perspective='CAMERA';area.tag_redraw()
bpy.ops.wm.save_as_mainfile(filepath=str(out/'robotics-kit.blend'))
print('Added category browsing scenes and saved master.')
