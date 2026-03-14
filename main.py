from src.modules import modules
from src.pv_module import PVModule
from src.mppt import MPPT
from src.simulation import Simulation
import numpy as np

module = PVModule(modules['Canadian Solar CS7N-700TB-AG'])

print(module.parameters)

dt = 0.005
t = np.arange(0, 2, dt)

G = np.ones_like(t)*1000
G[t > .75] = 500
G[t > 1.5] = 800

T = np.ones_like(t)*25
T[t>.75] = 60
T[t>1.5] = 40

# mppt = PeO_MPPT(mode="pid", step=0.25, kp=0.02, ki=0.005, kd=0.001)
mppt = MPPT(v_init=module.module['V_oc_ref']*.1)
sim = Simulation(module, mppt, t, G, T)

# --- Teste 1: Método Tensão Constante (CV) ---
mppt.cv_method(k=0.76)
sim.run(run_name="CV Method", v_start=module.module['V_oc_ref']*.5)

# --- Teste 2: Método P&O Fixo ---
mppt.peo_fixed_method(step=0.25)
sim.run(run_name="P&O Fixed", v_start=module.module['V_oc_ref']*.5)

# --- Teste 3: Método P&O PID ---
mppt.peo_pid_method(kp=0.05, ki=0.01)
sim.run(run_name="P&O PID", v_start=module.module['V_oc_ref']*.5)

# --- Plotando os Resultados ---
# Vai mostrar as três estratégias no mesmo gráfico!

print(f"Eficiência de CV Method = {sim.calculate_efficiency('CV Method'):.2f}%")
print(f"Eficiência de P&O Fixed = {sim.calculate_efficiency('P&O Fixed'):.2f}%")
print(f"Eficiência de P&O PID = {sim.calculate_efficiency('P&O PID'):.2f}%")
sim.plot()

# Se achar que o gráfico ficou bagunçado e quiser ocultar o P&O Fixo:
# sim.plot(curves_to_plot=["CV Method", "P&O PID"])

# sim.run(module.module['V_oc_ref']*.8)
# sim.run(0)
# sim.plot()
# # sim.plot_tracking()
# sim.plot_tracking_with_conditions()

# cases = [
#     (1000, 60),
#     (900, 55),
#     (800, 50),
#     (700, 45),
#     (600, 40),
#     (500, 35),
#     (400, 30),
#     (300, 25),
#     (200, 20),
#     (100, 15)
# ]

# cases = [
#     (1000, 60),
#     (1000, 55),
#     (1000, 50),
#     (1000, 45),
#     (1000, 40),
#     (1000, 35),
#     (1000, 30),
#     (1000, 25),
#     (1000, 20),
#     (1000, 15)
# ]

# cases = [
#     (1000, 25),
#     (800, 25),
#     (600, 25),
#     (400, 25),
#     (200, 25),

# ]

# module.plot_iv(cases)
# module.plot_pv(cases)

# mpp = module.get_mpp(1000, 25)
