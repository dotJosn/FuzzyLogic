"""
Equipe Josn ( Allan - Adrian - Gustavo - Tiago )

V1 - Umidade interna do motor

V2 - Ruído acústico

V3 - Vibração transversal (vertical/lateral)

V4 - Corrente nominal em carga

V5 - Torque entregue
"""

# Instalar bibliotecas necessárias
# !pip install scikit-fuzzy

import numpy as np
import skfuzzy as fuzz
from skfuzzy import control as ctrl

# =============================================
# DEFINIÇÃO DAS VARIÁVEIS FUZZY
# =============================================

# Variáveis de entrada
umidade = ctrl.Antecedent(np.arange(0, 101, 1), 'umidadeInternaDoMotor')
ruido = ctrl.Antecedent(np.arange(0, 141, 1), 'ruidoAcustico')
vibracao = ctrl.Antecedent(np.arange(0, 11, 0.1), 'vibracaoTransversal')
corrente = ctrl.Antecedent(np.arange(0.0, 450, 1), 'correnteNominalEmCarga')
torque = ctrl.Antecedent(np.arange(0.0, 2.01, 0.01), 'torqueEntregue')

# Variável de saída
risco_falha = ctrl.Consequent(np.arange(0, 101, 1), 'riscoFalha')

# =============================================
# FUNÇÕES DE PERTINÊNCIA
# =============================================

# Umidade Interna (%)
umidade['baixa'] = fuzz.trapmf(umidade.universe, [0, 0, 20, 60])
umidade['normal'] = fuzz.trimf(umidade.universe, [40, 60, 80])
umidade['alta'] = fuzz.trapmf(umidade.universe, [70, 80, 100, 100])

# Ruído Acústico (dB)
ruido['baixo'] = fuzz.trapmf(ruido.universe, [0, 0, 50, 70])
ruido['medio'] = fuzz.trimf(ruido.universe, [60, 75, 85])
ruido['alto'] = fuzz.trapmf(ruido.universe, [80, 85, 140, 140])

# Vibração Transversal (mm/s)
vibracao['baixa'] = fuzz.trapmf(vibracao.universe, [0, 0, 1.0, 2.5])
vibracao['normal'] = fuzz.trimf(vibracao.universe, [2.0, 3.5, 4.5])
vibracao['alta'] = fuzz.trapmf(vibracao.universe, [4.0, 4.5, 10, 10])

# Corrente Nominal
corrente['baixa'] = fuzz.trapmf(corrente.universe, [0, 0, 205, 250])
corrente['media'] = fuzz.trimf(corrente.universe, [235, 293, 337])
corrente['alta'] = fuzz.trapmf(corrente.universe, [322, 352, 450, 450])


# Torque Entregue
torque['baixo'] = fuzz.trapmf(torque.universe, [0.0, 0.0, 0.8, 0.9])
torque['medio'] = fuzz.trimf(torque.universe, [0.85, 1.0, 1.15])
torque['alto'] = fuzz.trapmf(torque.universe, [1.1, 1.3, 2.0, 2.0])

# Risco de Falha (%)
risco_falha['baixo'] = fuzz.trapmf(risco_falha.universe, [0, 0, 20, 40])
risco_falha['medio'] = fuzz.trimf(risco_falha.universe, [30, 50, 70])
risco_falha['alto'] = fuzz.trapmf(risco_falha.universe, [60, 80, 100, 100])

# =============================================
# REGRAS FUZZY
# =============================================
rules = [
    ctrl.Rule(umidade['alta'] | ruido['alto'] | vibracao['alta'], risco_falha['alto']),
    ctrl.Rule(corrente['alta'] & torque['baixo'], risco_falha['alto']),
    ctrl.Rule(ruido['medio'] & vibracao['normal'], risco_falha['medio']),
    ctrl.Rule(umidade['alta'] & ruido['medio'], risco_falha['medio']),
    ctrl.Rule(umidade['normal'] & ruido['baixo'] & vibracao['baixa'], risco_falha['baixo']),
    ctrl.Rule(torque['alto'] & corrente['alta'], risco_falha['alto']),
    ctrl.Rule(corrente['baixa'] & vibracao['alta'], risco_falha['medio']),
    ctrl.Rule(umidade['alta'] & torque['medio'], risco_falha['medio']),
    ctrl.Rule(vibracao['normal'] & ruido['alto'], risco_falha['medio']),
    ctrl.Rule(corrente['media'] & torque['medio'] & ruido['baixo'], risco_falha['baixo'])
]

