# Recreate the complete robot and obstacle-course scene in a single execution.
import bpy
# Preserve the prior model scene as an archive while freeing names for the rebuild.
old=bpy.data.scenes.get('Robot • White Studio')
if old:
 if bpy.context.screen and bpy.context.screen.is_animation_playing:bpy.ops.screen.animation_play()
 old.name='Archived previous robot'
 oldmaterials=set()
 for o in list(old.objects):
  if hasattr(o.data,'materials'):oldmaterials.update(m for m in o.data.materials if m)
  o.name='Archived • '+o.name
 for c in old.collection.children:c.name='Archived • '+c.name
 for m in oldmaterials:m.name='Archived • '+m.name
bpy.app.driver_namespace.pop('robot_build',None)
# 01_studio.py
import bpy, math, os
from mathutils import Vector, Quaternion
OUT = '/home/watchman-admin/Documents/tinashe/learn-robotics/models/robot-car'
scene = bpy.data.scenes.get('Robot • White Studio')
if scene is None:
    scene = bpy.data.scenes.new('Robot • White Studio')
bpy.context.window.scene = scene
scene.unit_settings.system = 'METRIC'
scene.unit_settings.scale_length = 1
scene.render.engine = 'BLENDER_EEVEE'
scene.eevee.taa_render_samples = 64
scene.eevee.use_gtao = True
scene.eevee.gtao_distance = 0.2
scene.eevee.gtao_factor = 1.3
scene.eevee.use_soft_shadows = True
scene.eevee.use_ssr = True
scene.eevee.use_ssr_refraction = True
scene.render.resolution_x = 1600
scene.render.resolution_y = 1200
scene.render.resolution_percentage = 100
scene.world = bpy.data.worlds.new('White studio environment')
scene.world.use_nodes = True
scene.world.node_tree.nodes['Background'].inputs[0].default_value = (0.8, 0.8, 0.8, 1)
scene.world.node_tree.nodes['Background'].inputs[1].default_value = 0.7
scene.view_settings.view_transform = 'Standard'
scene.view_settings.look = 'None'
scene.view_settings.exposure = 0
collections = {}
for name in ['01 White room', '02 Chassis', '03 Wheels and motors', '04 Arduino electronics', '05 Battery holder', '06 Ultrasonic sensor', '07 Wiring', '08 Cameras and lighting']:
    c = bpy.data.collections.new(name)
    scene.collection.children.link(c)
    collections[name] = c
active = collections['01 White room']

def move(o):
    for c in list(o.users_collection):
        c.objects.unlink(o)
    active.objects.link(o)
    return o

def material(name, c, metal=0, rough=0.4):
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    p = m.node_tree.nodes.get('Principled BSDF')
    p.inputs['Base Color'].default_value = (*c, 1)
    p.inputs['Metallic'].default_value = metal
    p.inputs['Roughness'].default_value = rough
    return m
white = material('White studio matte', (0.92, 0.92, 0.92), rough=0.78)
rubber = material('Black molded tyre rubber', (0.018, 0.021, 0.025), rough=0.72)
yellow = material('Yellow injection molded ABS', (0.98, 0.66, 0.014), rough=0.3)
black = material('Black electronics plastic', (0.018, 0.022, 0.028), rough=0.4)
metal = material('Machined aluminium', (0.65, 0.7, 0.73), 0.8, 0.24)
gold = material('Gold plated pins', (0.74, 0.49, 0.12), 0.75, 0.27)
blue = material('Blue solder mask', (0.016, 0.23, 0.38), 0.1, 0.36)
ink = material('White silkscreen', (0.94, 0.96, 0.98), rough=0.65)
red = material('Red insulated wire', (0.62, 0.008, 0.018), rough=0.35)
wireblue = material('Blue insulated wire', (0.006, 0.19, 0.6), rough=0.35)
wireyellow = material('Yellow insulated wire', (0.95, 0.6, 0.01), rough=0.35)
clear = material('Clear acrylic', (0.83, 0.96, 1), rough=0.08)
p = clear.node_tree.nodes['Principled BSDF']
p.inputs['Transmission'].default_value = 1
p.inputs['IOR'].default_value = 1.46
p.inputs['Alpha'].default_value = 0.28
clear.blend_method = 'BLEND'
clear.use_screen_refraction = True
clear.show_transparent_back = False

def bevel(o, width=0.001, segments=3):
    b = o.modifiers.new('Manufactured edge radius', 'BEVEL')
    b.width = width
    b.segments = segments
    o.data.use_auto_smooth = True
    o.modifiers.new('Weighted normals', 'WEIGHTED_NORMAL')
    return o

def box(name, loc, size, mat, r=0.001):
    bpy.ops.mesh.primitive_cube_add(size=1, location=loc)
    o = move(bpy.context.object)
    o.name = name
    o.scale = size
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    o.data.materials.append(mat)
    if r:
        bevel(o, r)
    return o

def cylinder(name, loc, radius, depth, mat, axis='Z', vertices=48):
    bpy.ops.mesh.primitive_cylinder_add(vertices=vertices, radius=radius, depth=depth, location=loc)
    o = move(bpy.context.object)
    o.name = name
    o.rotation_euler = Vector({'X': (1, 0, 0), 'Y': (0, 1, 0), 'Z': (0, 0, 1)}[axis]).to_track_quat('Z', 'Y').to_euler()
    o.data.materials.append(mat)
    for p in o.data.polygons:
        p.use_smooth = True
    bevel(o, min(0.0005, depth / 5), 2)
    return o

def sphere(name, loc, size, mat):
    bpy.ops.mesh.primitive_uv_sphere_add(segments=24, ring_count=12, location=loc)
    o = move(bpy.context.object)
    o.name = name
    o.scale = size
    o.data.materials.append(mat)
    for p in o.data.polygons:
        p.use_smooth = True
    return o

