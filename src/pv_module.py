from pvlib import pvsystem
import pvlib
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt


class PVModule:

    def __init__(self, module):
        self.module = module
        self.parameters = self._estimate_params()
    
    def _convert_temp_coef(self, coef_percent, ref_value):
        return (coef_percent / 100) * ref_value

    def _estimate_params(self):
        alpha_sc = self._convert_temp_coef(self.module['T_coef_sc'], self.module['I_sc_ref'])

        beta_voc = self._convert_temp_coef(self.module['T_coef_oc'],self.module['V_oc_ref'])

        I_L_ref, I_o_ref, R_s, R_sh_ref, a_ref, T_coef_sc =  pvlib.ivtools.sdm.fit_cec_sam(
            celltype = "monoSi",
            v_mp = self.module['V_mp_ref'],
            i_mp = self.module['I_mp_ref'],
            v_oc = self.module['V_oc_ref'],
            i_sc = self.module['I_sc_ref'],
            alpha_sc = alpha_sc,
            beta_voc = beta_voc,
            gamma_pmp = self.module['T_coef_pmp'],
            cells_in_series = self.module['N_s'],
        )

        return {
            'I_L_ref': I_L_ref,
            'I_o_ref': I_o_ref,
            'R_s': R_s,
            'R_sh_ref': R_sh_ref,
            'a_ref': a_ref,
            'alpha_sc': T_coef_sc
        }
    
    def calc_params(self, Geff, Tcell):
        """
        Calcula os parâmetros do modelo de diodo único
        usando o modelo de De Soto.
        """

        IL, I0, Rs, Rsh, nNsVth = pvsystem.calcparams_desoto(
            Geff,
            Tcell,
            alpha_sc=self.parameters['alpha_sc'],
            a_ref=self.parameters['a_ref'],
            I_L_ref=self.parameters['I_L_ref'],
            I_o_ref=self.parameters['I_o_ref'],
            R_sh_ref=self.parameters['R_sh_ref'],
            R_s=self.parameters['R_s'],
            EgRef=1.121,
            dEgdT=-0.0002677
        )

        return {
            'photocurrent': IL,
            'saturation_current': I0,
            'resistance_series': Rs,
            'resistance_shunt': Rsh,
            'nNsVth': nNsVth
        }

    def current_at_voltage(self, V, Geff, Tcell):
        """
        Calcula a corrente do módulo para uma tensão específica.
        Retorna um único ponto da curva I-V.
        """

        params = self.calc_params(Geff, Tcell)

        I = pvsystem.i_from_v(
            voltage=V,
            # method='lambertw',
            method='brentq',
            **params
        )

        return I

    def power_at_voltage(self, V, Geff, Tcell):
        """
        Calcula a potência para uma tensão específica.
        """

        I = self.current_at_voltage(V, Geff, Tcell)

        return V * I

    def iv_curve(self, Geff, Tcell, points=100):
        """
        Gera a curva I-V do módulo para uma irradiância
        e temperatura específicas.
        """

        params = self.calc_params(Geff, Tcell)
        
        curve_info = pvsystem.singlediode(method='lambertw', **params)

        v = np.linspace(0, curve_info['v_oc'], points)

        i = pvsystem.i_from_v(
            voltage=v,
            # method='lambertw',
            method='brentq',
            **params
        )

        return v, i, curve_info

    def pv_curve(self, Geff, Tcell, points=100):
        """
        Gera a curva P-V do módulo para uma irradiância
        e temperatura específicas.
        """

        v, i, curve_info = self.iv_curve(Geff, Tcell, points)

        p = np.multiply(v,i)

        return v, p, curve_info

    def plot_iv(self, conditions):
        """
        Plota curvas I-V para diferentes condições.
        """

        plt.figure()

        for Geff, Tcell in conditions:

            v, i, curve = self.iv_curve(Geff, Tcell)

            label = f"G={Geff} W/m², T={Tcell}°C"

            plt.plot(v, i, label=label)

            # marca MPP
            plt.plot(
                curve['v_mp'],
                curve['i_mp'],
                marker='o',
                color='black'
            )

        plt.xlabel("Voltage [V]")
        plt.ylabel("Current [A]")
        plt.title(self.module['Name'])
        plt.legend()
        plt.grid(True)
        plt.show()

    def plot_pv(self, conditions):
        """
        Plota curvas P-V para diferentes condições.
        """

        plt.figure()

        for Geff, Tcell in conditions:

            v, p, curve = self.pv_curve(Geff, Tcell)

            label = f"G={Geff} W/m², T={Tcell}°C"

            plt.plot(v, p, label=label)

            # marca MPP
            plt.plot(
                curve['v_mp'],
                curve['i_mp']*curve['v_mp'],
                marker='o',
                color='black'
            )

        plt.xlabel("Voltage [V]")
        plt.ylabel("Power [W]")
        plt.title(self.module['Name'])
        plt.legend()
        plt.grid(True)
        plt.show()
    
    def get_mpp(self, Geff, Tcell):
        """
        Retorna o ponto de máxima potência.
        """

        _, _, curve = self.iv_curve(Geff, Tcell)

        return {
            "Vmp": curve['v_mp'],
            "Imp": curve['i_mp'],
            "Pmp": curve['p_mp']
        }
