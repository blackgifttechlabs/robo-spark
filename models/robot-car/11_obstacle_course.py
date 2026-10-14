import math,json
from mathutils import Vector
master=bpy.data.objects['Robot assembly • move whole robot']
# Expand the white room without altering the robot's size.
for name,size,loc in [
 ('White floor',(6,6,.016),(0,0,-.009)),
 ('White back wall',(6,.025,2.4),(0,2.2,1.2)),
 ('White left wall',(.025,4.4,2.4),(-2.2,0,1.2)),
 ('White right wall',(.025,4.4,2.4),(2.2,0,1.2))]:
 o=bpy.data.objects[name];o.dimensions=size;o.location=loc
scene.world.node_tree.nodes['Background'].inputs[1].default_value=.8
# Broad overhead softboxes keep the whole course evenly lit.
for name,loc,energy,size in [('Large softbox',(-1,-.5,2.4),150,2.5),('Soft fill',(1,-1,1.8),80,2),('Back edge light',(0,1.5,2),100,2)]:
 o=bpy.data.objects[name];o.location=loc;o.data.energy=energy;o.data.size=size;o.rotation_euler=(Vector((0,-.1,0))-o.location).to_track_quat('-Z','Y').to_euler()
active=bpy.data.collections.get('09 Obstacle course')
if not active:
 active=bpy.data.collections.new('09 Obstacle course');scene.collection.children.link(active)
blockmat=material('Warm timber obstacle blocks',(.40,.20,.08),rough=.65)
# Subtle procedural timber grain.
nt=blockmat.node_tree;p=nt.nodes['Principled BSDF'];noise=nt.nodes.new('ShaderNodeTexNoise');noise.inputs['Scale'].default_value=7;noise.inputs['Detail'].default_value=3;mapping=nt.nodes.new('ShaderNodeVectorMath');mapping.operation='MULTIPLY';mapping.inputs[1].default_value=(5,1,30);coords=nt.nodes.new('ShaderNodeTexCoord');nt.links.new(coords.outputs['Generated'],mapping.inputs[0]);nt.links.new(mapping.outputs[0],noise.inputs['Vector']);ramp=nt.nodes.new('ShaderNodeValToRGB');ramp.color_ramp.elements[0].color=(.20,.08,.025,1);ramp.color_ramp.elements[1].color=(.63,.35,.14,1);nt.links.new(noise.outputs['Fac'],ramp.inputs[0]);nt.links.new(ramp.outputs['Color'],p.inputs['Base Color'])
block_positions=[(0,.65),(.42,-.15),(-.42,-.95)]
blocks=[]
for i,(x,y) in enumerate(block_positions,1):
 o=box('Obstacle block %d'%i,(x,y,.10),(.20,.20,.20),blockmat,.007);blocks.append(o)
 text('Block %d number'%i,str(i),(x,y,.201),.055,ink)
# Sensor indicator is a restrained cyan beam, shown only during detection pauses.
scanmat=material('Sensor detection cyan',(.01,.52,.65),rough=.3)
p=scanmat.node_tree.nodes['Principled BSDF'];p.inputs['Emission'].default_value=(.01,.35,.5,1);p.inputs['Emission Strength'].default_value=.4
scan=curve('Ultrasonic detection indicator',[(0,-.13,.097),(0,-.31,.097)],.0016,scanmat);scan.parent=master
# Course camera remains fixed so the three blocks and path changes are visible.
camera.location=(2.6,-3.8,3.4);target=Vector((0,-.10,.04));camera.rotation_euler=(target-camera.location).to_track_quat('-Z','Y').to_euler();camera.data.ortho_scale=3.65;scene.camera=camera
scene.render.resolution_x=1280;scene.render.resolution_y=1080;scene.render.resolution_percentage=100
scene.render.fps=24
# Rounded corners: straight segments and quadratic curves, sampled by arc length.
way=[Vector(v) for v in [(0,1.25),(0,1.04),(.42,1.04),(.42,.25),(-.42,.25),(-.42,-.55),(.42,-.55),(.42,-1.45)]]
route=[way[0]];stops=[]
for i in range(1,len(way)-1):
 prev,point,nxt=way[i-1],way[i],way[i+1];r=.11
 a=point+(prev-point).normalized()*r;b=point+(nxt-point).normalized()*r
 route.append(a)
 if i in [1,3,5]:stops.append(len(route)-1)
 for j in range(1,25):
  u=j/24;route.append((1-u)**2*a+2*(1-u)*u*point+u*u*b)
route.append(way[-1])
arc=[0]
for a,b in zip(route,route[1:]):arc.append(arc[-1]+(b-a).length)
stop_dist=[arc[i] for i in stops]
# Add 0.75 second stops while the sensor faces each block.
speed=.25;fps=24;pause_frames=18;poses=[];dist=0;next_stop=0;seg=0
while dist<arc[-1]-1e-8:
 if next_stop<len(stop_dist) and dist>=stop_dist[next_stop]-1e-8:
  for j in range(pause_frames):poses.append((dist,next_stop+1))
  next_stop+=1
 next_dist=min(arc[-1],dist+speed/fps)
 if next_stop<len(stop_dist):next_dist=min(next_dist,stop_dist[next_stop])
 poses.append((dist,0));dist=next_dist
