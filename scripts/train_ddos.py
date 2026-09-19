import runpy, sys
from pathlib import Path
sys.argv[1:] = ["ddos", *sys.argv[1:]]
runpy.run_path(str(Path(__file__).with_name("train_model.py")), run_name="__main__")
