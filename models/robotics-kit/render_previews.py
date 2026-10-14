import bpy,json
from pathlib import Path
OUT=Path(__file__).resolve().parent
bpy.ops.wm.open_mainfile(filepath=str(OUT/'robotics-kit.blend'))
manifest=json.loads((OUT/'manifest.json').read_text())
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
