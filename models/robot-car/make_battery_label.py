from PIL import Image,ImageDraw,ImageFont
from pathlib import Path
out=Path(__file__).parent/'huatai-battery-label.png'
im=Image.new('RGB',(1024,1024),(218,4,23));d=ImageDraw.Draw(im)
d.rectangle((300,0,500,1024),fill=(28,3,8))
font='/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'
word=Image.new('RGBA',(960,200));w=ImageDraw.Draw(word);f=ImageFont.truetype(font,148);w.text((20,5),'HUATAI',font=f,fill='white',stroke_width=1)
word=word.rotate(-90,expand=True);im.paste(word,(300,25),word)
fsmall=ImageFont.truetype(font,30)
for y in range(180,820,45):d.text((680,y),'HEAVY DUTY' if y%90==0 else 'SUPER POWER',font=fsmall,fill='white')
d.rectangle((665,65,805,155),fill='white');d.rectangle((685,80,785,140),fill=(0,147,58));d.ellipse((714,83,758,140),fill='white')
d.text((255,42),'+',font=ImageFont.truetype(font,52),fill='white');d.text((255,910),'−',font=ImageFont.truetype(font,52),fill='white')
im.save(out)
print(out)
