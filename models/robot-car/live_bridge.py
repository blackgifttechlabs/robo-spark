import socket,json,sys
code=open(sys.argv[1]).read()
if not sys.argv[1].endswith('01_studio.py') and '--direct' not in sys.argv[2:]:
 code='import bpy\nexec('+repr(code)+', bpy.app.driver_namespace["robot_build"])'
s=socket.create_connection(('127.0.0.1',9876),timeout=5);s.settimeout(180)
s.sendall(json.dumps({'type':'execute_code','params':{'code':code}}).encode());data=b''
while True:
 data+=s.recv(65536)
 try:r=json.loads(data);break
 except json.JSONDecodeError:pass
print(json.dumps(r,indent=2));s.close()
if r.get('status')!='success':raise SystemExit(1)
