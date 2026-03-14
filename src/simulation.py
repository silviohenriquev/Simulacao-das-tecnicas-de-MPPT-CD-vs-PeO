import numpy as np
import matplotlib.pyplot as plt


class Simulation:

    def __init__(self, module, mppt, t, irradiance, temperature):

        self.module = module
        self.mppt = mppt
        self.t = t
        self.G = irradiance
        self.T = temperature
        
        # Inicializa arrays vazios
        self.results = {
            'v': np.zeros_like(self.t),
            'i': np.zeros_like(self.t),
            'p': np.zeros_like(self.t),
            'p_max': np.zeros_like(self.t)
        }


    def run(self, v_start=None):
        # Se não passar v_start, ele usa o Voc * 0.8 como sugeri antes
        v_current = v_start if v_start else self.module.module['V_oc_ref'] * 0.8
        
        for k in range(len(self.t)):
            # 1. Medição
            i_current = self.module.current_at_voltage(v_current, self.G[k], self.T[k])
            p_current = v_current * i_current
            
            # 2. Armazenamento
            self.results['v'][k] = v_current
            self.results['i'][k] = i_current
            self.results['p'][k] = p_current
            
            # 3. Cálculo do alvo (apenas para comparação no gráfico)
            _, _, curve = self.module.pv_curve(self.G[k], self.T[k])
            self.results['p_max'][k] = curve['p_mp']

            # 4. Controle (Próximo passo de tensão)
            # Nota: O controle só acontece se não for o último passo
            if k < len(self.t) - 1:
                v_current = self.mppt.update(v_current, i_current)

    def plot(self):

        plt.figure(figsize=(10,6))

        plt.subplot(3,1,1)
        plt.plot(self.t, self.G)
        plt.ylabel("Irradiance (W/m²)")
        plt.grid()

        plt.subplot(3,1,2)
        plt.plot(self.t, self.results['v'])
        plt.ylabel("Voltage (V)")
        plt.plot(self.t, self.results['i'])
        plt.ylabel("Current (I)")
        plt.ylim(0, 50)
        plt.grid()

        plt.subplot(3,1,3)
        plt.plot(self.t, self.results['p'], label="MPPT Power")
        plt.plot(self.t, self.results['p_max'], label="Maximum Power")
        plt.ylabel("Power (W)")
        plt.xlabel("Time (s)")
        plt.grid()
        plt.legend()

        plt.show()

    def plot_tracking(self, step=1):

        Geff = self.G[0]
        Tcell = self.T if np.isscalar(self.T) else self.T[0]

        # curva PV real
        v_curve, p_curve, _ = self.module.pv_curve(Geff, Tcell)

        plt.figure(figsize=(8,6))

        plt.plot(v_curve, p_curve, label="PV curve")

        # trajetória do MPPT
        plt.plot(self.results['v'], self.results['p'], 'r-', label="MPPT trajectory")

        plt.xlabel("Voltage (V)")
        plt.ylabel("Power (W)")
        plt.title("MPPT Tracking on PV Curve")
        plt.grid()
        plt.legend()

        plt.show()

    def plot_tracking_with_conditions(self):

        changes = np.where(
            (np.diff(self.G) != 0) | (np.diff(self.T) != 0)
        )[0] + 1

        indices = np.concatenate(([0], changes))

        plt.figure(figsize=(8,6))

        for idx in indices:

            Geff = self.G[idx]
            Tcell = self.T[idx]

            v, p, curve = self.module.pv_curve(Geff, Tcell)

            label = f"G={Geff} W/m², T={Tcell}°C"

            plt.plot(v, p, label=label)

            plt.plot(
                curve["v_mp"],
                curve["p_mp"],
                "ko"
            )

        # trajetória MPPT
        plt.plot(self.results['v'], self.results['p'], "r-", label="MPPT trajectory")

        plt.xlabel("Voltage (V)")
        plt.ylabel("Power (W)")
        plt.title("PV Curves and MPPT Tracking")
        plt.grid()
        plt.legend()

        plt.show()