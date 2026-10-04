import re
with open("ml/addon/eval_cohorts.py", "r") as f:
    content = f.read()

header = """import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../../")))
"""
if "sys.path.insert" not in content:
    content = header + content
    with open("ml/addon/eval_cohorts.py", "w") as f:
        f.write(content)
