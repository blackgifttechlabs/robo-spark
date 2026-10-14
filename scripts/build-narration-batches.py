"""Group component scripts into roughly two-minute recording sessions."""
from pathlib import Path
import json,math,re,zipfile
root=Path(__file__).resolve().parent.parent
source=(root/'pages/learn/narration-data.js').read_text();data=json.loads(source[source.index('{'):source.rindex('}')+1]);batches=[]
for family,clips in [('basics',[c for t in data['tours'].values() for c in t['clips']]),('parts',data['parts'])]:
 total=sum(len(c['spoken'].split()) for c in clips);count=math.ceil(total/245);target=total/count;groups=[];group=[];words=0
 for i,c in enumerate(clips):
  n=len(c['spoken'].split())
  if group and words+n>target+20 and len(groups)<count-1:groups.append(group);group=[];words=0
  group.append(c);words+=n
 if group:groups.append(group)
 for i,group in enumerate(groups):
  words=sum(len(c['spoken'].split()) for c in group);batch={'id':f'{family}-batch-{i+1:02d}','family':family,'title':f'{"Start here" if family=="basics" else "Parts library"} · Recording {i+1}','clipIds':[c['id'] for c in group],'text':'\n\n<long pause>\n\n'.join(c['text'] for c in group),'spoken':'\n\n'.join(c['spoken'] for c in group),'style':data['style'],'words':words,'estimatedSeconds':round(words/125*60+(len(group)-1)*2)};batches.append(batch)
(root/'docs/narration/batches.json').write_text(json.dumps(batches,indent=2))
lines=['# Roughly two-minute recordings','', 'Copy one complete transcript below into AI Studio. Do not read the heading or component index aloud. Use the same voice and style for all batches. Duration is an estimate: the voice and expression change the final length.','', 'Keep the pause tags between paragraphs. They make component boundaries easier to locate. The audio will be aligned and split from the actual spoken words, not equal-duration guesses.','']
for b in batches:
 lines.extend([f'## {b["title"]}',f'Filename: `{b["id"]}.wav` · Estimated duration: {b["estimatedSeconds"]//60}:{b["estimatedSeconds"]%60:02d}',f'Includes {len(b["clipIds"])} separate explanations.','', '```text',b['text'],'```','', '### Component index — do not paste into the speech transcript',''])
 for id in b['clipIds']:
  c=next(c for c in [c for t in data['tours'].values() for c in t['clips']]+data['parts'] if c['id']==id);lines.append(f'- {c["title"]}: `{id}`')
 lines.append('')
(root/'docs/narration/TWO-MINUTE-BATCHES.md').write_text('\n'.join(lines))
with zipfile.ZipFile(root/'docs/narration/narration-pack.zip','w',zipfile.ZIP_DEFLATED) as z:
 for f in (root/'docs/narration').glob('*.md'):z.write(f,f.name)
 z.write(root/'docs/narration/batches.json','batches.json')
print('Grouped',sum(len(b['clipIds']) for b in batches),'clips into',len(batches),'approximately two-minute batches.')
for b in batches:print(b['id'],b['words'],'words',b['estimatedSeconds'],'estimated seconds')
