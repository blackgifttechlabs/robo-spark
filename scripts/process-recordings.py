"""Process only Downloads recordings renamed to known batch IDs.
Transcripts guide alignment; cuts use nearby quiet intervals and are logged for review.
Run in the temporary alignment environment; the website never performs alignment.
"""
import argparse,json,re,subprocess,wave,hashlib,shutil,time,difflib
from pathlib import Path
import numpy as np
parser=argparse.ArgumentParser();parser.add_argument('--downloads',type=Path,default=Path.home()/'Downloads');parser.add_argument('--cache',type=Path,default=Path('/tmp/robosparks-recordings'));parser.add_argument('--model',default='base.en');parser.add_argument('--model-dir',type=Path,default=Path('/tmp/robosparks-whisper-models'));parser.add_argument('--review-only',action='store_true');args=parser.parse_args()
root=Path(__file__).resolve().parent.parent
source=(root/'pages/learn/narration-data.js').read_text();data=json.loads(source[source.index('{'):source.rindex('}')+1]);clipmap={c['id']:c for t in data['tours'].values() for c in t['clips']};clipmap.update({c['id']:c for c in data['parts']})
batches={b['id']:b for b in json.loads((root/'docs/narration/batches.json').read_text())};suffixes={'.wav','.mp3','.m4a','.ogg','.flac','.aac'};selected={}
for path in args.downloads.iterdir():
 if not path.is_file() or path.suffix.lower() not in suffixes:continue
 name=path.name
 while Path(name).suffix.lower() in suffixes:name=Path(name).stem
 if name.startswith('v') and name[1:] in batches:name=name[1:]
 if name not in batches:continue
 if name not in selected or path.stat().st_mtime>selected[name].stat().st_mtime:selected[name]=path
