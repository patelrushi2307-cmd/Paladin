"""Offline CI-like final validation command."""
import subprocess, sys
from pathlib import Path
root = Path(__file__).parents[1]
venv_python = root / ".venv" / ("Scripts/python.exe" if sys.platform == "win32" else "bin/python")
python = str(venv_python) if venv_python.exists() else sys.executable
commands = [[python, "-m", "pytest", "-q", "backend/tests"], [python, "-m", "compileall", "-q", "backend/app", "scripts"], [python, str(root / "scripts" / "security_self_test.py")], [python, str(root / "scripts" / "health_check.py")], [python, str(root / "scripts" / "api_smoke.py")], [python, str(root / "scripts" / "benchmark_pipeline.py")], [python, str(root / "scripts" / "benchmark_pcap.py")], [python, str(root / "scripts" / "generate_final_reports.py")], ["npm.cmd", "test"], ["npm.cmd", "run", "build"]]
passed = True
for command in commands:
    working_directory = root / "frontend" if command[0] == "npm.cmd" else root
    print("RUN", " ".join(command)); result = subprocess.run(command, cwd=working_directory); passed = passed and result.returncode == 0
print("FINAL VALIDATION:", "PASS" if passed else "FAIL")
sys.exit(0 if passed else 1)