def curve(name, points, r, mat):
    c = bpy.data.curves.new(name, 'CURVE')
    c.dimensions = '3D'
    c.resolution_u = 16
    c.bevel_depth = r
    c.bevel_resolution = 3
    sp = c.splines.new('BEZIER')
    sp.bezier_points.add(len(points) - 1)
    for (p, co) in zip(sp.bezier_points, points):
        p.co = co
        p.handle_left_type = 'AUTO'
        p.handle_right_type = 'AUTO'
    o = bpy.data.objects.new(name, c)
    active.objects.link(o)
    o.data.materials.append(mat)
    return o

def text(name, body, loc, size, mat, rotation=None):
    c = bpy.data.curves.new(name, 'FONT')
    c.body = body
    c.size = size
    c.extrude = 1.5e-05
    c.align_x = 'CENTER'
    o = bpy.data.objects.new(name, c)
    active.objects.link(o)
    o.location = loc
    o.data.materials.append(mat)
    if rotation:
        o.rotation_euler = rotation
    return o
box('White floor', (0, 0, -0.009), (3, 3, 0.016), white, 0.006)
box('White back wall', (0, 0.65, 0.5), (3, 0.025, 1), white, 0.02)
box('White left wall', (-0.75, 0, 0.5), (0.025, 1.3, 1), white, 0.02)
box('White right wall', (0.75, 0, 0.5), (0.025, 1.3, 1), white, 0.02)
active = collections['08 Cameras and lighting']

def light(name, loc, power, size):
    bpy.ops.object.light_add(type='AREA', location=loc)
    o = move(bpy.context.object)
    o.name = name
    o.data.energy = power
    o.data.size = size
    o.rotation_euler = (Vector((0, 0, 0.06)) - o.location).to_track_quat('-Z', 'Y').to_euler()
light('Large softbox', (-0.35, -0.35, 0.55), 12, 0.45)
light('Soft fill', (0.35, -0.15, 0.35), 7, 0.35)
light('Back edge light', (0.05, 0.35, 0.5), 10, 0.3)
bpy.ops.object.camera_add(location=(0.36, -0.43, 0.3))
camera = move(bpy.context.object)
camera.name = 'Hero camera'
camera.rotation_euler = (Vector((0, 0, 0.065)) - camera.location).to_track_quat('-Z', 'Y').to_euler()
camera.data.type = 'ORTHO'
camera.data.ortho_scale = 0.43
camera.data.lens = 70
camera.data.clip_start = 0.001
scene.camera = camera
for screen in bpy.data.screens:
    for area in screen.areas:
        if area.type == 'VIEW_3D':
            area.spaces.active.region_3d.view_perspective = 'CAMERA'
            area.spaces.active.clip_start = 0.001
            area.spaces.active.shading.type = 'MATERIAL'
            area.spaces.active.shading.use_scene_world = True
            area.spaces.active.shading.use_scene_lights = True
namespace = {k: v for (k, v) in locals().copy().items() if not k.startswith('__')}
bpy.app.driver_namespace['robot_build'] = namespace
print('White studio ready; original scene preserved.')

# 02_chassis_wheels.py
active = collections['02 Chassis']
for z in [0.045, 0.07]:
    box('Clear acrylic chassis plate', (0, 0, z), (0.158, 0.205, 0.003), clear, 0.008)
for x in [-0.061, 0.061]:
    for y in [-0.083, 0.083]:
        cylinder('M3 metal standoff', (x, y, 0.0575), 0.003, 0.025, metal)
        cylinder('Chassis screw head', (x, y, 0.073), 0.0038, 0.0015, metal)
        box('Screw slot', (x, y, 0.0739), (0.005, 0.00065, 0.00015), black, 0)
active = collections['03 Wheels and motors']
wheel_roots = []
for (side, x) in [('Left', -0.093), ('Right', 0.093)]:
    for (end, y) in [('Front', -0.065), ('Rear', 0.065)]:
        label = side + ' ' + end
        before = set(bpy.data.objects)
        bpy.ops.mesh.primitive_torus_add(major_segments=64, minor_segments=16, location=(x, y, 0.034), rotation=(0, math.pi / 2, 0), major_radius=0.0255, minor_radius=0.009)
        o = move(bpy.context.object)
        o.name = label + ' rounded rubber tyre'
        o.data.materials.append(rubber)
        for p in o.data.polygons:
            p.use_smooth = True
        cylinder(label + ' wheel hub', (x, y, 0.034), 0.025, 0.019, yellow, 'X')
        outer = x + (-0.01 if x < 0 else 0.01)
        cylinder(label + ' hub recess', (outer, y, 0.034), 0.0205, 0.0007, black, 'X')
        cylinder(label + ' centre cap', (outer + (-0.001 if x < 0 else 0.001), y, 0.034), 0.007, 0.003, yellow, 'X')
        for j in range(5):
            a = j * math.tau / 5
            o = box(label + ' spoke ' + str(j), (outer, y + math.sin(a) * 0.011, 0.034 + math.cos(a) * 0.011), (0.003, 0.005, 0.021), yellow, 0.001)
            o.rotation_euler.x = -a
        bpy.ops.mesh.primitive_torus_add(major_segments=48, minor_segments=8, location=(outer, y, 0.034), rotation=(0, math.pi / 2, 0), major_radius=0.0225, minor_radius=0.0025)
        o = move(bpy.context.object)
        o.name = label + ' yellow rim'
        o.data.materials.append(yellow)
        verts = []
        faces = []
        for (row, offset) in enumerate([-0.006, 0, 0.006]):
            for j in range(36):
                a = (j + row % 2 * 0.45) * math.tau / 36
                centre = Vector((x + offset, y + 0.034 * math.sin(a), 0.034 + 0.034 * math.cos(a)))
                q = Quaternion((1, 0, 0), -a)
                base = len(verts)
                for v in [(-1, -1, -1), (-1, -1, 1), (-1, 1, -1), (-1, 1, 1), (1, -1, -1), (1, -1, 1), (1, 1, -1), (1, 1, 1)]:
                    verts.append(centre + q @ Vector((v[0] * 0.0027, v[1] * 0.0019, v[2] * 0.0008)))
                faces.extend([tuple((base + k for k in face)) for face in [(0, 4, 6, 2), (1, 3, 7, 5), (0, 1, 5, 4), (2, 6, 7, 3), (0, 2, 3, 1), (4, 5, 7, 6)]])
        mesh = bpy.data.meshes.new(label + ' tread mesh')
        mesh.from_pydata(verts, [], faces)
        mesh.update()
        o = bpy.data.objects.new(label + ' tyre tread', mesh)
        active.objects.link(o)
        o.data.materials.append(rubber)
        bevel(o, 0.00025, 2)
        bpy.ops.object.empty_add(type='PLAIN_AXES', location=(x, y, 0.034))
        root = move(bpy.context.object)
        root.name = label + ' wheel rotation'
        root.empty_display_size = 0.015
        for o in set(bpy.data.objects) - before:
            if o != root:
                world = o.matrix_world.copy()
                o.parent = root
                o.matrix_world = world
        wheel_roots.append(root)
        box(label + ' TT gearbox', (math.copysign(0.05, x), y, 0.047), (0.045, 0.027, 0.027), yellow, 0.003)
        cylinder(label + ' motor can', (math.copysign(0.02, x), y, 0.047), 0.01, 0.027, metal, 'X')
        cylinder(label + ' axle', (math.copysign(0.075, x), y, 0.034), 0.002, 0.026, metal, 'X')