poses.append((arc[-1],0))
for j in range(24):poses.append((arc[-1],0))
master.animation_data_clear()
for root in wheel_roots:root.animation_data_clear();root.rotation_mode='XYZ'
scene.frame_start=1;scene.frame_end=len(poses)
leftangle=rightangle=0;lastpos=None;lasttheta=None;seg=0;clearances=[]
def overlap_robot_block(pos,theta,block,margin=.018):
 # Separating-axis test against a conservative footprint expanded by margin.
 c=math.cos(theta);sn=math.sin(theta);ux=Vector((c,sn));uy=Vector((-sn,c));delta=Vector(block)-pos
 for axis in [ux,uy,Vector((1,0)),Vector((0,1))]:
  r_robot=(.116+margin)*abs(axis.dot(ux))+(.132+margin)*abs(axis.dot(uy));r_block=.10*(abs(axis.x)+abs(axis.y))
  if abs(delta.dot(axis))>r_robot+r_block:return False
 return True
for f,(d,detect) in enumerate(poses,1):
 while seg<len(arc)-2 and arc[seg+1]<d:seg+=1
 fraction=(d-arc[seg])/max(1e-9,arc[seg+1]-arc[seg]);pos=route[seg].lerp(route[seg+1],fraction)
 direction=(route[seg+1]-route[seg]).normalized();theta=math.atan2(direction.x,-direction.y)
 if lasttheta is not None:
  while theta-lasttheta>math.pi:theta-=math.tau
  while theta-lasttheta< -math.pi:theta+=math.tau
  ds=(pos-lastpos).length;turn=theta-lasttheta;leftangle+=(ds+.093*turn)/.0348;rightangle+=(ds-.093*turn)/.0348
 master.location=(pos.x,pos.y,0);master.rotation_mode='XYZ';master.rotation_euler=(0,0,theta);master.keyframe_insert('location',frame=f);master.keyframe_insert('rotation_euler',frame=f)
 for root in wheel_roots:
  root.rotation_euler.x=leftangle if root.name.startswith('Left') else rightangle;root.keyframe_insert('rotation_euler',frame=f)
 scan.hide_render=not bool(detect);scan.hide_viewport=not bool(detect);scan.keyframe_insert('hide_render',frame=f);scan.keyframe_insert('hide_viewport',frame=f)
 for block in block_positions:assert not overlap_robot_block(pos,theta,block),(f,tuple(pos),theta,block)
 lastpos=pos;lasttheta=theta
for o in [master]+wheel_roots:
 o.animation_data.action.name=o.name+' | obstacle avoidance'
 for fc in o.animation_data.action.fcurves:
  for k in fc.keyframe_points:k.interpolation='LINEAR'
for fc in scan.animation_data.action.fcurves:
 for k in fc.keyframe_points:k.interpolation='CONSTANT'
scene.timeline_markers.clear()
scene.timeline_markers.new('START — drive forward',frame=1)
for n in range(1,4):
 frames=[i+1 for i,p in enumerate(poses) if p[1]==n];scene.timeline_markers.new('DETECT BLOCK %d — stop and steer'%n,frame=frames[0])
scene.timeline_markers.new('CLEAR — all three blocks avoided',frame=len(poses)-24)
scene['animation_notes']='Choreographed three-obstacle avoidance. Cyan sensor indicator during 0.75-second stops. Wheel rotation follows path distance plus differential steering. Not an autonomous physics/sensor simulation.'
scene.frame_set(1)
for screen in bpy.data.screens:
 for area in screen.areas:
  if area.type=='VIEW_3D':area.spaces.active.region_3d.view_perspective='CAMERA';area.spaces.active.region_3d.view_camera_zoom=10;area.spaces.active.overlay.show_overlays=False;area.tag_redraw()
scene.render.filepath=OUT+'/obstacle-course.mp4';scene.render.image_settings.file_format='FFMPEG';scene.render.ffmpeg.format='MPEG4';scene.render.ffmpeg.codec='H264';scene.render.ffmpeg.constant_rate_factor='MEDIUM'
bpy.ops.wm.save_as_mainfile(filepath=OUT+'/robot-white-room.blend')
report={'frames':scene.frame_end,'fps':fps,'duration_seconds':round(scene.frame_end/fps,2),'path_length_m':round(arc[-1],3),'blocks':3,'collision_check':'All frames clear of all three blocks, including an 18 mm safety margin.','wheel_rotation':'Distance / 34.8 mm rolling radius, with differential steering at 186 mm track width.'}
open(OUT+'/animation-validation.json','w').write(json.dumps(report,indent=2));print(report)
