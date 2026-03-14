import numpy as np


class PeO_MPPT:

    def __init__(self, step=0.5, v_init=30, mode="fixed", kp=100, ki=0.01, kd=0):

        self.v = v_init
        self.prev_v = v_init
        self.prev_p = 0

        self.direction = 1

        # modo de operação
        self.mode = mode

        # passo fixo
        self.step = step

        # parâmetros PID
        self.kp = kp
        self.ki = ki
        self.kd = kd

        self.integral = 0
        self.prev_error = 0

    def _pid_step(self, error):
            self.integral += error
            # Reduzi os limites do integral windup para evitar acúmulo excessivo
            self.integral = np.clip(self.integral, -1, 1) 

            derivative = error - self.prev_error

            step = (
                self.kp * error +
                self.ki * self.integral +
                self.kd * derivative
            )

            self.prev_error = error

            # Mudei o limite mínimo para 0.005 para permitir que ele realmente "estacione"
            # Mudei o máximo para 2.0 para evitar pulos muito agressivos
            return np.clip(abs(step), 0.005, 2.0)

    def update(self, v, i):
            p = v * i

            dP = p - self.prev_p
            dV = v - self.prev_v

            # Evitar divisão por zero no cálculo da derivada
            if abs(dV) < 1e-4:
                dV = 1e-4 if dV >= 0 else -1e-4

            # lógica P&O tradicional mantida
            if dP > 0:
                if dV > 0:
                    self.direction = 1
                else:
                    self.direction = -1
            else:
                if dV > 0:
                    self.direction = -1
                else:
                    self.direction = 1

            # escolha do passo
            if self.mode == "fixed":
                step = self.step

            elif self.mode == "pid":
                # O verdadeiro erro do MPPT: a inclinação da curva (dP/dV)
                # Usamos o valor absoluto pois a lógica P&O já cuida da direção
                error = abs(dP / dV)
                step = self._pid_step(error)
            else:
                raise ValueError("Mode must be 'fixed' or 'pid'")

            # nova tensão
            self.v = v + self.direction * step

            self.prev_v = v
            self.prev_p = p

            return self.v
    