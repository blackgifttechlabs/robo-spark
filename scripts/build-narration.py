"""Create separate original narration clips, production scripts and playback data."""
from pathlib import Path
import json,re
root=Path(__file__).resolve().parent.parent
style='A warm, playful robot companion speaking to children aged 8–12. Clear conversational English, gentle curiosity, a friendly smile and light comic timing. About 125–140 words per minute. Small natural breaths and thoughtful pauses. Never shout. Treat a wrong guess as a chance to discover. Keep the voice and accent consistent across clips.'
# Each turn introduces or connects one component: a stable audio/animation boundary.
raw={
'what-is-a-robot':[
('ultrasonic-sensor','Distance sensor','<chuckles> Hello, explorer! I’m Sparks. See these two round eyes? This is a distance sensor. It measures how close an object is. Hmm... a block ahead! Better tell the controller.','sense'),
('microcontroller','Controller','Here comes the controller. Think of it as a small computer following a recipe. A person writes its instructions. <short pause> The sensor sends a measurement, and the program decides what happens next.','connect'),
('geared-motor','Motor','Now meet the motor. It changes electrical energy into movement. A motor driver controls its power. <chuckles> I could tell a wheel to turn all day... but without a motor, it would just sit there!','connect'),
('robot-wheel','Wheel','Ooh, here comes a wheel! Fit it to a motor shaft and it can roll. Sensors measure. Programs give instructions. Motors move things. Put those ideas together, and you have the beginnings of a rover.','connect'),
('ultrasonic-sensor','The whole team','<gasp> The path is clear! Our picture shows how the parts can work together. Real robots also need a power supply, a suitable driver and checked wiring. Your first challenge: which part notices the obstacle?','finish')],
'meet-the-parts':[
('aa-battery','Battery','Let’s meet the team, one part at a time. I’m a battery! Well... <chuckles> Sparks is talking for the battery. It stores energy. Find the raised positive end and the flat negative end.','inspect'),
('jumper-wires','Jumper wires','These are jumper wires. Their metal ends make connections. Their coloured covers help us follow the path. Hmm... colours are useful labels, but a red wire does not magically know where to go!','connect'),
('led','LED','This tiny light is an LED. Look closely: two legs! One is the anode, and one is the cathode. It needs to face the right way in a circuit. <short pause> Tiny part, bright idea.','connect'),
('resistor','Resistor','Wait a moment—our little light needs a helper. This is a resistor. It limits current through the LED. See the coloured bands? They describe its resistance. A suitable value depends on the real circuit.','connect'),
('slide-switch','Switch','Click! Here comes a switch. When its contacts join, it closes the path. When they separate, it opens the path. <chuckles> It’s like a tiny gate for this circuit.','connect'),
('breadboard','Breadboard','And this is a breadboard. No bread inside! <chuckles> It holds parts without soldering. Some holes are connected together underneath. The centre gap separates the two sides. Always check its layout before wiring.','inspect')],
'what-is-a-circuit':[
('aa-battery','Start with energy','Ready for a little mystery? A battery has two terminals. To power our light, we need a path from one terminal, through the parts, and back to the other. <short pause> A complete loop!','inspect'),
('resistor','Add the resistor','Our resistor joins the path. Its job is to limit current. Hmm... we are building an idea picture here. The correct resistor and connections for a real LED must be checked first.','connect'),
('led','Add the light','Now the LED arrives. The path continues through the light. Electrical energy can become light energy. <gasp> But there is still a gap! Let’s look at our switch.','connect'),
('slide-switch','Close the path','The switch closes its contacts. Now the loop is complete and our screen light glows. Open the contacts and it goes out. <chuckles> Mystery solved: a gap breaks the path.','circuit'),
('jumper-wires','Follow the loop','Follow the blue path around the whole loop. Battery, resistor, light, switch... and back again. Your turn: predict what happens when the switch opens. Then try it in practice mode.','finish')],
'one-light':[
('led','Meet the LED','Today’s big invention is... one little light! <chuckles> Every inventor starts somewhere. Turn this LED around. Find its two legs and the flat edge on its body. They help us identify the terminals.','inspect'),
('resistor','Protect the light','Here comes our resistor. It limits current through the light. More energy is not always better. Hmm... even a tiny LED needs the right circuit to stay happy.','connect'),
('aa-battery','Add the energy','The battery supplies energy. In a real build, ask an adult to help choose a suitable supply, resistor and LED connections. Our picture shows the idea, so you can understand each part’s job first.','connect'),
('jumper-wires','Complete the idea','We join our idea picture into a loop. <gasp> Look at that glow! An LED makes light, a resistor limits current, and a battery supplies energy. Try placing those helpers in practice mode.','circuit')],
'control-a-light':[
('aa-battery','Meet the supply','We have energy, a resistor and a little light. But I want to choose WHEN it shines. Hmm... could a tiny gate help? Let’s find out.','inspect'),
('slide-switch','Meet the switch','Here is our switch! Slide its handle and the contacts move. Open means a gap. Closed means the contacts join. <short pause> Say it with me: open... closed!','connect'),
('resistor','Keep the helper','The resistor stays in our circuit while we test the switch. It still limits current. <chuckles> We are changing the path, not forgetting our little light’s helper.','connect'),
('led','Light on, light off','Close the path... light on! Open the path... light off! <gasp> You’re in charge. Try it again and explain what changed in the connections.','circuit')],
'meet-the-controller':[
('microcontroller','A small computer','Meet the controller. It’s a small computer that runs a program. It doesn’t think like you do. <chuckles> You supply the clever instructions, and it follows them.','inspect'),
('push-button','Information in','Here comes a button. Pressing it can give the controller information. We call that an input. A sensor can provide an input too. Hmm... has someone pressed the button yet?','connect'),
('led','Action out','An LED is an output: it does something we can notice. A program can tell it to turn on, wait, turn off, and wait again. The LED still needs suitable connections and current limiting.','connect'),
('microcontroller','Put instructions in order','On... wait... off... wait! Repeat those instructions and the light blinks. <gasp> Order matters. Try sorting the parts into input, controller and output in practice mode.','finish')]
}
tours={}
for lesson,turns in raw.items():
 clips=[]
 for i,(part,title,text,action) in enumerate(turns):
  clips.append({'id':f'{lesson}--{i+1:02d}-{part}','part':part,'title':title,'text':text,'spoken':re.sub(r'<[^>]+>','',text).strip(),'action':action,'style':style,'sound':'scan' if action=='sense' else 'connect','captions':[s.strip() for s in re.split(r'(?<=[.!?])\s+',re.sub(r'<[^>]+>','',text)) if s.strip()]})
 tours[lesson]={'title':lesson.replace('-',' ').title(),'clips':clips}
