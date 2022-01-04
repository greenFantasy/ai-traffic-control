from datetime import time
import matplotlib
import numpy as np
from matplotlib import artist, pyplot as plt
from matplotlib import animation
import sys
import pandas as pd
import ast
import dill 
import re
import os

sys.path.append('../data')
sys.path.append('../sim')
plt.rcParams["savefig.dpi"] = 100
dataFolder = None
arg = None
if len(sys.argv)>1:
    arg = sys.argv[1]

def main(run_name):
    dataFolder = None
    if run_name:
        reg_compile = re.compile(f".*{run_name}")
        for dirpath, dirnames, filenames in os.walk('../data'):
            if len(dirnames)==0:
                continue
            dirs = [dirname for dirname in dirnames if  reg_compile.match(dirname)]
            if len(dirs)<=0:
                raise AssertionError( 'No matching directory found')
            else:
                dataFolder = min(dirs, key=lambda x: int(x.split("run")[-1]))
    dataPathPrefix = '../data/'+dataFolder+'/' if dataFolder else '../data/' 
    print(dataPathPrefix)
    animateData = 'vehicle_movement'
    trafficLightData = 'traffic_light_change'
    filename = dataPathPrefix+animateData+".csv"
    dfVehicles = pd.read_csv(filename)
    worldSavePath = dataPathPrefix + "worldsave" + ".pkl"
    # load world
    with open(worldSavePath, 'rb') as worldfile:
        world = dill.load(worldfile)
    filename = dataPathPrefix+trafficLightData+".csv"
    dfTrafficLight = pd.read_csv(filename)

    # First set up the figure, the axis, and the plot elements we want to animate
    fig = plt.figure()
    ax = plt.axes(xlim=(-120, 120), ylim=(-120, 120))
    ax.set_aspect('equal')
    cars, = ax.plot([], [], "bo", lw=2)
    timeArtist = ax.annotate('', xy=(1, 0),xycoords='axes fraction', fontsize=10, horizontalalignment='right', verticalalignment='bottom')

    # store the paths in a dict
    paths = dict()
    for street in world.streets:
        for path in street.paths:
            xs = []
            ys = []
            for i in range(int(path.parametrization.max_pos)):
                pos = path.parametrization.get_pos(i)
                xs.append(pos[0])
                ys.append(pos[1])
            paths[path.id] = (xs, ys)
    inter = world.intersection
    # store the generated paths in a dict as well
    subpaths = dict()
    for path in inter.sub_paths:
        xs = []
        ys = []
        for i in range(int(path.parametrization.max_pos)):
            pos = path.parametrization.get_pos(i)
            xs.append(pos[0])
            ys.append(pos[1])
        subpaths[path.id] = (xs, ys) 

    # Load up traffic light changes - store in a hashmap for easy access
    tlcHashmap = dict()
    for i in range(len(dfTrafficLight)):
        currElem = dfTrafficLight.iloc[i]
        tlID = currElem['Traffic_Light_ID']
        newState = currElem['State_New']
        timeStamp = currElem['TimeStamp']
        if timeStamp in tlcHashmap:
            tlcHashmap[timeStamp].append((tlID, newState))
        else:
            tlcHashmap[timeStamp] = [(tlID, newState)]

    # Store traffic lights in world in hashmap for easy access
    tlHashmap = dict()
    for tl in world.traffic_lights:
        tlHashmap[tl.id] = tl

    # plot the normal paths statically
    for key in paths.keys():
        (xs, ys) = paths[key]
        ax.plot(xs, ys, 'black')

    # plot the generated paths as empty at first just to create the objects - they are populated in init
    subpathArtists = dict()
    for key in subpaths.keys():
        (xs, ys) = subpaths[key]
        artis, = ax.plot([], [], 'red', linewidth=2.5)
        subpathArtists[key] = (artis, 'red')

    # initialization function: plot the background of each frame
    def init():
        cars.set_data([], [])
        timeArtist.set_text('Time @ 0')
        artists = [cars, timeArtist]
        for key in subpathArtists.keys():
            (artis, color) = subpathArtists[key]
            (xs, ys) = subpaths[key]
            artis.set_data(xs, ys)
            artis.set_color(color)
            artists.append(artis)
        return artists

    # animation function.  This is called sequentially
    dataNameToPlot = "Vehicle_Coords"
    def animate(i):
        coords = ast.literal_eval(dfVehicles.iloc[i][dataNameToPlot])
        time = dfVehicles.iloc[i]['TimeStamp']
        x = [coord[0] for coord in coords]
        y = [coord[1] for coord in coords]
        cars.set_data(x, y)
        timeArtist.set_text(f'Time @ {time}')
        if time in tlcHashmap:
            for (tlID, color) in tlcHashmap[time]:
                #get pathIDs from tlIDs
                currtl = tlHashmap[tlID]
                for (path, moveOp) in currtl.controlling_paths:
                    changing_path = path.connecting_paths[moveOp]
                    (artis, _) = subpathArtists[changing_path.id]
                    if color == 'green':
                        color = "#7EBDC2"
                    artis.set_color(color)
                    subpathArtists[changing_path.id] = (artis, color)
        artists = [cars, timeArtist]
        for (artis, _) in subpathArtists.values():
            artists.append(artis)
        return artists

    print("Animating...")
    # call the animator.  blit=True means only re-draw the parts that have changed.
    anim = animation.FuncAnimation(fig, animate, init_func=init,
                                frames=len(dfVehicles), interval=5, blit=True)

    # save the animation as an mp4.  This requires ffmpeg or mencoder to be
    # installed.  The extra_args ensure that the x264 codec is used, so that
    # the video can be embedded in html5.  You may need to adjust this for
    # your system: for more information, see
    # http://matplotlib.sourceforge.net/api/animation_api.html
    # anim.save('basic_animation.mp4', fps=30, extra_args=['-vcodec', 'libx264'])

    #plt.show()
    return anim

def show():
    plt.show()

if __name__ == "__main__":
    animation = main(arg)
    show()