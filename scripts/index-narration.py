from pathlib import Path
import json,re
root=Path(__file__).resolve().parent.parent
source=(root/'pages/learn/narration-data.js').read_text();data=json.loads(source[source.index('{'):source.rindex('}')+1])
valid={c['id'] for t in data['tours'].values() for c in t['clips']}|{c['id'] for c in data['parts']}
folder=root/'assets/audio/narration';index={}
for f in folder.iterdir():
 if f.suffix.lower() in ['.wav','.mp3','.ogg','.m4a'] and f.stem in valid:index[f.stem]='assets/audio/narration/'+f.name
(folder/'index.json').write_text(json.dumps(index,indent=2))
print(f'Indexed {len(index)} published narration recordings.')
