from datetime import time
import matplotlib
import numpy as np
from matplotlib import artist, pyplot as plt
from matplotlib import animation
import analyze
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
    ax = plt.axes(xlim=(-300, 300), ylim=(-300, 300))
    ax.set_aspect('equal')
    cars, = ax.plot([], [], "bo", lw=2)
    redcars, = ax.plot([], [], "ro", lw=2)
    greencars, = ax.plot([], [], "o", lw=2, color="#7EBDC2")
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
    # inter = world.intersection
    # store the generated paths in a dict as well
    subpaths = dict()
    try:
        world.intersections
    except:
        world.intersections = [world.intersection]
    for intersection in world.intersections:
        for path in intersection.sub_paths:
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

    # Load up vehicle state changes and store with timestamp for easy access
    vehicle_id_set = set()
    
    vehicle_intersection_times = analyze.load_vehicle_intersection_times(dataPathPrefix)
    vehicle_state_changes = dict()
    for dic in vehicle_intersection_times:
        enter_timestamp = dic['enter_time']
        leave_timestamp = dic['leave_time']
        aog_timestamp = dic.get('aog_red_time')
        vehicle_id = dic['vehicle_id']
        vehicle_id_set.add(vehicle_id)
        if enter_timestamp in vehicle_state_changes:
            vehicle_state_changes[enter_timestamp].append((vehicle_id, 'green'))
        else:
            vehicle_state_changes[enter_timestamp] = [(vehicle_id, 'green')]
        if leave_timestamp in vehicle_state_changes:
            vehicle_state_changes[leave_timestamp].append((vehicle_id, 'blue'))
        else:
            vehicle_state_changes[leave_timestamp] = [(vehicle_id, 'blue')]
        if aog_timestamp:
            if aog_timestamp in vehicle_state_changes:
                vehicle_state_changes[aog_timestamp].append((vehicle_id, 'red'))
            else:
                vehicle_state_changes[aog_timestamp] = [(vehicle_id, 'red')] 

    # initialize vehicle state hashmap
    vehicle_state = dict()
    for vehicle_id in vehicle_id_set:
        vehicle_state[vehicle_id] = "blue"

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
        redcars.set_data([], [])
        greencars.set_data([], [])
        timeArtist.set_text('Time @ 0')
        artists = [cars, redcars, greencars, timeArtist]
        for key in subpathArtists.keys():
            (artis, color) = subpathArtists[key]
            (xs, ys) = subpaths[key]
            artis.set_data(xs, ys)
            artis.set_color('red')
            artists.append(artis)
        return artists

    # animation function.  This is called sequentially
    dataNameToPlot = "Vehicle_Coords"
    def animate(i):
        coords = ast.literal_eval(dfVehicles.iloc[i][dataNameToPlot])
        time = dfVehicles.iloc[i]['TimeStamp']
        x = [coord[0] for coord in coords]
        y = [coord[1] for coord in coords]
        vehicle_ids = [coord[2] for coord in coords]
        # update car colors
        if time in vehicle_state_changes:
            for (vehicle_id, color) in vehicle_state_changes[time]:
                vehicle_state[vehicle_id] = color
        carsx, carsy =[[data[i] for i in range(len(vehicle_ids)) if vehicle_state[vehicle_ids[i]]=='blue'] for data in [x,y]]
        redcarsx, redcarsy =[[data[i] for i in range(len(vehicle_ids)) if vehicle_state[vehicle_ids[i]]=='red'] for data in [x,y]]
        greencarsx, greencarsy =[[data[i] for i in range(len(vehicle_ids)) if vehicle_state[vehicle_ids[i]]=='green'] for data in [x,y]]
        cars.set_data(carsx, carsy)
        redcars.set_data(redcarsx, redcarsy)
        greencars.set_data(greencarsx, greencarsy)
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
        artists = [cars, redcars, greencars, timeArtist]
        for (artis, _) in subpathArtists.values():
            artists.append(artis)
        artists.reverse()
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