bpy.ops.object.select_all(action='DESELECT')
print('Four detailed wheels, motors and acrylic chassis added.')

# 03_electronics.py
active = collections['04 Arduino electronics']
board = box('Arduino Uno blue PCB', (0, -0.021, 0.077), (0.069, 0.053, 0.002), blue, 0.003)
for x in [-0.029, 0.029]:
    for y in [-0.042, 0]:
        cylinder('PCB mounting ring', (x, y, 0.0784), 0.002, 0.0002, gold)
box('ATmega DIP microcontroller', (0.004, -0.029, 0.081), (0.033, 0.009, 0.0045), black, 0.0005)
for j in range(14):
    for y in [-0.035, -0.023]:
        box('ATmega metal lead', (-0.011 + j * 0.0023, y, 0.0795), (0.0008, 0.004, 0.001), metal, 0.0002)
box('USB type B metal socket', (-0.023, -0.009, 0.084), (0.012, 0.014, 0.011), metal, 0.001)
box('USB socket dark opening', (-0.023, -0.0018, 0.084), (0.009, 0.0003, 0.007), black, 0.0003)
box('USB socket white insert', (-0.023, -0.0019, 0.084), (0.006, 0.0003, 0.003), ink, 0.0002)
box('DC barrel jack', (-0.024, -0.038, 0.083), (0.011, 0.013, 0.01), black, 0.001)
cylinder('DC jack hole', (-0.024, -0.0445, 0.084), 0.003, 0.0003, metal, 'Y')
for (y, count) in [(-0.045, 14), (0.002, 10)]:
    box('Female pin header', (0, y, 0.082), (0.048, 0.0045, 0.008), black, 0.0005)
    for j in range(count):
        box('Header pin socket', (-0.022 + j * 0.0033, y, 0.0861), (0.0018, 0.0018, 0.0002), rubber, 0.0001)
box('Reset button housing', (0.025, -0.01, 0.0805), (0.005, 0.006, 0.004), metal, 0.0003)
cylinder('Reset button', (0.025, -0.01, 0.083), 0.0018, 0.0012, black)
for x in [0.019, 0.025]:
    cylinder('Electrolytic capacitor', (x, -0.035, 0.082), 0.0025, 0.007, metal)
    box('Capacitor top mark', (x, -0.035, 0.0856), (0.003, 0.0003, 0.0001), black, 0)
for j in range(10):
    x = -0.013 + j % 5 * 0.007
    y = -0.014 - j // 5 * 0.004
    box('Surface mount resistor', (x, y, 0.0788), (0.003, 0.0013, 0.0006), black, 0.00015)
    for dx in [-0.0016, 0.0016]:
        box('Resistor solder pad', (x + dx, y, 0.0785), (0.0009, 0.0015, 0.0003), metal, 0.0001)
text('Arduino silkscreen', 'ARDUINO', (0, -0.016, 0.0786), 0.004, ink)
text('UNO silkscreen', 'UNO', (0.018, -0.007, 0.0786), 0.005, ink)
text('Digital silkscreen', 'DIGITAL PWM', (0, -0.04, 0.0786), 0.0017, ink)
text('Analog silkscreen', 'ANALOG IN', (0, -0.003, 0.0786), 0.0015, ink)
for (x, m) in [(0.016, red), (0.02, yellow)]:
    box('Status LED', (x, -0.017, 0.079), (0.002, 0.0014, 0.001), m, 0.0002)
active = collections['05 Battery holder']
box('Battery tray base', (0, 0.06, 0.08), (0.094, 0.065, 0.004), black, 0.002)
for x in [-0.047, 0.047]:
    box('Battery holder side wall', (x, 0.06, 0.087), (0.003, 0.065, 0.017), black, 0.001)
for y in [0.028, 0.092]:
    box('Battery holder end wall', (0, y, 0.087), (0.094, 0.003, 0.017), black, 0.001)
for x in [-0.0235, 0, 0.0235]:
    box('Battery slot divider', (x, 0.06, 0.085), (0.002, 0.06, 0.01), black, 0.0007)
for (i, x) in enumerate([-0.035, -0.0117, 0.0117, 0.035]):
    box('Battery contact plate', (x, 0.031, 0.086), (0.012, 0.0005, 0.007), metal, 0.0002)
    pts = []
    for j in range(81):
        t = j / 80
        a = t * math.tau * 5
        pts.append((x + 0.004 * math.cos(a), 0.083 + t * 0.006, 0.087 + 0.004 * math.sin(a)))
    curve('Battery spring ' + str(i), pts, 0.00045, metal)
