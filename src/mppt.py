import numpy as np

class MPPT:
    def __init__(self, v_init=30):
        self.v_init = v_init
        self.reset()
        # Define uma estratégia padrão que não faz nada
        self._strategy = self._idle_step

    def reset(self):
        """Limpa o histórico para uma nova simulação"""
        self.v = self.v_init
        self.prev_v = self.v_init
        self.prev_p = 0
        self.direction = 1
        self.integral = 0
        self.prev_error = 0

    # --- ESCOLHA DO MÉTODO ---

    def cv_method(self, k=0.78):
        """Configura o controlador para Tensão Constante"""
        self.k_cv = k
        self._strategy = self._cv_step

    def peo_fixed_method(self, step=0.5):
        """Configura o controlador para P&O com passo fixo"""
        self.step = step
        self._strategy = self._peo_fixed_step

    def peo_pid_method(self, kp=0.05, ki=0.01, kd=0.0):
        """Configura o controlador para P&O com PID"""
        self.kp = kp
        self.ki = ki
        self.kd = kd
        self._strategy = self._peo_pid_step

    # --- O CONTRATO ---
    
    def update(self, v, i, **kwargs):
        """A simulação sempre chama isso, e a estratégia atual resolve"""
        return self._strategy(v, i, **kwargs)

    # --- AS LÓGICAS INTERNAS PRIVADAS ---

    def _idle_step(self, v, i, **kwargs):
        return v

    def _cv_step(self, v, i, **kwargs):
        # Tenta pegar o 'voc' dos argumentos extras. 
        current_voc = kwargs.get('voc')
        if current_voc is None:
            raise ValueError("O método CV dinâmico exige que o 'voc' seja passado no update.")
            
        # Calcula a nova referência baseada no Voc daquele exato milissegundo
        return current_voc * self.k_cv

    def _peo_fixed_step(self, v, i, **kwargs):
        p = v * i
        if p - self.prev_p > 0:
            self.direction = 1 if v - self.prev_v > 0 else -1
        else:
            self.direction = -1 if v - self.prev_v > 0 else 1
            
        self.prev_v = v
        self.prev_p = p
        return v + self.direction * self.step

    def _peo_pid_step(self, v, i, **kwargs):
        p = v * i
        dV = v - self.prev_v
        
        # Evita divisão por zero
        if abs(dV) < 1e-4:
            dV = 1e-4 if dV >= 0 else -1e-4

        dP = p - self.prev_p
        
        # Lógica de Direção do P&O
        if dP > 0:
            current_direction = 1 if dV > 0 else -1
        else:
            current_direction = -1 if dV > 0 else 1

        # --- CORREÇÃO DO INTEGRAL WINDUP ---
        # Se a direção mudou, significa que cruzamos o Ponto de Máxima Potência.
        # Precisamos zerar a integral para não acumular erro passado.
        if current_direction != self.direction:
            self.integral = 0
            
        self.direction = current_direction

        # Cálculo do Erro e PID
        error = abs(dP / dV)
        # Aumentei um pouco o limite do clip do integrador para dar mais margem de atuação
        self.integral = np.clip(self.integral + error, -5, 5) 
        derivative = error - self.prev_error
        
        # Calcula o tamanho do passo
        step_raw = self.kp * error + self.ki * self.integral + self.kd * derivative
        step = np.clip(abs(step_raw), 0.005, 2.0)
        
        # Atualiza a "memória" do controlador
        self.prev_error = error
        self.prev_v = v
        self.prev_p = p
        
        # Retorna a NOVA TENSÃO
        return v + self.direction * step