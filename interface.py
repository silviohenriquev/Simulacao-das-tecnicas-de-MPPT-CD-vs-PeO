import tkinter as tk
from tkinter import ttk

from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

from src.modules import modules
from src.pv_module import PVModule


class PVApp:

    def __init__(self, root):

        self.root = root
        self.root.title("PV Module Simulator")

        self.module_data = modules['Canadian Solar CS7N-700TB-AG'].copy()
        self.module = PVModule(self.module_data)

        self.entries = {}
        self.param_vars = {}

        self.create_inputs()
        self.create_parameters()
        self.create_plots()

        self.update_parameters()
        self.update_simulation()

    # ---------------- INPUTS ---------------- #

    def create_inputs(self):

        frame = ttk.LabelFrame(self.root, text="Module Parameters")
        frame.grid(row=0, column=0, padx=10, pady=10, sticky="n")

        params = [
            "I_sc_ref",
            "V_oc_ref",
            "I_mp_ref",
            "V_mp_ref",
            "N_s"
        ]

        for i, p in enumerate(params):

            ttk.Label(frame, text=p).grid(row=i, column=0, sticky="w")

            var = tk.DoubleVar(value=self.module_data[p])
            ttk.Entry(frame, textvariable=var, width=10).grid(row=i, column=1)

            self.entries[p] = var

        ttk.Label(frame, text="Irradiance").grid(row=6, column=0, sticky="w")
        self.G = tk.DoubleVar(value=1000)
        ttk.Entry(frame, textvariable=self.G, width=10).grid(row=6, column=1)

        ttk.Label(frame, text="Temperature").grid(row=7, column=0, sticky="w")
        self.T = tk.DoubleVar(value=25)
        ttk.Entry(frame, textvariable=self.T, width=10).grid(row=7, column=1)

        ttk.Button(
            frame,
            text="Estimate Parameters",
            command=self.run_simulation
        ).grid(row=8, column=0, columnspan=2, pady=10)

    # ---------------- PARAMETERS ---------------- #

    def create_parameters(self):

        frame = ttk.LabelFrame(self.root, text="Estimated Parameters")
        frame.grid(row=0, column=1, padx=10, pady=10, sticky="n")

        params = [
            'I_L_ref',
            'I_o_ref',
            'R_s',
            'R_sh_ref',
            'a_ref',
            'alpha_sc'
        ]

        for i, p in enumerate(params):

            ttk.Label(frame, text=p).grid(row=i, column=0, sticky="w")

            var = tk.StringVar()
            ttk.Label(frame, textvariable=var, width=12).grid(row=i, column=1)

            self.param_vars[p] = var

    def update_parameters(self):

        for p, var in self.param_vars.items():

            value = self.module.parameters[p]
            var.set(f"{value:.4e}")

    # ---------------- PLOTS ---------------- #

    def create_plots(self):

        frame = ttk.Frame(self.root)
        frame.grid(row=1, column=0, columnspan=2, padx=10, pady=10)

        self.fig = Figure(figsize=(7, 6))

        self.ax_iv = self.fig.add_subplot(211)
        self.ax_pv = self.fig.add_subplot(212)

        self.canvas = FigureCanvasTkAgg(self.fig, master=frame)
        self.canvas.get_tk_widget().pack()

    # ---------------- SIMULATION ---------------- #

    def run_simulation(self):

        try:

            for k in self.entries:
                self.module_data[k] = self.entries[k].get()

            self.module = PVModule(self.module_data)

            self.update_parameters()
            self.update_simulation()

        except Exception as e:
            print("Simulation error:", e)

    def update_simulation(self):

        G = self.G.get()
        T = self.T.get()

        v, i, curve = self.module.iv_curve(G, T)
        v2, p, _ = self.module.pv_curve(G, T)

        self.ax_iv.clear()
        self.ax_pv.clear()

        self.ax_iv.plot(v, i)
        self.ax_iv.plot(curve["v_mp"], curve["i_mp"], "ro")

        self.ax_pv.plot(v2, p)
        self.ax_pv.plot(curve["v_mp"], curve["p_mp"], "ro")

        self.ax_iv.set_title("I-V Curve")
        self.ax_pv.set_title("P-V Curve")

        self.ax_iv.set_ylabel("Current [A]")
        self.ax_pv.set_ylabel("Power [W]")
        self.ax_pv.set_xlabel("Voltage [V]")

        self.ax_iv.grid()
        self.ax_pv.grid()

        self.canvas.draw()


if __name__ == "__main__":

    root = tk.Tk()

    app = PVApp(root)

    root.mainloop()