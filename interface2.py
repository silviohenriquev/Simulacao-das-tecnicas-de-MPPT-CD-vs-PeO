import tkinter as tk
from tkinter import ttk
import numpy as np
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk

# Importando suas classes (ajuste os caminhos conforme sua estrutura de pastas)
from src.modules import modules
from src.pv_module import PVModule
from src.mppt import MPPT
from src.simulation import Simulation

class PVApp:
    def __init__(self, root):
        self.root = root
        self.root.title("PV Module & MPPT Simulator")
        
        # Dados Iniciais
        self.module_data = modules['Canadian Solar CS7N-700TB-AG'].copy()
        self.module = PVModule(self.module_data)
        
        # Variáveis da Aba de Modelagem
        self.entries = {}
        self.param_vars = {}
        
        # Notebook para abas
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(expand=True, fill="both")
        
        self.tab_modelling = ttk.Frame(self.notebook)
        self.tab_simulation = ttk.Frame(self.notebook)
        
        self.notebook.add(self.tab_modelling, text="Modelagem do Módulo")
        self.notebook.add(self.tab_simulation, text="Simulação MPPT")

        # Configura as duas abas
        self.setup_modelling_tab()
        self.setup_simulation_tab()

        # Roda a modelagem inicial para preencher os gráficos da Aba 1
        self.run_modelling_update()

    # =========================================================================
    # ---------------- ABA 1: MODELAGEM (REORGANIZADA) -----------------
    # =========================================================================
    def setup_modelling_tab(self):
        # Criamos dois frames principais para dividir a aba em duas colunas
        left_column = ttk.Frame(self.tab_modelling)
        left_column.grid(row=0, column=0, padx=10, pady=10, sticky="n")

        right_column = ttk.Frame(self.tab_modelling)
        right_column.grid(row=0, column=1, padx=10, pady=10, sticky="nsew")

        # --- COLUNA 1 (ESQUERDA): Parâmetros um abaixo do outro ---
        
        # Frame de Inputs (Module Parameters)
        input_frame = ttk.LabelFrame(left_column, text="Module Parameters")
        input_frame.pack(fill="x", pady=5)

        params_in = ["I_sc_ref", "V_oc_ref", "I_mp_ref", "V_mp_ref", "N_s", "T_coef_sc", "T_coef_oc", "T_coef_pmp"]
        for i, p in enumerate(params_in):
            ttk.Label(input_frame, text=p).grid(row=i, column=0, sticky="w", padx=5, pady=2)
            var = tk.DoubleVar(value=self.module_data[p])
            ttk.Entry(input_frame, textvariable=var, width=10).grid(row=i, column=1, padx=5, pady=2)
            self.entries[p] = var

        # Campos de teste (G e T) dentro do mesmo frame ou logo abaixo
        ttk.Label(input_frame, text="Irradiance").grid(row=9, column=0, sticky="w", padx=5, pady=2)
        self.G_mod = tk.DoubleVar(value=1000)
        ttk.Entry(input_frame, textvariable=self.G_mod, width=10).grid(row=9, column=1, padx=5, pady=2)

        ttk.Label(input_frame, text="Temperature").grid(row=10, column=0, sticky="w", padx=5, pady=2)
        self.T_mod = tk.DoubleVar(value=25)
        ttk.Entry(input_frame, textvariable=self.T_mod, width=10).grid(row=10, column=1, padx=5, pady=2)

        ttk.Button(input_frame, text="Estimate Parameters", command=self.run_modelling_update).grid(row=11, column=0, columnspan=2, pady=10)

        # Frame de Parâmetros Estimados (Abaixo dos inputs)
        param_frame = ttk.LabelFrame(left_column, text="Estimated Parameters")
        param_frame.pack(fill="x", pady=10)

        params_out = ['I_L_ref', 'I_o_ref', 'R_s', 'R_sh_ref', 'a_ref', 'alpha_sc']
        for i, p in enumerate(params_out):
            ttk.Label(param_frame, text=p).grid(row=i, column=0, sticky="w", padx=5, pady=2)
            var = tk.StringVar()
            ttk.Label(param_frame, textvariable=var, width=15, foreground="blue").grid(row=i, column=1, padx=5, pady=2)
            self.param_vars[p] = var

        # --- COLUNA 2 (DIREITA): Gráficos um abaixo do outro ---
        
        self.mod_fig = Figure(figsize=(7, 7)) # Aumentei um pouco a altura para acomodar os dois
        self.ax_iv = self.mod_fig.add_subplot(211)
        self.ax_pv_mod = self.mod_fig.add_subplot(212)

        self.mod_canvas = FigureCanvasTkAgg(self.mod_fig, master=right_column)
        self.mod_canvas.get_tk_widget().pack(side="top", fill="both", expand=True)

        # HABILITAR A LUPA (Navigation Toolbar)
        # Ela aparece logo abaixo do gráfico
        self.toolbar_mod = NavigationToolbar2Tk(self.mod_canvas, right_column)
        self.toolbar_mod.update()
        self.toolbar_mod.pack(side="top", fill="x")

    def run_modelling_update(self):
        try:
            # Atualiza dicionário e recria o módulo
            for k in self.entries:
                self.module_data[k] = self.entries[k].get()
            
            # Aqui atualizamos o self.module (A Aba 2 vai usar esse mesmo módulo atualizado!)
            self.module = PVModule(self.module_data)

            # Atualiza Labels de Parâmetros
            for p, var in self.param_vars.items():
                value = self.module.parameters[p]
                var.set(f"{value:.4e}")

            # Atualiza Gráficos
            G = self.G_mod.get()
            T = self.T_mod.get()
            print(f"DEBUG: T={T} | Rs={self.module.parameters['R_s']:.4f} | Rsh={self.module.parameters['R_sh_ref']:.4f}")

            v, i, curve = self.module.iv_curve(G, T)
            v2, p, _ = self.module.pv_curve(G, T)

            self.ax_iv.clear()
            self.ax_pv_mod.clear()

            self.ax_iv.plot(v, i, label="I-V Curve")
            self.ax_iv.plot(curve["v_mp"], curve["i_mp"], "ro", label="MPP")
            self.ax_pv_mod.plot(v2, p, label="P-V Curve", color="orange")
            self.ax_pv_mod.plot(curve["v_mp"], curve["p_mp"], "ro", label="MPP")

            self.ax_iv.set_title(f"I-V Curve (G={G} W/m², T={T} °C)")
            self.ax_pv_mod.set_title("P-V Curve")
            self.ax_iv.set_ylabel("Current [A]")
            self.ax_pv_mod.set_ylabel("Power [W]")
            self.ax_pv_mod.set_xlabel("Voltage [V]")

            self.ax_iv.grid(True)
            self.ax_pv_mod.grid(True)
            self.mod_fig.tight_layout()
            self.mod_canvas.draw()
            
        except Exception as e:
            print("Erro na modelagem:", e)

    # =========================================================================
    # ---------------- ABA 2: SIMULAÇÃO DINÂMICA (COMPLETA) -------------------
    # =========================================================================
    def setup_simulation_tab(self):
        # Frame Principal da Aba 2 (Scrollable se necessário, mas aqui usaremos colunas)
        main_sim_frame = ttk.Frame(self.tab_simulation)
        main_sim_frame.pack(fill="both", expand=True)

        # --- COLUNA DA ESQUERDA: INPUTS (Painel de Controle) ---
        ctrl_panel = ttk.Frame(main_sim_frame, width=300)
        ctrl_panel.pack(side="left", fill="y", padx=10, pady=10)

        # 1. Configurações de Tempo e Simulação
        time_frame = ttk.LabelFrame(ctrl_panel, text="Global Simulation Settings")
        time_frame.pack(fill="x", pady=5)

        self.sim_dt = tk.DoubleVar(value=0.005)
        self.sim_total_t = tk.DoubleVar(value=2.0)
        self.sim_v_start_pct = tk.DoubleVar(value=0.8) # % da Voc

        ttk.Label(time_frame, text="Time Step (dt):").grid(row=0, column=0, sticky="w")
        ttk.Entry(time_frame, textvariable=self.sim_dt, width=8).grid(row=0, column=1)
        
        ttk.Label(time_frame, text="Total Time (s):").grid(row=1, column=0, sticky="w")
        ttk.Entry(time_frame, textvariable=self.sim_total_t, width=8).grid(row=1, column=1)

        ttk.Label(time_frame, text="V_start (% Voc):").grid(row=2, column=0, sticky="w")
        ttk.Entry(time_frame, textvariable=self.sim_v_start_pct, width=8).grid(row=2, column=1)

        # 2. Parâmetros dos Algoritmos
        mppt_params_frame = ttk.LabelFrame(ctrl_panel, text="MPPT Algorithm Parameters")
        mppt_params_frame.pack(fill="x", pady=5)

        # CV
        ttk.Label(mppt_params_frame, text="CV - k factor:", font='Helvetica 9 bold').grid(row=0, column=0, sticky="w")
        self.mppt_k_cv = tk.DoubleVar(value=0.76)
        ttk.Entry(mppt_params_frame, textvariable=self.mppt_k_cv, width=8).grid(row=0, column=1)

        # Fixed
        ttk.Label(mppt_params_frame, text="Fixed - Step:", font='Helvetica 9 bold').grid(row=1, column=0, sticky="w")
        self.mppt_step_fixed = tk.DoubleVar(value=0.25)
        ttk.Entry(mppt_params_frame, textvariable=self.mppt_step_fixed, width=8).grid(row=1, column=1)

        # PID
        ttk.Label(mppt_params_frame, text="PID - Kp:", font='Helvetica 9 bold').grid(row=2, column=0, sticky="w")
        self.mppt_kp = tk.DoubleVar(value=0.05)
        ttk.Entry(mppt_params_frame, textvariable=self.mppt_kp, width=8).grid(row=2, column=1)

        ttk.Label(mppt_params_frame, text="PID - Ki:").grid(row=3, column=0, sticky="w")
        self.mppt_ki = tk.DoubleVar(value=0.005)
        ttk.Entry(mppt_params_frame, textvariable=self.mppt_ki, width=8).grid(row=3, column=1)

        # 3. Cenário Ambiental (Degraus)
        env_frame = ttk.LabelFrame(ctrl_panel, text="Environmental Scenario (Steps)")
        env_frame.pack(fill="x", pady=5)

        # Headers
        ttk.Label(env_frame, text="Time (s)").grid(row=0, column=1)
        ttk.Label(env_frame, text="G (W/m²)").grid(row=0, column=2)
        ttk.Label(env_frame, text="T (°C)").grid(row=0, column=3)

        # Ponto Inicial (t=0)
        ttk.Label(env_frame, text="Start:").grid(row=1, column=0)
        self.g0 = tk.DoubleVar(value=1000); ttk.Entry(env_frame, textvariable=self.g0, width=6).grid(row=1, column=2)
        self.t0 = tk.DoubleVar(value=25); ttk.Entry(env_frame, textvariable=self.t0, width=6).grid(row=1, column=3)

        # Degrau 1
        ttk.Label(env_frame, text="Step 1:").grid(row=2, column=0)
        self.t_step1 = tk.DoubleVar(value=0.75); ttk.Entry(env_frame, textvariable=self.t_step1, width=6).grid(row=2, column=1)
        self.g1 = tk.DoubleVar(value=500); ttk.Entry(env_frame, textvariable=self.g1, width=6).grid(row=2, column=2)
        self.temp1 = tk.DoubleVar(value=25); ttk.Entry(env_frame, textvariable=self.temp1, width=6).grid(row=2, column=3)

        # Degrau 2
        ttk.Label(env_frame, text="Step 2:").grid(row=3, column=0)
        self.t_step2 = tk.DoubleVar(value=1.5); ttk.Entry(env_frame, textvariable=self.t_step2, width=6).grid(row=3, column=1)
        self.g2 = tk.DoubleVar(value=800); ttk.Entry(env_frame, textvariable=self.g2, width=6).grid(row=3, column=2)
        self.temp2 = tk.DoubleVar(value=25); ttk.Entry(env_frame, textvariable=self.temp2, width=6).grid(row=3, column=3)

        # Botão Rodar
        ttk.Button(ctrl_panel, text="RUN COMPARISON", command=self.run_mppt_comparison).pack(fill="x", pady=10)

        # Resultados (Atualizado com os botões See Tracker)
        res_frame = ttk.LabelFrame(ctrl_panel, text="Tracking Efficiency (%)")
        res_frame.pack(fill="x", pady=5)
        
        # Dicionários para guardar as variáveis e os botões
        self.eff_vars = {
            "CV Method": tk.StringVar(value="CV: ---"),
            "P&O Fixed": tk.StringVar(value="Fixed: ---"),
            "P&O PID": tk.StringVar(value="PID: ---")
        }
        self.tracker_buttons = {}
        
        # Configuração das cores para manter a legenda visual
        colors = {"CV Method": "blue", "P&O Fixed": "green", "P&O PID": "red"}

        for alg, color in colors.items():
            row_frame = ttk.Frame(res_frame)
            row_frame.pack(fill="x", pady=2, padx=5)
            
            # Label da Eficiência
            ttk.Label(row_frame, textvariable=self.eff_vars[alg], foreground=color, width=15).pack(side="left")
            
            # Botão "See Tracker" (inicia desabilitado)
            btn = ttk.Button(row_frame, text="See Tracker", state="disabled",
                             command=lambda name=alg: self.show_tracker_popup(name))
            btn.pack(side="right")
            self.tracker_buttons[alg] = btn

        # --- COLUNA DA DIREITA: GRÁFICOS ---
        plot_frame = ttk.Frame(main_sim_frame)
        plot_frame.pack(side="right", expand=True, fill="both", padx=5)

        self.sim_fig = Figure(figsize=(8, 7))
        self.ax_p = self.sim_fig.add_subplot(211)
        self.ax_v = self.sim_fig.add_subplot(212)
        
        self.sim_canvas = FigureCanvasTkAgg(self.sim_fig, master=plot_frame)
        self.sim_canvas.get_tk_widget().pack(expand=True, fill="both")

        toolbar_frame = ttk.Frame(plot_frame) # Frame para a barra não bagunçar o layout
        toolbar_frame.pack(side="bottom", fill="x")
        
        self.toolbar = NavigationToolbar2Tk(self.sim_canvas, toolbar_frame)
        self.toolbar.update()



    def run_mppt_comparison(self):
        try:
            # 1. Configuração do Tempo (Dinâmico)
            dt = self.sim_dt.get()
            t_total = self.sim_total_t.get()
            t = np.arange(0, t_total, dt)
            
            # 2. Construção dos perfis G e T baseados nos inputs
            G = np.ones_like(t) * self.g0.get()
            T = np.ones_like(t) * self.t0.get()
            
            # Aplica Degrau 1
            mask1 = t >= self.t_step1.get()
            G[mask1] = self.g1.get()
            T[mask1] = self.temp1.get()
            
            # Aplica Degrau 2
            mask2 = t >= self.t_step2.get()
            G[mask2] = self.g2.get()
            T[mask2] = self.temp2.get()

            # 3. Inicialização (Usando V_oc do módulo atualizado na Aba 1)
            voc_ref = self.module.module['V_oc_ref']
            mppt = MPPT(v_init=voc_ref * 0.1)
            sim = Simulation(self.module, mppt, t, G, T)
            v_start = voc_ref * (self.sim_v_start_pct.get() / 100.0 if self.sim_v_start_pct.get() > 1 else self.sim_v_start_pct.get())

            # 4. Rodar Simulações com parâmetros da UI
            mppt.cv_method(k=self.mppt_k_cv.get())
            sim.run(run_name="CV Method", v_start=v_start)

            mppt.peo_fixed_method(step=self.mppt_step_fixed.get())
            sim.run(run_name="P&O Fixed", v_start=v_start)

            mppt.peo_pid_method(kp=self.mppt_kp.get(), ki=self.mppt_ki.get())
            sim.run(run_name="P&O PID", v_start=v_start)

            self.current_sim = sim

            # 5. Atualizar Eficiências e Habilitar Botões
            for alg in ["CV Method", "P&O Fixed", "P&O PID"]:
                eff = sim.calculate_efficiency(alg)
                # Atualiza o texto curto (ex: CV: 99.50%)
                self.eff_vars[alg].set(f"{alg.split()[0]}: {eff:.2f} %")
                # Habilita o botão See Tracker
                self.tracker_buttons[alg].config(state="normal")

            # 6. Renderizar Gráficos
            self.ax_p.clear()
            self.ax_v.clear()

            p_max = sim.all_results["CV Method"]['p_max']
            self.ax_p.plot(t, p_max, 'k--', alpha=0.5, label="Ideal Pmax")
            
            cores = {"CV Method": "blue", "P&O Fixed": "green", "P&O PID": "red"}
            for name in cores:
                res = sim.all_results[name]
                self.ax_p.plot(t, res['p'], label=name, color=cores[name], alpha=0.8)
                self.ax_v.plot(t, res['v'], label=name, color=cores[name], alpha=0.8)

            self.ax_p.set_ylabel("Power [W]")
            self.ax_p.set_title("Dynamic Power Comparison")
            self.ax_p.legend(loc="lower right", fontsize='small')
            self.ax_p.grid(True, alpha=0.3)

            self.ax_v.set_ylabel("Voltage [V]")
            self.ax_v.set_xlabel("Time [s]")
            self.ax_v.grid(True, alpha=0.3)
            
            self.sim_fig.tight_layout()
            self.sim_canvas.draw()

        except Exception as e:
            print(f"Erro na simulação comparativa: {e}")

    def show_tracker_popup(self, run_name):
        """
        Abre uma nova janela pop-up exibindo o gráfico de rastreamento do MPPT
        gerado pela classe Simulation.
        """
        # Verifica se uma simulação já foi rodada e está salva
        if hasattr(self, 'current_sim') and self.current_sim:
            # Cria a janela Pop-up flutuante
            popup = tk.Toplevel(self.root)
            popup.title(f"Tracker Viewer - {run_name}")
            popup.geometry("750x600")
            
            # Chama o método da Simulation que devolve a Figura do Matplotlib
            fig = self.current_sim.plot_tracking_with_conditions(run_name)
            
            if fig:
                # Desenha o gráfico na nova janela
                canvas = FigureCanvasTkAgg(fig, master=popup)
                canvas.draw()
                canvas.get_tk_widget().pack(side="top", fill="both", expand=True)
                
                # Adiciona a lupa (Toolbar) na parte de baixo do pop-up
                toolbar_frame = ttk.Frame(popup)
                toolbar_frame.pack(side="bottom", fill="x")
                toolbar = NavigationToolbar2Tk(canvas, toolbar_frame)
                toolbar.update()

if __name__ == "__main__":
    root = tk.Tk()
    app = PVApp(root)
    root.mainloop()