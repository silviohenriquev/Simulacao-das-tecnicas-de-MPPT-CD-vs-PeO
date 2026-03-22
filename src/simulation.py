import matplotlib.pyplot as plt
import numpy as np

class Simulation:
    def __init__(self, module, mppt, t, irradiance, temperature):
        self.module = module
        self.mppt = mppt
        self.t = t
        self.G = irradiance
        self.T = temperature
        
        # Agora guarda múltiplas rodadas!
        self.all_results = {}

    def run(self, run_name, v_start=None):
        """
        Roda a simulação e salva os resultados usando o 'run_name' como chave.
        """
        # 1. Reseta o MPPT para não pegar o erro da simulação anterior
        self.mppt.reset() 
        
        v_current = v_start if v_start else self.module.module['V_oc_ref'] * 0.8
        
        # Dicionário temporário para esta rodada
        res = {
            'v': np.zeros_like(self.t),
            'i': np.zeros_like(self.t),
            'p': np.zeros_like(self.t),
            'p_max': np.zeros_like(self.t)
        }

        # ==========================================
        # VARIÁVEIS DO SISTEMA DE CACHE
        # ==========================================
        last_G = -1
        last_T = -1
        cached_p_mp = 0
        cached_voc = 0

        for k in range(len(self.t)):
            current_G = self.G[k]
            current_T = self.T[k]

            # --- 1. SISTEMA DE CACHE ---
            # Só recalcula a curva completa da pvlib se a irradiância ou temperatura mudarem!
            # Isso acelera a simulação em até 90% para degraus longos.
            if current_G != last_G or current_T != last_T:
                _, _, curve = self.module.pv_curve(current_G, current_T)
                cached_p_mp = curve['p_mp']
                cached_voc = curve['v_oc']
                
                # Atualiza a memória do cache
                last_G = current_G
                last_T = current_T

            # --- 2. TRAVA DE TENSÃO DE SEGURANÇA ---
            # Impede que o MPPT peça uma tensão maior que o Voc atual.
            # É isso que evita que o solver brentq/lambertw exploda a potência.
            v_current = np.clip(v_current, 0, cached_voc * 0.99)

            # Medição no painel com a tensão já validada
            i_current = self.module.current_at_voltage(v_current, current_G, current_T)
            i_current = max(0, i_current) # Trava física: corrente gerada não pode ser negativa
            
            p_current = v_current * i_current
            
            # Salva no vetor de resultados
            res['v'][k] = v_current
            res['i'][k] = i_current
            res['p'][k] = p_current
            res['p_max'][k] = cached_p_mp

            # Pega o Voc corrigido termicamente do cache
            if k < len(self.t) - 1:
                v_current = self.mppt.update(v_current, i_current, voc=cached_voc)
                
        # Salva a rodada no dicionário principal
        self.all_results[run_name] = res

    def plot(self, curves_to_plot=None):
        """
        Plota as curvas. Se curves_to_plot for None, plota todas que rodaram.
        Você pode passar uma lista de strings para ocultar algumas: 
        ex: sim.plot(curves_to_plot=["CV", "P&O PID"])
        """
        if curves_to_plot is None:
            curves_to_plot = list(self.all_results.keys())

        plt.figure(figsize=(10,8))

        # 1. Irradiância
        plt.subplot(3,1,1)
        plt.plot(self.t, self.G, color='orange')
        plt.ylabel("Irradiance (W/m²)")
        plt.grid()

        # 2. Tensão (Comparativo)
        plt.subplot(3,1,2)
        for name in curves_to_plot:
            plt.plot(self.t, self.all_results[name]['v'], label=f"V - {name}")
        plt.ylabel("Voltage (V)")
        plt.legend(loc="lower right")
        plt.ylim(0, 50)
        plt.grid()

        # 3. Potência (A estrela do show)
        plt.subplot(3,1,3)
        for name in curves_to_plot:
            plt.plot(self.t, self.all_results[name]['p'], label=f"P - {name}")
            
        # Pega a potência máxima (como é igual para todos, basta pegar do primeiro da lista)
        first_key = list(self.all_results.keys())[0]
        plt.plot(self.t, self.all_results[first_key]['p_max'], 'k--', alpha=0.6, label="Maximum Power")
        
        plt.ylabel("Power (W)")
        plt.xlabel("Time (s)")
        plt.legend(loc="lower right")
        plt.grid()

        plt.tight_layout()
        plt.show()

    def calculate_efficiency(self, run_name):
        """
        Calcula a eficiência de rastreamento para uma simulação específica.
        """
        if run_name not in self.all_results:
            print(f"Erro: O resultado '{run_name}' não existe. Rode a simulação primeiro.")
            return

        # Recupera os vetores de potência
        p_extraida = self.all_results[run_name]['p']
        p_maxima = self.all_results[run_name]['p_max']

        # Cálculo da Eficiência (%)
        # Somamos toda a potência ao longo do tempo (equivalente à energia)
        eficiencia = (np.sum(p_extraida) / np.sum(p_maxima)) * 100

        return eficiencia
    
    def plot_tracking_with_conditions(self, run_name):
        if run_name not in self.all_results:
            return None

        # MUDANÇA AQUI: Criar fig e ax de forma explícita
        from matplotlib.figure import Figure
        fig = Figure(figsize=(8, 6), dpi=100)
        ax = fig.add_subplot(111)

        changes = np.where((np.diff(self.G) != 0) | (np.diff(self.T) != 0))[0] + 1
        indices = np.concatenate(([0], changes))

        for idx in indices:
            Geff = self.G[idx]
            Tcell = self.T[idx]
            v, p, curve = self.module.pv_curve(Geff, Tcell)
            
            # MUDANÇA: Usar ax.plot em vez de plt.plot
            ax.plot(v, p, label=f"G={Geff}, T={Tcell}", alpha=0.5, linestyle="--")
            ax.plot(curve["v_mp"], curve["p_mp"], "ko")

        res = self.all_results[run_name]
        ax.plot(res['v'], res['p'], "r-", label=f"Trajectory", linewidth=1.5)

        # MUDANÇA: Configurar labels no objeto ax
        ax.set_xlabel("Voltage (V)")
        ax.set_ylabel("Power (W)")
        ax.set_title(f"MPPT Tracking - {run_name}")
        ax.grid(True)
        ax.legend()
        
        return fig