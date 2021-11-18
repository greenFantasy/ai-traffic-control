# ai-traffic-control

Link to design docs: https://docs.google.com/document/d/164u84Un-C45WBT_5X3l0JRWVUuWJGWQ1KaaaA1IaLko/edit

Recommended: Set up a virtual environment for this project.

Python package requirements are stored in requirements.txt. If you add new
requirements, please add them via "pip freeze > requirements.txt" in the correct
directory.

## Profiling Code

If not already installed, first, install snakeviz:
  pip install snakeviz

Then, run the program you want to profile with cProfile and store the generated data in temp.dat
  python -m cProfile -o temp.dat create_world_dedicated_left.py
  
Visualize with:
  snakeviz temp.dat

