"""Report Docker validation status without falsely claiming execution."""
import shutil, subprocess, sys
if shutil.which("docker") is None:
    print("DOCKER RUNTIME NOT EXECUTED: docker executable unavailable")
    sys.exit(2)
commands = [["docker", "compose", "config"], ["docker", "compose", "build"]]
passed = True
for command in commands:
    result = subprocess.run(command); passed = passed and result.returncode == 0
print("DOCKER VALIDATION:", "PASS" if passed else "FAIL")
sys.exit(0 if passed else 1)
