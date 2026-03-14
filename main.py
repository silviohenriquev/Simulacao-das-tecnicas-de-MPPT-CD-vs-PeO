from src.modules import modules
from src.pv_module import PVModule
from src.mppt import PeO_MPPT
from src.simulation import Simulation
import numpy as np

module = PVModule(modules['Canadian Solar CS7N-700TB-AG'])

dt = 0.005
t = np.arange(0, 2, dt)

G = np.ones_like(t)*1000
G[t > .75] = 500
G[t > 1.5] = 800

T = np.ones_like(t)*25
T[t>.75] = 60
T[t>1.5] = 40

mppt = PeO_MPPT(mode="fixed", step=0.25, kp=0.02, ki=0.005, kd=0.001)

sim = Simulation(module, mppt, t, G, T)

sim.run(module.module['V_oc_ref']*.8)
sim.plot()
# sim.plot_tracking()
sim.plot_tracking_with_conditions()

# cases = [
#     (1000, 25),
#     (800, 25),
#     (600, 25),
#     (400, 25),
#     (200, 25)
# ]

# module.plot_iv(cases)
# # module.plot_pv(cases)

# mpp = module.get_mpp(1000, 25)