active = collections['06 Ultrasonic sensor']
box('White ultrasonic upright bracket', (0, -0.101, 0.086), (0.065, 0.006, 0.038), ink, 0.002)
box('Sensor mounting foot', (0, -0.095, 0.074), (0.065, 0.024, 0.004), ink, 0.001)
box('HC-SR04 blue PCB', (0, -0.106, 0.094), (0.047, 0.002, 0.021), blue, 0.001)
for x in [-0.013, 0.013]:
    cylinder('Ultrasonic aluminium transducer', (x, -0.116, 0.098), 0.01, 0.017, metal, 'Y', 64)
    cylinder('Ultrasonic dark grille', (x, -0.1249, 0.098), 0.0084, 0.0004, rubber, 'Y', 64)
    bpy.ops.mesh.primitive_torus_add(major_segments=48, minor_segments=8, location=(x, -0.1253, 0.098), rotation=(math.pi / 2, 0, 0), major_radius=0.0091, minor_radius=0.00065)
    o = move(bpy.context.object)
    o.name = 'Sensor rolled aluminium rim'
    o.data.materials.append(metal)
    for j in range(-7, 8):
        v = j * 0.001
        reach = math.sqrt(max(0, 0.0077 ** 2 - v * v))
        curve('Sensor grille horizontal', [(x - reach, -0.1256, 0.098 + v), (x + reach, -0.1256, 0.098 + v)], 0.0001, metal)
        curve('Sensor grille vertical', [(x + v, -0.1256, 0.098 - reach), (x + v, -0.1256, 0.098 + reach)], 0.0001, metal)
for x in [-0.022, 0.022]:
    cylinder('Sensor mounting screw', (x, -0.108, 0.087), 0.0018, 0.0012, metal, 'Y')
text('Sensor label', 'HC-SR04', (0, -0.1073, 0.106), 0.0025, ink, (math.pi / 2, 0, 0))
active = collections['07 Wiring']
for (i, m) in enumerate([red, black, wireblue, wireyellow]):
    x = -0.005 + i * 0.0035
    curve('Jumper wire ' + str(i), [(x, 0.003, 0.086), (x - 0.01, -0.007, 0.135 + i * 0.002), (x + 0.006, -0.06, 0.138 + i * 0.002), (x, -0.098, 0.114)], 0.0008, m)
    for (y, z) in [(0.003, 0.089), (-0.098, 0.111)]:
        box('Jumper female connector', (x, y, z), (0.0026, 0.003, 0.008), black, 0.0003)
curve('Battery positive lead', [(0.043, 0.066, 0.088), (0.053, 0.03, 0.085), (0.038, -0.005, 0.09), (0.023, 0.002, 0.089)], 0.0009, red)
curve('Battery negative lead', [(0.043, 0.064, 0.087), (0.056, 0.025, 0.081), (0.03, -0.009, 0.091), (0.02, 0.002, 0.089)], 0.0009, black)
for x in [-0.05, 0.05]:
    curve('Motor red power lead', [(x, -0.065, 0.05), (x * 0.8, -0.04, 0.064), (x * 0.5, -0.01, 0.072)], 0.00055, red)
    curve('Motor black power lead', [(x, 0.065, 0.05), (x * 0.8, 0.03, 0.061), (x * 0.5, 0, 0.072)], 0.00055, black)
bpy.ops.object.select_all(action='DESELECT')
print('Arduino board, four-cell holder, twin sensor grilles and jumper wiring added.')

# 04_save.py
scene['reference'] = 'Four-view robot reference generated from the supplied robot photograph.'
scene['front_direction'] = 'Negative Y; wheels rotate around local X.'
scene['dimensions_note'] = 'Approximate visual proportions, not a measured engineering CAD model.'
for root in wheel_roots:
    root['rotate_axis'] = 'X'
active = collections['08 Cameras and lighting']
for (name, loc) in [('Front', (0, -0.55, 0.13)), ('Rear', (0, 0.55, 0.13)), ('Left', (-0.55, 0, 0.13)), ('Right', (0.55, 0, 0.13)), ('Top', (0, 0, 0.55))]:
    bpy.ops.object.camera_add(location=loc)
    o = move(bpy.context.object)
    o.name = name + ' orthographic camera'
    o.rotation_euler = (Vector((0, 0, 0.07)) - o.location).to_track_quat('-Z', 'Y').to_euler()
    o.data.type = 'ORTHO'
    o.data.ortho_scale = 0.3
    o.data.clip_start = 0.001
scene.camera = camera
scene.render.image_settings.file_format = 'PNG'
scene.render.filepath = OUT + '/robot-white-room.png'
bpy.ops.object.select_all(action='DESELECT')
for screen in bpy.data.screens:
    for area in screen.areas:
        if area.type == 'VIEW_3D':
            area.spaces.active.region_3d.view_perspective = 'CAMERA'
            area.spaces.active.region_3d.view_camera_zoom = 12
            area.spaces.active.overlay.show_overlays = False
assert len(wheel_roots) == 4
assert all((len(o.data.vertices) > 0 for o in scene.objects if o.type == 'MESH'))
print('Saved robot-white-room.blend with', len(scene.objects), 'editable objects and six cameras.')

# 05_lighting.py
for (name, energy) in [('Large softbox', 3), ('Soft fill', 1.5), ('Back edge light', 2.5)]:
    bpy.data.objects[name].data.energy = energy
clear.node_tree.nodes['Principled BSDF'].inputs['Alpha'].default_value = 0.45
blue.node_tree.nodes['Principled BSDF'].inputs['Base Color'].default_value = (0.008, 0.1, 0.22, 1)
yellow.node_tree.nodes['Principled BSDF'].inputs['Base Color'].default_value = (0.85, 0.43, 0.005, 1)
for screen in bpy.data.screens:
    for area in screen.areas:
        if area.type == 'VIEW_3D':
            area.spaces.active.overlay.show_overlays = False
            area.tag_redraw()
print('Balanced white studio lighting; scene saved.')

