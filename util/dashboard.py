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
import ast
import plotly.express as px
from plotly.subplots import make_subplots
import plotly.graph_objects as go

sys.path.append('../data')
sys.path.append('../sim')

# Get settings
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
if 'thresholds' in dash_params:
    dash_params['thresholds'] =  ast.literal_eval(dash_params['thresholds'])
if 'data_to_graph' in dash_params:
    dash_params['data_to_graph'] =  ast.literal_eval(dash_params['data_to_graph'])

# Get the directories of runs and the number of runs
num_runs = 0
dirs = None
for dirpath, dirnames, filenames in os.walk('../data'):
    if len(dirnames)==0:
        continue
    dirs = [dirname for dirname in dirnames if re.match(".*run[0-9]*", dirname)]
    num_runs = len(dirs)-1

# Display the graphs 
graph_datanames = dash_params['data_to_graph']
graph_data = {}
for dataname in graph_datanames:
    graph_data[dataname] = {}
for dirname in dirs:
    run_num = int(dirname.split("run")[-1])
    try:
        results = analyze.analyze(os.path.join('../data', dirname))
    except FileNotFoundError:
        continue
    for dataname in graph_datanames:
        graph_data[dataname][run_num] = results[dataname]

metrics = graph_datanames
final_fig = make_subplots(rows=len(metrics) // 2 + len(metrics) % 2, cols=2, subplot_titles=metrics)
for i, metric in enumerate(graph_datanames):
    fig_metric = go.Scatter(
        x=list(graph_data[metric].keys()), 
        y=list(graph_data[metric].values()),
        line=dict(color='royalblue'),)
    final_fig.append_trace(fig_metric, row=i // 2 + 1, col=i % 2 + 1)
    if metric in dash_params['thresholds']:
        fig_thresh = go.Scatter(
            x=list(graph_data[metric].keys()), 
            y=list([dash_params["thresholds"][metric]]*len(graph_data[metric].values())),
            line=dict(color='firebrick', dash='dash'),)
        final_fig.append_trace(fig_thresh, row=i // 2 + 1, col=i % 2 + 1)
final_fig.update_layout(
            height=300 * (len(metrics) // 2 + len(metrics) % 2),
            width=1000,
            showlegend=False,
        )
st.plotly_chart(final_fig)

cached_animation_path = "cached_animations/"
for dirpath, dirnames, filenames in os.walk(cached_animation_path):
    files = filenames
cached_animations = {}
for file in files:
    # load string
    if file == ".gitkeep":
        continue
    with open(os.path.join(cached_animation_path, file), "r") as text_file:
        lines = text_file.readlines()
        cached_html = "".join(lines)
        cached_animations[int(file.split("run")[-1])] = cached_html

def render_animation(run_num):
    if run_num in cached_animations:
        return cached_animations[run_num]
    animation = animator.main(f"run{run_num}")    
    return animation.to_html5_video() #.to_html5_video() has an embed limit of 20MB that can be 

# # with st.expander("Open to see simulation animations"): # To add an expander
# Animate the simulations 
import animator 
stepsize = 10
x = st.slider('Choose which simulation to animate', min_value=0, max_value=num_runs, step=stepsize)
components.html(render_animation(x), width = 800, height=1000) 