# =============================================
# SISTEMA DE CONTROLE
# =============================================
sistema_risco = ctrl.ControlSystem(rules)
simulador = ctrl.ControlSystemSimulation(sistema_risco)

# =============================================
# FUNÇÃO DE INTERAÇÃO
# =============================================
def avaliar_risco_motor():
    try:
        print("\n" + "="*40)
        print("AVALIAÇÃO DE RISCO DE FALHA EM MOTORES")
        print("="*40 + "\n")

        # Capturar entradas
        umid = float(input("Umidade interna do motor (%) (0 a 100): "))
        ruid = float(input("Nível de ruído (dB) (0 a 140): "))
        vib = float(input("Vibração transversal (mm/s) (0 a 10): "))
        corr = float(input("Corrente medida (A) (0 a 450): "))
        torq = float(input("Torque (% da nominal) (0 a 2): "))

        # Validar entradas
        limites = {
            'Umidade': (0, 100),
            'Ruído': (0, 140),
            'Vibração': (0, 10),
            'Corrente': (0, 450),
            'Torque': (0, 2)
        }

        if not (limites['Umidade'][0] <= umid <= limites['Umidade'][1] and
                limites['Ruído'][0] <= ruid <= limites['Ruído'][1] and
                limites['Vibração'][0] <= vib <= limites['Vibração'][1] and
                limites['Corrente'][0] <= corr <= limites['Corrente'][1] and
                limites['Torque'][0] <= torq <= limites['Torque'][1]):
            print("\nERRO: Um ou mais valores fora dos limites permitidos!")
            return

        # Mapeamento de valores para exibição
        input_map = {
            'umidadeInternaDoMotor': umid,
            'ruidoAcustico': ruid,
            'vibracaoTransversal': vib,
            'correnteNominalEmCarga': corr,
            'torqueEntregue': torq
        }

        # Configurar entradas
        for key, value in input_map.items():
            simulador.input[key] = value

        # Processar
        simulador.compute()
        resultado = simulador.output['riscoFalha']

        # Exibir resultados
        print("\n" + "-"*40)
        print("RELATÓRIO DE ANÁLISE:")
        print(f"• Umidade: {umid}%")
        print(f"• Ruído: {ruid} dB")
        print(f"• Vibração: {vib} mm/s")
        print(f"• Corrente: {corr}")
        print(f"• Torque: {torq*100:.1f}%")

        # Calcular pertinências
        print("\nATIVAÇÃO DOS CONJUNTOS FUZZY:")
        for var in [umidade, ruido, vibracao, corrente, torque]:
            print(f"\n{var.label}:")
            valor = input_map[var.label]
            for termo in var.terms:
                grau = fuzz.interp_membership(var.universe, var[termo].mf, valor)
                if grau > 0.001:
                    print(f"  → {termo.ljust(8)}: {grau:.2%}")

        # Classificação final
        print("\n" + "-"*40)
        print(f"RISCO CALCULADO: {resultado:.2f}%")
        if resultado <= 40:
            print("CLASSIFICAÇÃO: BAIXO RISCO")
        elif resultado <= 70:
            print("CLASSIFICAÇÃO: RISCO MÉDIO")
        else:
            print("CLASSIFICAÇÃO: ALTO RISCO")

        # Mostrar gráfico
        risco_falha.view(sim=simulador)

    except ValueError:
        print("\nERRO: Insira apenas valores numéricos!")
    except Exception as e:
        print(f"\nERRO INESPERADO: {str(e)}")

# =============================================
# EXECUÇÃO
# =============================================
if __name__ == "__main__":
    avaliar_risco_motor()
