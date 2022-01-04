import sys
import re
import os

sys.path.append('../data')
sys.path.append('../sim')

# Get the directories of runs
dirs = None
for dirpath, dirnames, filenames in os.walk('../data'):
    if len(dirnames)==0:
        continue
    dirs = [dirname for dirname in dirnames if re.match(".*run[0-9]*", dirname)]

import animator 
cached_animation_path = "cached_animations/"
stepsize = 10
for dir in dirs:
    if int(dir.split("run")[-1]) % stepsize == 0:
        anim = animator.main(dir)
        html = anim.to_html5_video()
        #cache it in cached animations 
        with open(os.path.join(cached_animation_path, dir), "w") as text_file:
            print(html, file=text_file)
        print(f"cached animation {dir} to file")