if not selected:raise SystemExit('No recordings renamed to known batch IDs were found. Unrelated downloads were not opened.')
args.cache.mkdir(parents=True,exist_ok=True)
review_dir=root/'docs/narration/alignment';review_dir.mkdir(exist_ok=True)
output=root/'assets/audio/narration';output.mkdir(exist_ok=True)
import torch,stable_whisper
torch.set_num_threads(4)
print('Loading English alignment model…',flush=True)
model=stable_whisper.load_model(args.model,device='cpu',download_root=str(args.model_dir))
for name,path in sorted(selected.items()):
 report_path=review_dir/(name+'.json');digest=hashlib.sha256(path.read_bytes()).hexdigest()
 if report_path.exists():
  old=json.loads(report_path.read_text())
  if old.get('source_sha256')==digest and all((output/(id+'.wav')).exists() for id in batches[name]['clipIds']):print('ALREADY PROCESSED',name,flush=True);continue
 cache=args.cache/(name+path.suffix.lower());shutil.copy2(path,cache);decoded=args.cache/(name+'-decoded.wav')
 subprocess.run(['ffmpeg','-v','error','-y','-i',str(cache),'-ar','24000','-ac','1','-c:a','pcm_s16le',str(decoded)],check=True)
 with wave.open(str(decoded),'rb') as wav:rate=wav.getframerate();raw=wav.readframes(wav.getnframes())
 samples=np.frombuffer(raw,dtype='<i2').astype(np.float64)/32768;duration=len(samples)/rate;clips=[clipmap[id] for id in batches[name]['clipIds']]
 print('ALIGNING',name,f'{duration:.2f}s',len(clips),'components',flush=True)
 transcription_path=args.cache/(name+'-transcribed.json')
 if transcription_path.exists():transcription=json.loads(transcription_path.read_text())
 else:
  result=model.transcribe(str(decoded),language='en',fp16=False,verbose=False)
  transcription=result.to_dict();transcription_path.write_text(json.dumps(transcription,indent=2))
 observed=[w for segment in transcription.get('segments',[]) for w in segment.get('words',[])]
 def tokens(text):
  text=text.lower().replace('’',"'").replace('colour','color')
  return [re.sub(r'^h+m+$','hmm',t) for t in re.findall(r"[a-z0-9]+(?:'[a-z]+)?",text)]
 heard=[];word_refs=[]
 for w in observed:
  for token in tokens(w['word']):heard.append(token);word_refs.append(w)
 expected=[];ranges=[]
 for c in clips:
  start=len(expected);expected.extend(tokens(c['spoken']));ranges.append((start,len(expected)))
 matches={}
 for block in difflib.SequenceMatcher(None,expected,heard,autojunk=False).get_matching_blocks():
  for j in range(block.size):matches[block.a+j]=block.b+j
 segments=[]
 for c,(start,end) in zip(clips,ranges):
  anchors=[j for j in range(start,end) if j in matches]
  coverage=len(anchors)/(end-start)
  if coverage<.78 or not anchors or anchors[0]-start>4 or end-1-anchors[-1]>4:
   raise RuntimeError(f'{name}: recorded wording needs review for {c["id"]}; match {coverage:.1%}. No guessed cuts were exported.')
  first=matches[anchors[0]];last=matches[anchors[-1]];first_word=word_refs[first];last_word=word_refs[last]
  words=[];seen=set()
  for j in range(first,last+1):
   w=word_refs[j];key=(w['start'],w['end'],w['word'])
   if key not in seen:words.append(w);seen.add(key)
  segments.append({'start':first_word['start'],'end':last_word['end'],'words':words,'text':c['spoken'],'transcript_match':coverage})
 boundaries=[0.0];gaps=[]
 for i in range(len(segments)-1):
  a=float(segments[i]['end']);b=float(segments[i+1]['start'])
  if b<a:raise RuntimeError(name+': overlapping speech boundaries; manual review required')
  first=max(0,int((a+.015)*rate));last=min(len(samples),int((b-.015)*rate));step=int(.01*rate)
  chunks=[]
  for j in range(first,last-step,step):chunks.append((j/rate,float(np.sqrt(np.mean(samples[j:j+step]**2)))))
  runs=[];start=None
  for timestamp,rms in chunks:
   if rms<.008 and start is None:start=timestamp
   elif rms>=.008 and start is not None:runs.append((start,timestamp));start=None
  if start is not None:runs.append((start,last/rate))
  quiet=max(runs,key=lambda p:p[1]-p[0]) if runs else None
  boundary=(quiet[0]+quiet[1])/2 if quiet and quiet[1]-quiet[0]>=.06 else (a+b)/2
  boundaries.append(boundary);gaps.append({'previous_word_end':a,'next_word_start':b,'quiet_interval':quiet,'cut':boundary,'last_words':segments[i]['text'].strip().split()[-6:],'first_words':segments[i+1]['text'].strip().split()[:6]})
 boundaries.append(duration)
 cuts=[]
 for i,(clip,segment) in enumerate(zip(clips,segments)):
  start,end=boundaries[i:i+2]
  if not segment.get('words') or not 0<=start<float(segment['end'])<=end<=duration+.001:raise RuntimeError(name+': invalid component interval '+clip['id'])
  words=segment['words'];instant=sum(float(w['end'])<=float(w['start']) for w in words)
  if instant>max(2,len(words)*.15):raise RuntimeError(name+': too many unaligned words in '+clip['id'])
  cuts.append({'id':clip['id'],'part':clip['part'],'start':round(start,6),'end':round(end,6),'duration':round(end-start,6),'first_spoken_word':words[0].get('word',''),'last_spoken_word':words[-1].get('word',''),'alignment':words,'transcript_match':segment['transcript_match']})
 report={'batch':name,'source_filename':path.name,'source_sha256':digest,'source_duration':duration,'method':'Recognized speech word timestamps matched to known component transcripts; longest nearby quiet interval for cuts','model':args.model,'sample_rate':rate,'clips':cuts,'boundary_checks':gaps,'review':'Validated against the known transcript and quiet intervals; individual boundary diagnostics are included'}
 if not args.review_only:
  for cut in cuts:
   first=round(cut['start']*rate);last=round(cut['end']*rate)
   with wave.open(str(output/(cut['id']+'.wav')),'wb') as w:w.setnchannels(1);w.setsampwidth(2);w.setframerate(rate);w.writeframes(raw[first*2:last*2])
 report_path.write_text(json.dumps(report,indent=2));print('ALIGNED',name,len(cuts),'clips',flush=True)
print('PROCESSING COMPLETE',flush=True)