kit=json.loads((root/'models/robotics-kit/manifest.json').read_text())
extra={
 'ultrasonic-sensor':'Measures how close an object is using sound pulses.', 'servo-actuator':'Turns an arm to a commanded position.', 'geared-motor':'Turns electrical energy into rotation, using gears to change speed and torque.', 'microcontroller':'Runs the instructions in your program.', 'breadboard':'Holds small circuit parts. Groups of holes are connected underneath.', 'motor-driver':'Controls power to a motor when the controller sends instructions.', 'motion-sensor':'Detects changes in infrared radiation that can indicate movement.', 'temperature-sensor':'Measures temperature and humidity.', 'light-sensor':'Measures changes in light level.', 'buzzer':'Turns an electrical signal into a buzzing sound.', 'stepper-motor':'Turns in controlled steps with a suitable driver.', 'battery-holder':'Holds batteries and connects their terminals.', 'led':'Makes light when connected the right way with suitable current limiting.', 'potentiometer':'Changes resistance when you turn its knob.', 'push-button':'Changes a connection when you press it.', 'jumper-wires':'Connect circuit parts together.', 'robot-wheel':'Rolls to help a rover move.', 'relay':'Uses an electrically controlled switch to change a connection.', 'infrared-sensor':'Uses infrared light to detect nearby objects.', 'linear-actuator':'Moves a rod in or out.'}
parts=[]
for i,p in enumerate(kit['components']):
 description=p.get('lesson') or extra.get(p['id'],'Helps connect or support robot parts.')
 intro=['Ooh, look closely!','Hmm... what could we make with this?','Ready for another discovery?','Here comes another helper!'][i%4]
 text=f"{intro} This is {p['name'].lower()}. {description} "+(' <chuckles> Small parts can lead to big ideas!' if i%7==0 else 'Turn it around and notice its shape.')
 parts.append({'id':'part--'+p['id'],'part':p['id'],'title':p['name'],'text':text,'spoken':re.sub(r'<[^>]+>','',text),'style':style,'action':'inspect'})
data={'style':style,'voice':'Puck','model':'gemini-3.8-flash-tts','tours':tours,'parts':parts}
(root/'pages/learn/narration-data.js').write_text('export const narration = '+json.dumps(data,indent=2)+';\n')
doc=root/'docs/narration';doc.mkdir(exist_ok=True)
for lesson,tour in tours.items():
 lines=[f'# {tour["title"]}: separate narration clips','', 'Generate each clip separately. Keep the same voice and style. Save each download using the clip ID as its filename.','', '## Style field','',style,'']
 for clip in tour['clips']:
  lines.extend([f'## {clip["title"]}',f'Filename: `{clip["id"]}.wav`',f'Visual: {clip["part"]}; animation action: {clip["action"]}.','', '### Current Gemini TTS transcript','', '```text',clip['text'],'```','', '### Bracket-tag version for earlier TTS models','', '```text',re.sub(r'<([^>]+)>',r'[\1]',clip['text']),'```',''])
 (doc/(lesson+'.md')).write_text('\n'.join(lines))
lines=['# Separate narration for all 70 parts','', 'Use the common style in `AI-STUDIO-GUIDE.md`. Generate one file per part. These are original scripts.','']
for clip in parts:lines.extend([f'## {clip["title"]}',f'Filename: `{clip["id"]}.wav`','', '```text',clip['text'],'```',''])
(doc/'all-70-parts.md').write_text('\n'.join(lines))
print(f'Wrote {sum(len(t["clips"]) for t in tours.values())} lesson clips and 70 separate part scripts.')
