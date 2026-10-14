import bpy,os
s=bpy.context.scene
out=os.path.dirname(bpy.data.filepath)
s.render.resolution_x=960;s.render.resolution_y=810;s.eevee.taa_render_samples=24
s.render.image_settings.file_format='PNG';s.render.filepath=out+'/obstacle-course-poster.png';s.frame_set(1);bpy.ops.render.render(write_still=True)
s.render.image_settings.file_format='FFMPEG';s.render.ffmpeg.format='MPEG4';s.render.ffmpeg.codec='H264';s.render.ffmpeg.constant_rate_factor='MEDIUM';s.render.filepath=out+'/obstacle-course.mp4';bpy.ops.render.render(animation=True)
