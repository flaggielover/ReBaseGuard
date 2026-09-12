import sys
from pathlib import Path
NS = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(NS/"src"))
sys.path.insert(0, str(NS/"audit"))
sys.path.insert(0, str(NS.parent/"p4_theory_generalization"/"src"))
