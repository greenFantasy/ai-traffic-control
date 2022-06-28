# Reinforcement Learning for Traffic Signal Optimization

Traffic lights are often controlled via ancient technology and algorithms, especially outside of the biggest, highest-budget cities. Over 99% of traffic light networks in the U.S. are manually timed, that is, the timings for each green-red sequence is determined manually by a traffic engineer. These timings are inflexible, and cannot fully adapt to local changes in traffic (think holidays, rush hour, accidents, events, or even small temporary variance in traffic patterns). Coordination of traffic networks is also a nasty problem, engineers use heuristics to try and maximize the "arrival on green percentage" for cars through major roads.

**In this project, we build**

- a system to train **DQN-based centralized traffic agents** which can control a fleet of traffic lights to maximize coordination and minimize travel time for cars
- **a fast, flexible simulation software** which can support arbitrary maps/road networks, used to train our DQN agent with high parallelism

### Results

For a variety of simple maps with up to 10 intersections, our DQN agent significantly improves with training easily beats out the best fixed-timing based method.

## For Contributing Devs: ai-traffic-control

Link to design docs: https://docs.google.com/document/d/164u84Un-C45WBT_5X3l0JRWVUuWJGWQ1KaaaA1IaLko/edit

Recommended: Set up a virtual environment for this project.

Python package requirements are stored in requirements.txt. If you add new
requirements, please add them via "pip freeze > requirements.txt" in the correct
directory.

### Profiling Code

If not already installed, first, install snakeviz:
```
  pip install snakeviz
```
Then, run the program you want to profile with cProfile and store the generated data in temp.dat
```
  python -m cProfile -o temp.dat create_world_dedicated_left.py
```
Visualize with:
```
  snakeviz temp.dat
```

### Launch Dashboard

If not already installed, first, install streamlist:
```
  conda install -c conda-forge streamlit
```
Go into the util/ directory, and launch dashboard with:
```
  streamlit run dashboard.py
```
Click the resulting localhost link to view dashboard. 

### Google Drive Folder
https://drive.google.com/drive/folders/1SbjJa9zi4Zx_dCfpG5t4CzzoCA89aYzk
