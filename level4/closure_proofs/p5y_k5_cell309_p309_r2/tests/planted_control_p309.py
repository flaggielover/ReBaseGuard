# q309: planted-control  (this file MUST trigger every static-scan kind; it is never executed)
from fractions import Fraction
from fractions import Fraction as FF
import c2_d5_forecast  # FORBIDDEN_IMPORT
CELL = 309  # CELL_LITERAL
DRIFT = Fraction(9, 5)  # BAND_LITERAL
PATH = "evidence/TCT_INPUTS_309.json"  # TARGET_PATH
DRIFT2 = FF(7, 4)  # BAND_LITERAL via alias (must fire)
