import sys
import re
import os
from multiprocessing import Pool

sys.path.append('../data')
sys.path.append('../sim')

import animator 
cached_animation_path = "cached_animations/"    

def cache_animation(dir): 
    anim = animator.main(dir)
    html = anim.to_html5_video()
    #cache it in cached animations 
    with open(os.path.join(cached_animation_path, dir), "w") as text_file:
        print(html, file=text_file)
    print(f"cached animation {dir} to file")


def cache_driver(num_cores):
    
    print('using %d threads' % num_cores)

    # get params
    settings_file = "dashboard_settings.txt"
    dash_params = {}
    with open(settings_file, "r") as dash_params_file:
        for line in dash_params_file.readlines():
            split_line = line.strip().split("=")
            if len(split_line) != 2:
                print(f"Encountered bad line while loading train_params: {line}, skipping for now")
            else:
                dash_params[split_line[0]] = split_line[1]

    if 'stepsize' in dash_params:
        dash_params['stepsize'] = int(dash_params['stepsize'])

    os.chdir("../util")
    # Get the directories of runs to cache
    dirs = None
    for dirpath, dirnames, filenames in os.walk('../data'):
        if len(dirnames)==0:
            continue
        dirs = [dirname for dirname in dirnames if re.match(".*run[0-9]*", dirname)]
    caching_dirs = [dir for dir in dirs if int(dir.split("run")[-1]) % dash_params['stepsize'] == 0]

    # Cache in parallel 
    with Pool(num_cores) as p:
        p.map(cache_animation, caching_dirs)

if __name__ == "__main__":
    cache_driver(num_cores=4)
    print("Caching Animations Complete")