# 06_assembly.py
active = collections['02 Chassis']
bpy.ops.object.empty_add(type='PLAIN_AXES', location=(0, 0, 0))
master = move(bpy.context.object)
master.name = 'Robot assembly • move whole robot'
master.empty_display_size = 0.04
for key in ['02 Chassis', '03 Wheels and motors', '04 Arduino electronics', '05 Battery holder', '06 Ultrasonic sensor', '07 Wiring']:
    for o in list(collections[key].objects):
        if o != master and o.parent is None:
            world = o.matrix_world.copy()
            o.parent = master
            o.matrix_world = world
bpy.ops.object.select_all(action='DESELECT')
master.select_set(True)
bpy.context.view_layer.objects.active = master
print('Master assembly control saved. Robot remains open in Blender.')

# 07_batteries.py
active = collections['05 Battery holder']
label = bpy.data.materials.get('HUATAI red printed battery sleeve') or material('HUATAI red printed battery sleeve', (0.8, 0.005, 0.02), rough=0.32)
nt = label.node_tree
tex = nt.nodes.new('ShaderNodeTexImage')
tex.image = bpy.data.images.load(OUT + '/huatai-battery-label.png', check_existing=True)
tex.image.pack()
nt.links.new(tex.outputs['Color'], nt.nodes['Principled BSDF'].inputs['Base Color'])
for (i, x) in enumerate([-0.035, -0.0117, 0.0117, 0.035]):
    before = set(bpy.data.objects)
    z = 0.09
    y0 = 0.035
    y1 = 0.082
    r = 0.0098
    N = 96
    verts = []
    faces = []
    for y in [y0, y1]:
        for j in range(N):
            a = j * math.tau / N
            verts.append((x + r * math.cos(a), y, z + r * math.sin(a)))
    for j in range(N):
        faces.append((j, (j + 1) % N, (j + 1) % N + N, j + N))
    mesh = bpy.data.meshes.new('Battery %d printed sleeve mesh' % (i + 1))
    mesh.from_pydata(verts, [], faces)
    mesh.update()
    o = bpy.data.objects.new('HUATAI battery %d red sleeve' % (i + 1), mesh)
    active.objects.link(o)
    o.data.materials.append(label)
    uv = mesh.uv_layers.new(name='Label wrap')
    for poly in mesh.polygons:
        j = poly.index
        poly.use_smooth = True
        for (li, co) in zip(poly.loop_indices, [(j / N, 0), ((j + 1) / N, 0), ((j + 1) / N, 1), (j / N, 1)]):
            uv.data[li].uv = co
    cylinder('Battery %d negative metal cap' % (i + 1), (x, y1 + 0.00035, z), r, 0.0007, metal, 'Y', 64)
    cylinder('Battery %d positive cap' % (i + 1), (x, y0 - 0.00035, z), r, 0.0007, metal, 'Y', 64)
    cylinder('Battery %d positive button' % (i + 1), (x, y0 - 0.00105, z), 0.0035, 0.001, metal, 'Y', 48)
    for y in [y0 + 0.0003, y1 - 0.0003]:
        bpy.ops.mesh.primitive_torus_add(major_segments=64, minor_segments=8, location=(x, y, z), rotation=(math.pi / 2, 0, 0), major_radius=r - 0.00035, minor_radius=0.00035)
        rim = move(bpy.context.object)
        rim.name = 'Battery %d red insulating rim' % (i + 1)
        rim.data.materials.append(red)
    bpy.ops.object.empty_add(type='PLAIN_AXES', location=(x, (y0 + y1) / 2, z))
    root = move(bpy.context.object)
    root.name = 'HUATAI battery %d assembly' % (i + 1)
    root.empty_display_size = 0.008
    for p in set(bpy.data.objects) - before:
        if p != root:
            world = p.matrix_world.copy()
            p.parent = root
            p.matrix_world = world
    root.parent = bpy.data.objects['Robot assembly • move whole robot']
    root['cell_type'] = 'Reference-style cylindrical dry cell; dimensions fitted to existing holder.'
bpy.ops.object.select_all(action='DESELECT')
for screen in bpy.data.screens:
    for area in screen.areas:
        if area.type == 'VIEW_3D':
            area.tag_redraw()
print('Four red HUATAI batteries inserted; label texture packed into the blend file.')

# 08_battery_labels.py
for i in range(1, 5):
    o = bpy.data.objects['HUATAI battery %d red sleeve' % i]
    for loop in o.data.uv_layers.active.data:
        loop.uv.x += 0.28
print('Battery branding rotated into view and saved.')

# 09_refresh_label.py
tex.image.reload()
tex.image.pack()
print('Red sleeves and upright brand lettering saved.')

# 10_label_orientation.py
for i in range(1, 5):
    o = bpy.data.objects['HUATAI battery %d red sleeve' % i]
    for loop in o.data.uv_layers.active.data:
        loop.uv.y = 1 - loop.uv.y
print('Label reading direction corrected.')

# 11_obstacle_course.py
import math, json
from mathutils import Vector
master = bpy.data.objects['Robot assembly • move whole robot']
for (name, size, loc) in [('White floor', (6, 6, 0.016), (0, 0, -0.009)), ('White back wall', (6, 0.025, 2.4), (0, 2.2, 1.2)), ('White left wall', (0.025, 4.4, 2.4), (-2.2, 0, 1.2)), ('White right wall', (0.025, 4.4, 2.4), (2.2, 0, 1.2))]:
    o = bpy.data.objects[name]
    o.dimensions = size
    o.location = loc
scene.world.node_tree.nodes['Background'].inputs[1].default_value = 0.8
for (name, loc, energy, size) in [('Large softbox', (-1, -0.5, 2.4), 150, 2.5), ('Soft fill', (1, -1, 1.8), 80, 2), ('Back edge light', (0, 1.5, 2), 100, 2)]:
    o = bpy.data.objects[name]
    o.location = loc
    o.data.energy = energy
    o.data.size = size
    o.rotation_euler = (Vector((0, -0.1, 0)) - o.location).to_track_quat('-Z', 'Y').to_euler()
