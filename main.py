from config import parameters
from pv_module import PVModule

module = PVModule(parameters)

cases = [
    (1000, 25),
    (800, 25),
    (600, 25),
    (400, 25),
    (200, 25)
]

# module.plot_iv(cases)
module.plot_pv(cases)

mpp = module.get_mpp(1000, 25)

print(mpp)