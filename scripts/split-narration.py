"""Align a recording to its known transcript and cut at component boundaries.
No equal-length splitting. Review generated cutpoints before publication.
"""
import argparse,json,re,subprocess,tempfile,wave
from pathlib import Path
root=Path(__file__).resolve().parent.parent
p=argparse.ArgumentParser();p.add_argument('audio',type=Path);p.add_argument('--batch',required=True);p.add_argument('--cuts',type=Path,help='Reviewed cutpoints JSON instead of alignment');p.add_argument('--model',default='base');p.add_argument('--output',type=Path,default=root/'assets/audio/narration');p.add_argument('--review-only',action='store_true');args=p.parse_args()
batches=json.loads((root/'docs/narration/batches.json').read_text());batch=next((b for b in batches if b['id']==args.batch),None)
if not batch:raise SystemExit('Unknown batch ID')
if not args.audio.is_file():raise SystemExit('Audio file does not exist')
s=(root/'pages/learn/narration-data.js').read_text();d=json.loads(s[s.index('{'):s.rindex('}')+1]);catalog={c['id']:c for t in d['tours'].values() for c in t['clips']};catalog.update({c['id']:c for c in d['parts']});clips=[catalog[id] for id in batch['clipIds']]
args.output.mkdir(parents=True,exist_ok=True)
# Decode first so edits and fades can be sample-accurate, even when input is MP3.
with tempfile.TemporaryDirectory(prefix='sparks-audio-') as folder:
 decoded=Path(folder)/'decoded.wav'
 subprocess.run(['ffmpeg','-v','error','-y','-i',str(args.audio),'-ar','24000','-ac','1','-c:a','pcm_s16le',str(decoded)],check=True)
 with wave.open(str(decoded),'rb') as w:rate=w.getframerate();frames=w.readframes(w.getnframes());duration=len(frames)/2/rate
 if args.cuts:cuts=json.loads(args.cuts.read_text())
 else:
  try:import stable_whisper
  except ImportError:raise SystemExit('For transcript alignment, install stable-ts in a separate Python environment: pip install stable-ts. Alternatively provide reviewed --cuts JSON. No recording was split.')
  model=stable_whisper.load_model(args.model,device='cpu')
  # Newline-delimited known component turns preserve segment boundaries.
  result=model.align(str(decoded),'\n'.join(c['spoken'].strip() for c in clips),language='en',original_split=True)
  if result is None:raise SystemExit('Alignment found no speech. Review the recording; no cuts were made.')
  doc=result.to_dict();segments=doc.get('segments',[])
  if len(segments)!=len(clips):raise SystemExit('Alignment did not preserve every component boundary. Review and provide --cuts JSON; no guessed cuts were made.')
  cuts={}
  for i,(c,seg) in enumerate(zip(clips,segments)):
   if not seg.get('words') or seg['end']<=seg['start']:raise SystemExit('A component could not be aligned. Review cutpoints; no guessed cuts were made.')
   start=0 if i==0 else (segments[i-1]['end']+seg['start'])/2
   end=duration if i==len(clips)-1 else (seg['end']+segments[i+1]['start'])/2
   cuts[c['id']]={'start':max(0,start),'end':min(duration,end)}
  review=args.output/(args.batch+'-cutpoints.json');review.write_text(json.dumps(cuts,indent=2));print('Alignment cutpoints saved:',review)
  # Alignment is a proposal: use review-only first when bringing back a new recording.
 previous=0
 for c in clips:
  cut=cuts.get(c['id']);
  if not cut:raise SystemExit('Missing cutpoint for '+c['id'])
  start,end=float(cut['start']),float(cut['end'])
  if not 0<=start<end<=duration+.001 or start<previous-.001:raise SystemExit('Invalid or overlapping cutpoints for '+c['id'])
  previous=end
 if args.review_only:print('Validated cutpoints. Listen and review them before final export.');raise SystemExit(0)
 for c in clips:
  cut=cuts[c['id']];start=round(float(cut['start'])*rate);end=round(float(cut['end'])*rate)
  with wave.open(str(args.output/(c['id']+'.wav')),'wb') as w:w.setnchannels(1);w.setsampwidth(2);w.setframerate(rate);w.writeframes(frames[start*2:end*2])
  print('Cut',c['id'],f'{start/rate:.3f}–{end/rate:.3f}s')
print('Split at the supplied/aligned component boundaries. Run python3 scripts/index-narration.py after reviewing the clips.')
