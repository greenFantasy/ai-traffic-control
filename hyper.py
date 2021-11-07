import sys
sys.path.append("../ai-traffic-control/sim")
sys.path.append("../ai-traffic-control/RL")
sys.path.append("../ai-traffic-control/generator")
sys.path.append("../ai-traffic-control/data")
import world
import generator

w = world.DedicatedLeftTurnIntersectionWorld([20.] * 4)
w.add_generator(generator.SimpleGenerator(w, {"p": 0.01}))
for i in range(10000):
    w.play()