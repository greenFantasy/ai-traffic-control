'''
Uses Streamlit to create a dashboard
'''
import streamlit as st
import streamlit.components.v1 as components
from matplotlib import artist, pyplot as plt
import sys
import os
import re
import analyze 
import pandas as pd

sys.path.append('../data')
sys.path.append('../sim')

# Get the directories of runs and the number of runs
num_runs = 0
dirs = None
for dirpath, dirnames, filenames in os.walk('../data'):
    if len(dirnames)==0:
        continue
    dirs = [dirname for dirname in dirnames if re.match(".*run[0-9]*", dirname)]
    num_runs = len(dirs)-1

# Display the graphs 
graph_datanames = ['total_spawned', 'total_through', 'mean_wait_time']
graph_data = {}
for dataname in graph_datanames:
    graph_data[dataname] = {}
for dirname in dirs:
    run_num = int(dirname.split("run")[-1])
    results = analyze.analyze(os.path.join('../data', dirname))
    for dataname in graph_datanames:
        graph_data[dataname][run_num] = results[dataname]

for dataname in graph_datanames:
    st.header(dataname)
    dataframe = pd.DataFrame.from_dict({"iterations":graph_data[dataname].keys(), dataname: graph_data[dataname].values()})
    st.vega_lite_chart(dataframe, 
        {"mark": {"type": "line", "tooltip": True}, 
        "width": 800,
        "height": 400,
        "encoding": {
            "x": {"field": "iterations", "type": "quantitative"},
            "y": {"field": dataname, "type": "quantitative"}
        }})

# # with st.expander("Open to see simulation animations"): # To add an expander
# # Animate the simulations 
# import animator 
# x = st.slider('Choose which simulation to animate', min_value=0, max_value=num_runs)
# animation = animator.main(f"run{x}")    
# html = animation.to_html5_video() #.to_html5_video() has an embed limit of 20MB that can be overridden
# components.html(html, height=1000) 