active = bpy.data.collections.get('09 Obstacle course')
if not active:
    active = bpy.data.collections.new('09 Obstacle course')
    scene.collection.children.link(active)
blockmat = material('Warm timber obstacle blocks', (0.4, 0.2, 0.08), rough=0.65)
nt = blockmat.node_tree
p = nt.nodes['Principled BSDF']
noise = nt.nodes.new('ShaderNodeTexNoise')
noise.inputs['Scale'].default_value = 7
noise.inputs['Detail'].default_value = 3
mapping = nt.nodes.new('ShaderNodeVectorMath')
mapping.operation = 'MULTIPLY'
mapping.inputs[1].default_value = (5, 1, 30)
coords = nt.nodes.new('ShaderNodeTexCoord')
nt.links.new(coords.outputs['Generated'], mapping.inputs[0])
nt.links.new(mapping.outputs[0], noise.inputs['Vector'])
ramp = nt.nodes.new('ShaderNodeValToRGB')
ramp.color_ramp.elements[0].color = (0.2, 0.08, 0.025, 1)
ramp.color_ramp.elements[1].color = (0.63, 0.35, 0.14, 1)
nt.links.new(noise.outputs['Fac'], ramp.inputs[0])
nt.links.new(ramp.outputs['Color'], p.inputs['Base Color'])
block_positions = [(0, 0.65), (0.42, -0.15), (-0.42, -0.95)]
blocks = []
for (i, (x, y)) in enumerate(block_positions, 1):
    o = box('Obstacle block %d' % i, (x, y, 0.1), (0.2, 0.2, 0.2), blockmat, 0.007)
    blocks.append(o)
    text('Block %d number' % i, str(i), (x, y, 0.201), 0.055, ink)
scanmat = material('Sensor detection cyan', (0.01, 0.52, 0.65), rough=0.3)
p = scanmat.node_tree.nodes['Principled BSDF']
p.inputs['Emission'].default_value = (0.01, 0.35, 0.5, 1)
p.inputs['Emission Strength'].default_value = 0.4
scan = curve('Ultrasonic detection indicator', [(0, -0.13, 0.097), (0, -0.31, 0.097)], 0.0016, scanmat)
scan.parent = master
camera.location = (2.6, -3.8, 3.4)
target = Vector((0, -0.1, 0.04))
camera.rotation_euler = (target - camera.location).to_track_quat('-Z', 'Y').to_euler()
camera.data.ortho_scale = 3.65
scene.camera = camera
scene.render.resolution_x = 1280
scene.render.resolution_y = 1080
scene.render.resolution_percentage = 100
scene.render.fps = 24
way = [Vector(v) for v in [(0, 1.25), (0, 1.04), (0.42, 1.04), (0.42, 0.25), (-0.42, 0.25), (-0.42, -0.55), (0.42, -0.55), (0.42, -1.45)]]
route = [way[0]]
stops = []
for i in range(1, len(way) - 1):
    (prev, point, nxt) = (way[i - 1], way[i], way[i + 1])
    r = 0.11
    a = point + (prev - point).normalized() * r
    b = point + (nxt - point).normalized() * r
    route.append(a)
    if i in [1, 3, 5]:
        stops.append(len(route) - 1)
    for j in range(1, 25):
        u = j / 24
        route.append((1 - u) ** 2 * a + 2 * (1 - u) * u * point + u * u * b)
route.append(way[-1])
arc = [0]
for (a, b) in zip(route, route[1:]):
    arc.append(arc[-1] + (b - a).length)
stop_dist = [arc[i] for i in stops]
speed = 0.25
fps = 24
pause_frames = 18
poses = []
dist = 0
next_stop = 0
seg = 0
while dist < arc[-1] - 1e-08:
    if next_stop < len(stop_dist) and dist >= stop_dist[next_stop] - 1e-08:
        for j in range(pause_frames):
            poses.append((dist, next_stop + 1))
        next_stop += 1
    next_dist = min(arc[-1], dist + speed / fps)
    if next_stop < len(stop_dist):
        next_dist = min(next_dist, stop_dist[next_stop])
    poses.append((dist, 0))
    dist = next_dist
poses.append((arc[-1], 0))
for j in range(24):
    poses.append((arc[-1], 0))
master.animation_data_clear()
for root in wheel_roots:
    root.animation_data_clear()
    root.rotation_mode = 'XYZ'
scene.frame_start = 1
scene.frame_end = len(poses)
leftangle = rightangle = 0
lastpos = None
lasttheta = None
seg = 0
clearances = []

def overlap_robot_block(pos, theta, block, margin=0.018):
    c = math.cos(theta)
    sn = math.sin(theta)
    ux = Vector((c, sn))
    uy = Vector((-sn, c))
    delta = Vector(block) - pos
    for axis in [ux, uy, Vector((1, 0)), Vector((0, 1))]:
        r_robot = (0.116 + margin) * abs(axis.dot(ux)) + (0.132 + margin) * abs(axis.dot(uy))
        r_block = 0.1 * (abs(axis.x) + abs(axis.y))
        if abs(delta.dot(axis)) > r_robot + r_block:
            return False
    return True
for (f, (d, detect)) in enumerate(poses, 1):
    while seg < len(arc) - 2 and arc[seg + 1] < d:
        seg += 1
    fraction = (d - arc[seg]) / max(1e-09, arc[seg + 1] - arc[seg])
    pos = route[seg].lerp(route[seg + 1], fraction)
    direction = (route[seg + 1] - route[seg]).normalized()
    theta = math.atan2(direction.x, -direction.y)
    if lasttheta is not None:
        while theta - lasttheta > math.pi:
            theta -= math.tau
        while theta - lasttheta < -math.pi:
            theta += math.tau
        ds = (pos - lastpos).length
        turn = theta - lasttheta
        leftangle += (ds + 0.093 * turn) / 0.0348
        rightangle += (ds - 0.093 * turn) / 0.0348
    master.location = (pos.x, pos.y, 0)
    master.rotation_mode = 'XYZ'
    master.rotation_euler = (0, 0, theta)
    master.keyframe_insert('location', frame=f)
    master.keyframe_insert('rotation_euler', frame=f)
    for root in wheel_roots:
        root.rotation_euler.x = leftangle if root.name.startswith('Left') else rightangle
        root.keyframe_insert('rotation_euler', frame=f)
    scan.hide_render = not bool(detect)
    scan.hide_viewport = not bool(detect)
    scan.keyframe_insert('hide_render', frame=f)
    scan.keyframe_insert('hide_viewport', frame=f)
    for block in block_positions:
        assert not overlap_robot_block(pos, theta, block), (f, tuple(pos), theta, block)
    lastpos = pos
    lasttheta = theta
