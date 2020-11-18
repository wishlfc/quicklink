import sys
import os

above_path = os.sep.join(os.path.dirname(os.path.abspath(__file__)).split(os.sep)[:-1])
if above_path not in sys.path:
    sys.path.append(above_path)
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from view_prdescription import pr_description
from view_bts import view_bts, view_bts_get