"""Optional Gemini TTS production tool. Credentials come only from the environment."""
import argparse,base64,json,os,urllib.request
from pathlib import Path
root=Path(__file__).resolve().parent.parent
parser=argparse.ArgumentParser();group=parser.add_mutually_exclusive_group(required=True);group.add_argument('--clip');group.add_argument('--lesson');group.add_argument('--batch');parser.add_argument('--voice',default='Puck');parser.add_argument('--model',default='gemini-3.8-flash-tts');args=parser.parse_args()
key=os.environ.get('GEMINI_API_KEY')
if not key:raise SystemExit('Set GEMINI_API_KEY in your terminal environment before running this production tool.')
s=(root/'pages/learn/narration-data.js').read_text();data=json.loads(s[s.index('{'):s.rindex('}')+1]);clips=[c for t in data['tours'].values() for c in t['clips']]+data['parts']
if args.batch:
 batches=json.loads((root/'docs/narration/batches.json').read_text());clips=[b for b in batches if b['id']==args.batch]
elif args.lesson:
 if args.lesson not in data['tours']:raise SystemExit('Unknown lesson ID')
 clips=data['tours'][args.lesson]['clips']
else:clips=[c for c in clips if c['id']==args.clip]
if not clips:raise SystemExit('No matching clip ID')
for c in clips:
 payload={'model':args.model,'input':[{'type':'user_input','content':[{'type':'text','text':c['text'],'annotations':[{'type':'speech_metadata','style':c['style']}]}]}],'response_format':{'type':'audio'},'generation_config':{'speech_config':[{'voice':args.voice}]}}
 request=urllib.request.Request('https://generativelanguage.googleapis.com/v1beta/interactions',data=json.dumps(payload).encode(),headers={'x-goog-api-key':key,'Content-Type':'application/json'})
 try:
  response=json.loads(urllib.request.urlopen(request,timeout=180).read())
 except urllib.error.HTTPError as e:raise SystemExit(f'Google API returned HTTP {e.code}; check access and the selected model.')
 blocks=[b for step in response.get('steps',[]) if step.get('type')=='model_output' for b in step.get('content',[]) if b.get('type')=='audio']
 if not blocks:raise SystemExit('Google returned no audio block; review the API response in your account.')
 audio=base64.b64decode(blocks[-1]['data'])
 if audio[:4]!=b'RIFF':raise SystemExit('Expected a WAV response. Check model output format before saving.')
 folder=root/('assets/audio/batches' if args.batch else 'assets/audio/narration');folder.mkdir(exist_ok=True);target=folder/(c['id']+'.wav');target.write_bytes(audio);print('Generated '+target.name)
print('Align and cut the batch before indexing.' if args.batch else 'Run python3 scripts/index-narration.py to publish the clip paths.')
