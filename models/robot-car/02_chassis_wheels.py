active=collections['02 Chassis']
for z in [.045,.070]:
 box('Clear acrylic chassis plate',(0,0,z),(.158,.205,.003),clear,.008)
for x in [-.061,.061]:
 for y in [-.083,.083]:
  cylinder('M3 metal standoff',(x,y,.0575),.003,.025,metal)
  cylinder('Chassis screw head',(x,y,.073),.0038,.0015,metal)
  box('Screw slot',(x,y,.0739),(.005,.00065,.00015),black,0)
active=collections['03 Wheels and motors']
# Separate wheel assemblies permit future rotation and animation.
wheel_roots=[]
for side,x in [('Left',-.093),('Right',.093)]:
 for end,y in [('Front',-.065),('Rear',.065)]:
  label=side+' '+end;before=set(bpy.data.objects)
  bpy.ops.mesh.primitive_torus_add(major_segments=64,minor_segments=16,location=(x,y,.034),rotation=(0,math.pi/2,0),major_radius=.0255,minor_radius=.009);o=move(bpy.context.object);o.name=label+' rounded rubber tyre';o.data.materials.append(rubber)
  for p in o.data.polygons:p.use_smooth=True
  cylinder(label+' wheel hub',(x,y,.034),.025,.019,yellow,'X')
  # Dark cavities between five radial spokes.
  outer=x+(-.010 if x<0 else .010)
  cylinder(label+' hub recess',(outer,y,.034),.0205,.0007,black,'X')
  cylinder(label+' centre cap',(outer+(-.001 if x<0 else .001),y,.034),.007,.003,yellow,'X')
  for j in range(5):
   a=j*math.tau/5;o=box(label+' spoke '+str(j),(outer,y+math.sin(a)*.011,.034+math.cos(a)*.011),(.003,.005,.021),yellow,.001);o.rotation_euler.x=-a
  bpy.ops.mesh.primitive_torus_add(major_segments=48,minor_segments=8,location=(outer,y,.034),rotation=(0,math.pi/2,0),major_radius=.0225,minor_radius=.0025);o=move(bpy.context.object);o.name=label+' yellow rim';o.data.materials.append(yellow)
  # Build 108 tread blocks into one editable mesh.
  verts=[];faces=[]
  for row,offset in enumerate([-.006,0,.006]):
   for j in range(36):
    a=(j+(row%2)*.45)*math.tau/36;centre=Vector((x+offset,y+.034*math.sin(a),.034+.034*math.cos(a)))
    q=Quaternion((1,0,0),-a);base=len(verts)
    for v in [(-1,-1,-1),(-1,-1,1),(-1,1,-1),(-1,1,1),(1,-1,-1),(1,-1,1),(1,1,-1),(1,1,1)]:verts.append(centre+q@Vector((v[0]*.0027,v[1]*.0019,v[2]*.0008)))
    faces.extend([tuple(base+k for k in face) for face in [(0,4,6,2),(1,3,7,5),(0,1,5,4),(2,6,7,3),(0,2,3,1),(4,5,7,6)]])
  mesh=bpy.data.meshes.new(label+' tread mesh');mesh.from_pydata(verts,[],faces);mesh.update();o=bpy.data.objects.new(label+' tyre tread',mesh);active.objects.link(o);o.data.materials.append(rubber);bevel(o,.00025,2)
  bpy.ops.object.empty_add(type='PLAIN_AXES',location=(x,y,.034));root=move(bpy.context.object);root.name=label+' wheel rotation';root.empty_display_size=.015
  for o in set(bpy.data.objects)-before:
   if o!=root:world=o.matrix_world.copy();o.parent=root;o.matrix_world=world
  wheel_roots.append(root)
  box(label+' TT gearbox',(math.copysign(.050,x),y,.047),(.045,.027,.027),yellow,.003)
  cylinder(label+' motor can',(math.copysign(.020,x),y,.047),.010,.027,metal,'X')
  cylinder(label+' axle',(math.copysign(.075,x),y,.034),.002,.026,metal,'X')
bpy.ops.object.select_all(action='DESELECT')
print('Four detailed wheels, motors and acrylic chassis added.')
