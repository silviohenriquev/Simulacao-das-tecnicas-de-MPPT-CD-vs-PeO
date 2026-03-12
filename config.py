# Exemplo de parametros do modulo Canadian Solar CS5P-220M:
parameters = {
    'Name': 'Canadian Solar CS5P-220M',   # Nome/modelo do módulo fotovoltaico
    'BIPV': 'N',                          # Indica se o módulo é integrado à construção (Building Integrated PV): N = não
    'Date': '10/5/2009',                  # Data de registro/criação do modelo no banco de dados
    'T_NOCT': 42.4,                       # Temperatura Nominal de Operação da Célula (°C) em condições NOCT
    'A_c': 1.7,                           # Área do módulo fotovoltaico em m²
    'N_s': 96,                            # Número de células fotovoltaicas conectadas em série no módulo
    'I_sc_ref': 5.1,                      # Corrente de curto-circuito (Isc) em condições padrão STC (A)
    'V_oc_ref': 59.4,                     # Tensão de circuito aberto (Voc) em STC (V)
    'I_mp_ref': 4.69,                     # Corrente no ponto de máxima potência (Imp) em STC (A)
    'V_mp_ref': 46.9,                     # Tensão no ponto de máxima potência (Vmp) em STC (V)
    'alpha_sc': 0.004539,                 # Coeficiente de temperatura da corrente de curto-circuito (A/°C)
    'beta_oc': -0.22216,                  # Coeficiente de temperatura da tensão de circuito aberto (V/°C)
    'a_ref': 2.6373,                      # Parâmetro térmico do modelo de diodo (produto do fator de idealidade do diodo, número de células e tensão térmica)
    'I_L_ref': 5.114,                     # Corrente fotogerada (corrente de luz) nas condições STC (A)
    'I_o_ref': 8.196e-10,                 # Corrente de saturação do diodo em STC (A), relacionada à recombinação de portadores
    'R_s': 1.065,                         # Resistência série do módulo (Ω), representa perdas internas nos contatos e conexões
    'R_sh_ref': 381.68,                   # Resistência shunt (paralela) em STC (Ω), representa correntes de fuga dentro da célula
    'Adjust': 8.7,                        # Parâmetro empírico de ajuste usado para melhorar o encaixe da curva I-V ao modelo
    'gamma_r': -0.476,                    # Coeficiente de temperatura da potência (%/°C)
    'Version': 'MM106',                   # Versão do modelo ou do banco de dados de parâmetros
    'PTC': 200.1,                         # Potência máxima do módulo em condições PTC (PVUSA Test Conditions) em watts
    'Technology': 'Mono-c-Si',            # Tecnologia da célula fotovoltaica: silício monocristalino
}