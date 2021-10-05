import numpy as np
from matplotlib import pyplot as plt
from matplotlib import animation
import sys
import pandas as pd
import ast
sys.path.append('../data')

dataPathPrefix = '../data/'
animateData = 'vehicle_movement'
filename = dataPathPrefix+animateData+".csv"
df = pd.read_csv(filename)

# First, process the vehicle movement into a dataframe

def main(world):
    # First set up the figure, the axis, and the plot element we want to animate
    fig = plt.figure()
    ax = plt.axes(xlim=(-100, 100), ylim=(-100, 100))
    line, = ax.plot([], [], "bo", lw=2)

    # plot the paths statically
    for street in world.streets:
        for path in street.paths:
            xs = []
            ys = []
            for i in range(int(path.parametrization.max_pos)):
                pos = path.parametrization.get_pos(i)
                xs.append(pos[0])
                ys.append(pos[1])
            ax.plot(xs, ys, 'r')

    # initialization function: plot the background of each frame
    def init():
        line.set_data([], [])
        return line,

    # animation function.  This is called sequentially
    dataNameToPlot = "Vehicle_Coords"
    def animate(i):
        coords = ast.literal_eval(df.iloc[i][dataNameToPlot])
        x = [coord[0] for coord in coords]
        y = [coord[1] for coord in coords]
        line.set_data(x, y)
        return line,

    print("Animating...")
    # call the animator.  blit=True means only re-draw the parts that have changed.
    anim = animation.FuncAnimation(fig, animate, init_func=init,
                                frames=len(df), interval=10, blit=True)

    # save the animation as an mp4.  This requires ffmpeg or mencoder to be
    # installed.  The extra_args ensure that the x264 codec is used, so that
    # the video can be embedded in html5.  You may need to adjust this for
    # your system: for more information, see
    # http://matplotlib.sourceforge.net/api/animation_api.html
    # anim.save('basic_animation.mp4', fps=30, extra_args=['-vcodec', 'libx264'])

    plt.show()
