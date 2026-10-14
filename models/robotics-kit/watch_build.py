import bpy
from pathlib import Path
p=Path('/home/watchman-admin/Documents/tinashe/learn-robotics/models/robotics-kit/build_kit.py')
def start():
    if not p.exists(): return 1.0
    exec(compile(p.read_text(),str(p),'exec'),{'__file__':str(p),'__name__':'__main__'})
    return None
bpy.app.timers.register(start,first_interval=2.0)
