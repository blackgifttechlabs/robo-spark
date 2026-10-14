"""Render the real Blender components with transparent backgrounds for the UI."""
import bpy,json
from pathlib import Path
root=Path(__file__).resolve().parents[2];out=root/'assets/parts-real';out.mkdir(exist_ok=True)
bpy.ops.wm.open_mainfile(filepath=str(root/'models/robotics-kit/robotics-kit.blend'))
manifest=json.loads((root/'models/robotics-kit/manifest.json').read_text())
for i,part in enumerate(manifest['components']):
 scene=next(s for s in bpy.data.scenes if s.get('component_id')==part['id']);bpy.context.window.scene=scene
 for obj in scene.objects:
  if obj.name.startswith('Studio ground'):obj.hide_render=True
 scene.render.film_transparent=True;scene.render.engine='BLENDER_EEVEE';scene.eevee.taa_render_samples=32
 scene.render.resolution_x=640;scene.render.resolution_y=480;scene.render.resolution_percentage=100;scene.render.image_settings.file_format='PNG';scene.render.image_settings.color_mode='RGBA'
 scene.render.filepath=str(out/(part['id']+'.png'));print('CUTOUT',i+1,'/70',part['id'],flush=True);bpy.ops.render.render(write_still=True)
(out/'README.md').write_text('These transparent PNGs are renders of the editable Blender kit. Rebuild with models/robotics-kit/render_cutouts.py. The ground is hidden for this render; component geometry is unchanged.\n')
print('CUTOUTS COMPLETE',flush=True)
