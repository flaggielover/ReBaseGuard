import sys
from pathlib import Path
NS = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(NS/"production"))
sys.path.insert(0, str(NS.parent/"p4z_location_family_feasibility"/"src"))
sys.path.insert(0, str(NS.parent/"p4z_location_family_feasibility"/"production"))
sys.path.insert(0, str(NS.parent/"p4_theory_generalization"/"src"))