for o in [master] + wheel_roots:
    o.animation_data.action.name = o.name + ' | obstacle avoidance'
    for fc in o.animation_data.action.fcurves:
        for k in fc.keyframe_points:
            k.interpolation = 'LINEAR'
for fc in scan.animation_data.action.fcurves:
    for k in fc.keyframe_points:
        k.interpolation = 'CONSTANT'
scene.timeline_markers.clear()
scene.timeline_markers.new('START — drive forward', frame=1)
for n in range(1, 4):
    frames = [i + 1 for (i, p) in enumerate(poses) if p[1] == n]
    scene.timeline_markers.new('DETECT BLOCK %d — stop and steer' % n, frame=frames[0])
scene.timeline_markers.new('CLEAR — all three blocks avoided', frame=len(poses) - 24)
scene['animation_notes'] = 'Choreographed three-obstacle avoidance. Cyan sensor indicator during 0.75-second stops. Wheel rotation follows path distance plus differential steering. Not an autonomous physics/sensor simulation.'
scene.frame_set(1)
for screen in bpy.data.screens:
    for area in screen.areas:
        if area.type == 'VIEW_3D':
            area.spaces.active.region_3d.view_perspective = 'CAMERA'
            area.spaces.active.region_3d.view_camera_zoom = 10
            area.spaces.active.overlay.show_overlays = False
            area.tag_redraw()
scene.render.filepath = OUT + '/obstacle-course.mp4'
scene.render.image_settings.file_format = 'FFMPEG'
scene.render.ffmpeg.format = 'MPEG4'
scene.render.ffmpeg.codec = 'H264'
scene.render.ffmpeg.constant_rate_factor = 'MEDIUM'
report = {'frames': scene.frame_end, 'fps': fps, 'duration_seconds': round(scene.frame_end / fps, 2), 'path_length_m': round(arc[-1], 3), 'blocks': 3, 'collision_check': 'All frames clear of all three blocks, including an 18 mm safety margin.', 'wheel_rotation': 'Distance / 34.8 mm rolling radius, with differential steering at 186 mm track width.'}
open(OUT + '/animation-validation.json', 'w').write(json.dumps(report, indent=2))
print(report)

# 12_fix_assembly.py
from mathutils import Matrix
excluded = {'White floor', 'White back wall', 'White left wall', 'White right wall', 'Ultrasonic detection indicator'}
fixed = 0
for o in scene.objects:
    if o == master or o.type in {'LIGHT', 'CAMERA'} or o.name in excluded or o.name.startswith(('Obstacle block', 'Block ')):
        continue
    if o.parent is None:
        rest = o.matrix_world.copy()
        o.parent = master
        o.matrix_parent_inverse = Matrix.Identity(4)
        o.matrix_basis = rest
        fixed += 1
for o in scene.objects:
    if o == master or o.name in excluded or o.name.startswith(('Obstacle block', 'Block ')) or (o.type in {'LIGHT', 'CAMERA'}):
        continue
    n = o.name
    if n.startswith(('Left Front', 'Left Rear', 'Right Front', 'Right Rear')):
        key = '03 Wheels and motors'
    elif n.startswith(('Clear acrylic', 'M3 ', 'Chassis screw', 'Screw slot')):
        key = '02 Chassis'
    elif 'lead' in n or n.startswith(('Jumper', 'Motor red', 'Motor black')):
        key = '07 Wiring'
    elif n.startswith(('Battery', 'HUATAI')):
        key = '05 Battery holder'
    elif n.startswith(('Ultrasonic', 'Sensor', 'White ultrasonic', 'HC-SR04')):
        key = '06 Ultrasonic sensor'
    else:
        key = '04 Arduino electronics'
    for c in list(o.users_collection):
        c.objects.unlink(o)
    collections[key].objects.link(o)
bpy.data.objects['White back wall'].location.y = 3
bpy.data.objects['White left wall'].location.x = -3
bpy.data.objects['White right wall'].location.x = 3
for (name, power) in [('Large softbox', 75), ('Soft fill', 40), ('Back edge light', 60)]:
    bpy.data.objects[name].data.energy = power
camera.data.ortho_scale = 2.9
scene.frame_set(1)
bpy.context.view_layer.update()
for name in ['Left Front wheel rotation', 'Arduino Uno blue PCB', 'Battery tray base']:
    o = bpy.data.objects[name]
    assert o.parent == master, name
    assert o.matrix_world.translation.y > 0.9, name
scene.render.resolution_x = 1280
scene.render.resolution_y = 1080
scene.eevee.taa_render_samples = 24
print('Fixed', fixed, 'assembly parents; wheel, board and holder movement verified.')

