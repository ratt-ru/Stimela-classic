import Pyxis
import ms
import lsm
import mqt
from Pyxis.ModSupport import *

LOG = II("${OUTDIR>/}log-meqtrees_sim.txt")

def azishe():

    mqt.msrun(II("${mqt.CATTERY}/Siamese/turbo-sim.py"), 
              job = '_tdl_job_1_simulate_MS', 
              section = "sim", 
              args = ["${ms.MS_TDL}", "${lsm.LSM_TDL}"])
