"""sys.path bootstrap for the real point executor (imports the frozen R1-R4, protocol and point-certificate code)."""
from __future__ import annotations

import sys
from pathlib import Path

NS = Path(__file__).resolve().parents[1]
CP = NS.parents[0]
REPO = NS.parents[2]
PROTOCOL_NS = CP / "p5y_k5_cusum_first_real_probe_protocol"
R4_NS = CP / "p5y_k5_cusum_order3_r4_tightening"
R3_NS = CP / "p5y_k5_cusum_order3_r3_infrastructure"
R2_NS = CP / "p5y_k5_cusum_order3_r2_repair"
R1_NS = CP / "p5y_k5_cusum_order3_real_producer"
POINT_NS = CP / "p5y_gammatilde_point_certificate"
AUX5_NS = CP / "p5y_k1_cusum_aux5_successor"

for _p in (str(AUX5_NS / "code"), str(POINT_NS / "code"), str(PROTOCOL_NS / "code"), str(R1_NS / "code"), str(R2_NS / "code"),
           str(R3_NS / "code"), str(R4_NS / "code"), str(NS / "code")):
    if _p in sys.path:
        sys.path.remove(_p)
    sys.path.insert(0, _p)