# 13_course_camera.py
scene.frame_set(1)
bpy.data.objects['White floor'].dimensions = (8, 8, 0.016)
bpy.data.objects['White back wall'].location.y = 4
bpy.data.objects['White back wall'].dimensions = (8, 0.025, 2.4)
bpy.data.objects['White left wall'].location.x = -4
bpy.data.objects['White left wall'].dimensions = (0.025, 8, 2.4)
bpy.data.objects['White right wall'].location.x = 4
bpy.data.objects['White right wall'].dimensions = (0.025, 8, 2.4)
overview = bpy.data.objects.new('Obstacle course overview camera', camera.data.copy())
collections['08 Cameras and lighting'].objects.link(overview)
overview.matrix_world = camera.matrix_world.copy()
start_target = Vector((0, -0.1, 0.04))
direction = (camera.location - start_target).normalized()
start_offset = camera.location - start_target
camera.animation_data_clear()
camera.data.animation_data_clear()
for f in range(1, scene.frame_end + 1):
    scene.frame_set(f)
    u = max(0, min(1, (f - 24) / 48))
    u = u * u * (3 - 2 * u)
    robot = master.location.copy()
    close_target = Vector((robot.x, robot.y - 0.25, 0.06))
    target = start_target.lerp(close_target, u)
    offset = start_offset.lerp(direction * 1.65, u)
    camera.location = target + offset
    camera.rotation_euler = (target - camera.location).to_track_quat('-Z', 'Y').to_euler()
    camera.data.ortho_scale = 2.9 * (1 - u) + 1.25 * u
    camera.keyframe_insert('location', frame=f)
    camera.keyframe_insert('rotation_euler', frame=f)
    camera.data.keyframe_insert('ortho_scale', frame=f)
for anim in [camera.animation_data, camera.data.animation_data]:
    for fc in anim.action.fcurves:
        for k in fc.keyframe_points:
            k.interpolation = 'LINEAR'
scene.frame_set(1)
scene.camera = camera
print('Room expanded to 8 metres; overview and smooth tracking cameras saved.')

# 16_quality.py
for (name, power) in [('Large softbox', 48), ('Soft fill', 24), ('Back edge light', 32)]:
    bpy.data.objects[name].data.energy = power
scene.view_settings.exposure = 0
scene.world.node_tree.nodes['Background'].inputs[0].default_value = (0.7, 0.7, 0.7, 1)
scene.world.node_tree.nodes['Background'].inputs[1].default_value = 0.35
scene.eevee.taa_samples = 32
scene.eevee.taa_render_samples = 128
scene.eevee.use_ssr = False
scene.eevee.use_ssr_refraction = False
scene.eevee.use_gtao = True
scene.eevee.gtao_distance = 0.1
scene.eevee.gtao_factor = 1.0
scene.eevee.use_soft_shadows = True
scene.eevee.shadow_cube_size = '2048'
scene.eevee.shadow_cascade_size = '2048'
clear.blend_method = 'HASHED'
clear.use_screen_refraction = False
clear.shadow_method = 'NONE'
clear.use_nodes = True
p = clear.node_tree.nodes['Principled BSDF']
p.inputs['Transmission'].default_value = 0
p.inputs['Alpha'].default_value = 0.2
p.inputs['Base Color'].default_value = (0.68, 0.86, 0.91, 1)
p.inputs['Roughness'].default_value = 0.22
scene.render.resolution_x = 1920
scene.render.resolution_y = 1620
scene.render.resolution_percentage = 100
scene.render.image_settings.color_mode = 'RGB'
scene.render.film_transparent = False
scene.sync_mode = 'FRAME_DROP'
scene.render.use_motion_blur = False
for l in collections['08 Cameras and lighting'].objects:
    if l.type == 'LIGHT':
        l.data.use_shadow = True
        l.data.use_contact_shadow = True
        l.data.contact_shadow_distance = 0.2
scene.frame_set(145)
for screen in bpy.data.screens:
    for area in screen.areas:
        if area.type == 'VIEW_3D':
            area.spaces.active.shading.type = 'MATERIAL'
            area.spaces.active.shading.use_scene_lights = True
            area.spaces.active.shading.use_scene_world = True
            area.tag_redraw()
scene['quality_notes'] = 'Normal neutral lighting. 128 render samples, 1920px output, soft 2048px shadows. Hashed acrylic transparency replaces alpha-sort blending; SSR disabled to avoid moving reflection/refraction artifacts. Rendered animation provides fixed 24 fps independent of viewport performance.'
print('Normal lighting, high quality output and stable acrylic transparency saved.')

# 18_white_plastic.py
plastic = bpy.data.materials.get('White molded chassis plastic') or material('White molded chassis plastic', (0.78, 0.8, 0.82), rough=0.38)
p = plastic.node_tree.nodes['Principled BSDF']
p.inputs['Transmission'].default_value = 0
p.inputs['Alpha'].default_value = 1
plastic.blend_method = 'OPAQUE'
plastic.diffuse_color = (0.85, 0.87, 0.89, 1)
for o in scene.objects:
    if o.type == 'MESH':
        for slot in o.material_slots:
            if slot.material == clear:
                slot.material = plastic
scene.render.resolution_x = 1920
scene.render.resolution_y = 1080
scene.render.resolution_percentage = 100
camera.data.shift_x = -0.12
scene.frame_set(145)
scene['chassis_material'] = 'Solid white molded plastic; glass removed.'
print('Chassis changed to solid white plastic in both editable parts and live viewport; widescreen hero framing saved.')
for m in bpy.data.materials:
 if m.name.startswith('Archived'):continue
 if m.use_nodes and m.node_tree.nodes.get('Principled BSDF'):
  m.diffuse_color=m.node_tree.nodes['Principled BSDF'].inputs['Base Color'].default_value
 if 'HUATAI' in m.name:m.diffuse_color=(.8,.01,.02,1)
scene.frame_set(145)
for screen in bpy.data.screens:
 for area in screen.areas:
  if area.type=='VIEW_3D':
   area.spaces.active.shading.type='SOLID';area.spaces.active.shading.color_type='MATERIAL';area.spaces.active.overlay.show_overlays=False;area.tag_redraw()
scene['build_notes']='Recreated in one execution. White plastic, normal studio light, three-obstacle route, distance-based wheel spin and high-quality render settings.'
bpy.app.driver_namespace['robot_build']={k:v for k,v in locals().copy().items() if not k.startswith('__')}
bpy.ops.wm.save_as_mainfile(filepath=OUT+'/robot-white-room.blend')
print('Complete robot recreation saved. Playback paused for stability.')
