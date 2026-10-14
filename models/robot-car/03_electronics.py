active=collections['04 Arduino electronics']
board=box('Arduino Uno blue PCB',(0,-.021,.077),(.069,.053,.002),blue,.003)
for x in [-.029,.029]:
 for y in [-.042,0]:cylinder('PCB mounting ring',(x,y,.0784),.002,.0002,gold)
box('ATmega DIP microcontroller',(.004,-.029,.081),(.033,.009,.0045),black,.0005)
for j in range(14):
 for y in [-.035,-.023]:box('ATmega metal lead',(-.011+j*.0023,y,.0795),(.0008,.004,.001),metal,.0002)
box('USB type B metal socket',(-.023,-.009,.084),(.012,.014,.011),metal,.001)
box('USB socket dark opening',(-.023,-.0018,.084),(.009,.0003,.007),black,.0003)
box('USB socket white insert',(-.023,-.0019,.084),(.006,.0003,.003),ink,.0002)
box('DC barrel jack',(-.024,-.038,.083),(.011,.013,.010),black,.001)
cylinder('DC jack hole',(-.024,-.0445,.084),.003,.0003,metal,'Y')
for y,count in [(-.045,14),(.002,10)]:
 box('Female pin header',(0,y,.082),(.048,.0045,.008),black,.0005)
 for j in range(count):box('Header pin socket',(-.022+j*.0033,y,.0861),(.0018,.0018,.0002),rubber,.0001)
box('Reset button housing',(.025,-.010,.0805),(.005,.006,.004),metal,.0003)
cylinder('Reset button',(.025,-.010,.083),.0018,.0012,black)
for x in [.019,.025]:
 cylinder('Electrolytic capacitor',(x,-.035,.082),.0025,.007,metal)
 box('Capacitor top mark',(x,-.035,.0856),(.003,.0003,.0001),black,0)
for j in range(10):
 x=-.013+(j%5)*.007;y=-.014-(j//5)*.004;box('Surface mount resistor',(x,y,.0788),(.003,.0013,.0006),black,.00015)
 for dx in [-.0016,.0016]:box('Resistor solder pad',(x+dx,y,.0785),(.0009,.0015,.0003),metal,.0001)
text('Arduino silkscreen','ARDUINO',(0,-.016,.0786),.004,ink)
text('UNO silkscreen','UNO',(.018,-.007,.0786),.005,ink)
text('Digital silkscreen','DIGITAL PWM',(0,-.040,.0786),.0017,ink)
text('Analog silkscreen','ANALOG IN',(0,-.003,.0786),.0015,ink)
for x,m in [(.016,red),(.020,yellow)]:box('Status LED',(x,-.017,.079),(.002,.0014,.001),m,.0002)
active=collections['05 Battery holder']
box('Battery tray base',(0,.060,.080),(.094,.065,.004),black,.002)
for x in [-.047,.047]:box('Battery holder side wall',(x,.060,.087),(.003,.065,.017),black,.001)
for y in [.028,.092]:box('Battery holder end wall',(0,y,.087),(.094,.003,.017),black,.001)
for x in [-.0235,0,.0235]:box('Battery slot divider',(x,.060,.085),(.002,.06,.010),black,.0007)
for i,x in enumerate([-.035,-.0117,.0117,.035]):
 box('Battery contact plate',(x,.031,.086),(.012,.0005,.007),metal,.0002)
 pts=[]
 for j in range(81):
  t=j/80;a=t*math.tau*5;pts.append((x+.004*math.cos(a),.083+t*.006,.087+.004*math.sin(a)))
 curve('Battery spring '+str(i),pts,.00045,metal)
active=collections['06 Ultrasonic sensor']
box('White ultrasonic upright bracket',(0,-.101,.086),(.065,.006,.038),ink,.002)
box('Sensor mounting foot',(0,-.095,.074),(.065,.024,.004),ink,.001)
box('HC-SR04 blue PCB',(0,-.106,.094),(.047,.002,.021),blue,.001)
for x in [-.013,.013]:
 cylinder('Ultrasonic aluminium transducer',(x,-.116,.098),.010,.017,metal,'Y',64)
 cylinder('Ultrasonic dark grille',(x,-.1249,.098),.0084,.0004,rubber,'Y',64)
 bpy.ops.mesh.primitive_torus_add(major_segments=48,minor_segments=8,location=(x,-.1253,.098),rotation=(math.pi/2,0,0),major_radius=.0091,minor_radius=.00065);o=move(bpy.context.object);o.name='Sensor rolled aluminium rim';o.data.materials.append(metal)
 # Crosshatched fine grille, clipped to the circular face.
 for j in range(-7,8):
  v=j*.001;reach=math.sqrt(max(0,.0077**2-v*v))
  curve('Sensor grille horizontal',[(x-reach,-.1256,.098+v),(x+reach,-.1256,.098+v)],.00010,metal)
  curve('Sensor grille vertical',[(x+v,-.1256,.098-reach),(x+v,-.1256,.098+reach)],.00010,metal)
for x in [-.022,.022]:cylinder('Sensor mounting screw',(x,-.108,.087),.0018,.0012,metal,'Y')
text('Sensor label','HC-SR04',(0,-.1073,.106),.0025,ink,(math.pi/2,0,0))
active=collections['07 Wiring']
for i,m in enumerate([red,black,wireblue,wireyellow]):
 x=-.005+i*.0035
 curve('Jumper wire '+str(i),[(x,.003,.086),(x-.01,-.007,.135+i*.002),(x+.006,-.06,.138+i*.002),(x,-.098,.114)],.0008,m)
 for y,z in [(.003,.089),(-.098,.111)]:box('Jumper female connector',(x,y,z),(.0026,.003,.008),black,.0003)
curve('Battery positive lead',[(.043,.066,.088),(.053,.03,.085),(.038,-.005,.090),(.023,.002,.089)],.0009,red)
curve('Battery negative lead',[(.043,.064,.087),(.056,.025,.081),(.030,-.009,.091),(.02,.002,.089)],.0009,black)
for x in [-.05,.05]:
 curve('Motor red power lead',[(x,-.065,.05),(x*.8,-.04,.064),(x*.5,-.01,.072)],.00055,red)
 curve('Motor black power lead',[(x,.065,.05),(x*.8,.03,.061),(x*.5,0,.072)],.00055,black)
bpy.ops.object.select_all(action='DESELECT')
print('Arduino board, four-cell holder, twin sensor grilles and jumper wiring added.')
