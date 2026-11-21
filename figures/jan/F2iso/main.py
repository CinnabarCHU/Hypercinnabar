from pathlib import Path
import subprocess
import sys
folder=Path(__file__).resolve().parent
root=folder.parents[2]
subprocess.run([sys.executable,str(root/'main.py'),folder.name,'--version',folder.parent.name,*sys.argv[1:]],check=True)
