"""
============================================================
 SIGEC - Sistema Integrado de Gestao Energetica da Colonia
 Missao Aurora Siger / Colonia Marte
============================================================

Este sistema reune, de forma organizada, tudo o que foi trabalhado na fase:

  1. Organizacao dos dados        -> listas, tabela chave-valor e hierarquia
  2. Regras de decisao (logica)   -> regras booleanas R1,R2,R3,R4 e R5
  3. Analise do uso de energia    -> compara geracao, consumo e reserva
  4. Modelagem e previsao         -> regressao linear simples (minimos quadrados)

O foco esta na logica, na organizacao e na interpretacao.
Nenhuma biblioteca externa e usada: apenas Python.
Toda decisao e deterministica e auditavel (mesma entrada -> mesma saida).
"""


# ============================================================
# 1. ORGANIZACAO DOS DADOS DA COLONIA
# ============================================================

# (a) LISTA  ->  historico cronologico das leituras dos sensores.
#     Serve de base para a previsao por regressao.
historico_vento = [8, 10, 12]      # velocidade do vento (m/s)
historico_energia = [20, 25, 30]   # energia eolica gerada (kW)

# (b) TABELA CHAVE-VALOR  ->  estado atual (instantaneo) da base.
#     Permite consulta direta e rapida de cada grandeza.
estado_atual = {
    "geracao": 45,
    "consumo": 60,
    "reserva": 30,
    "clima": "OK",
}

# Inventario de subsistemas (Quadro 1 do relatorio).
# Cada subsistema guarda tipo, capacidade, prioridade e se e essencial.
# Quanto MENOR a prioridade, mais critico (1 = nunca desliga).
subsistemas = {
    "LIFE": {"tipo": "consumo_essencial",     "capacidade": 18,  "prioridade": 1, "essencial": True},
    "MED":  {"tipo": "consumo_essencial",     "capacidade": 10,  "prioridade": 2, "essencial": True},
    "SOL":  {"tipo": "geracao",               "capacidade": 60,  "prioridade": 3, "essencial": False},
    "WIND": {"tipo": "geracao",               "capacidade": 40,  "prioridade": 4, "essencial": False},
    "BAT":  {"tipo": "reserva",               "capacidade": 200, "prioridade": 5, "essencial": False},
    "SCI":  {"tipo": "consumo_nao_essencial", "capacidade": 25,  "prioridade": 6, "essencial": False},
    "LOG":  {"tipo": "consumo_nao_essencial", "capacidade": 5,   "prioridade": 7, "essencial": False}, 
}

# (c) ORGANIZACAO HIERARQUICA  ->  representa a colonia como uma arvore,
# separando geracao, armazenamento e consumo (Figura 1 do relatorio).
arvore_energetica = {
    "SISTEMA ENERGETICO": {
        "Geracao": {
            "Solar (SOL)": "60 kW",
            "Eolica (WIND)": "40 kW",
        },
        "Armazenamento": {
            "Baterias (BAT)": "200 kWh",
        },
        "Consumo": {
            "Essencial": {
                "Suporte a Vida (LIFE)": "18 kW",
                "Modulo Medico (MED)": "10 kW",
            },
            "Nao essencial": {
                "Laboratorio (SCI)": "25 kW",
                "Logistica (LOG)": "5 kW",
            },
        },
    }
}


# ============================================================
# 2. REGRAS DE DECISAO E LOGICA DO SISTEMA (secao 3)
# ============================================================

def aplicar_regras_decisao(energia, consumo):
    """
    Aplica as regras de decisao do SIGEC (Quadro 2).

    Parte de uma regra simples (R1) e combina condicoes com o
    operador E (and) quando necessario (R2).

    Retorna:
      - mensagens : lista de acoes/alertas gerados
      - modo_economia : True se o MODO ECONOMIA foi ativado
    """
    mensagens = []
    modo_economia = False

    # R2 - Combinada: energia < 50 E consumo > 60
    if energia < 50 and consumo > 60:
        mensagens.append("MODO ECONOMIA ATIVADO")
        modo_economia = True
    # R1 - Basica: energia < 50  (so alerta se nao caiu no modo economia)
    elif energia < 50:
        mensagens.append("ALERTA: reduzir consumo")

    return mensagens, modo_economia


def priorizar_cargas(subsistemas):
    """
    R3 - Priorizacao e suporte a vida (secao 3.2).

    Quando o MODO ECONOMIA esta ativo, mantem os subsistemas
    essenciais (LIFE/MED) ligados e desliga os nao essenciais (SCI/LOG).
    Decisoes automaticas nunca comprometem vidas humanas.
    """
    mantidos = []
    desligados = []
    for nome, dados in subsistemas.items():
        # so faz sentido ligar/desligar cargas de consumo
        if dados["tipo"].startswith("consumo"):
            if dados["essencial"]:
                mantidos.append(nome)
            else:
                desligados.append(nome)
    return mantidos, desligados


def avaliar_balanco(geracao, consumo):
    """
    R4 / R5 - Balanco entre geracao e consumo (Quadro 2).
    """
    if consumo > geracao:
        return "RISCO: deficit energetico"
    elif geracao > consumo:
        return "SUGESTAO: armazenar excedente"
    else:
        return "OPERACAO NORMAL"


# ============================================================
# 3. ANALISE DO USO DE ENERGIA (secao 3.3)
# ============================================================

def analisar_uso_energia(geracao, consumo, reserva=0, margem=10):
    """
    Compara geracao, consumo e reserva e gera uma acao clara (Quadro 3).

    A 'margem' define uma pequena faixa de tolerancia: diferencas pequenas
    entre geracao e consumo sao tratadas como EQUILIBRIO (operacao normal).

    Retorna uma tupla (situacao, saida_do_sistema).
    """
    diferenca = geracao - consumo

    # Geracao e consumo praticamente iguais -> equilibrio
    if abs(diferenca) <= margem:
        return ("Equilibrio", "OPERACAO NORMAL")

    # Sobra de energia -> armazenar
    if diferenca > 0:
        return ("Superavit", "SUGESTAO: armazenar energia excedente")

    # Falta energia: verifica se a reserva cobre o deficit
    deficit = -diferenca
    if reserva >= deficit:
        return ("Deficit coberto", "MODO ECONOMIA + uso da reserva")
    else:
        return ("Deficit", "ALERTA: consumo maior que geracao")


# ============================================================
# 4. MODELAGEM E PREVISAO DE ENERGIA (secao 4)
# ============================================================

def calcular_regressao(xs, ys):
    """
    Regressao linear simples pelo metodo dos minimos quadrados.

    Ajusta a reta E(v) = a*v + b a partir das listas historicas.

        a = soma((vi - media_v) * (Ei - media_E)) / soma((vi - media_v)^2)
        b = media_E - a * media_v

    Retorna os coeficientes (a, b).
    """
    n = len(xs)
    media_x = sum(xs) / n
    media_y = sum(ys) / n

    numerador = 0
    denominador = 0
    for i in range(n):
        numerador += (xs[i] - media_x) * (ys[i] - media_y)
        denominador += (xs[i] - media_x) ** 2

    a = numerador / denominador
    b = media_y - a * media_x
    return a, b


def prever_energia(a, b, v):
    """Usa a reta ajustada para estimar a energia para um vento 'v'."""
    return a * v + b


# ============================================================
# 5. FUNCAO AUXILIAR: navegar/exibir a hierarquia
# ============================================================

def mostrar_hierarquia(no, nivel=0):
    """Percorre a arvore de subsistemas e imprime de forma indentada."""
    recuo = "   " * nivel
    if isinstance(no, dict):
        for chave, valor in no.items():
            if isinstance(valor, dict):
                print(recuo + "- " + chave)
                mostrar_hierarquia(valor, nivel + 1)
            else:
                print(recuo + "- " + chave + ": " + str(valor))


# ============================================================
# 6. DEMONSTRACAO (reproduz os cenarios do relatorio)
# ============================================================

def main():
    print("=" * 60)
    print(" SIGEC - Sistema Integrado de Gestao Energetica da Colonia")
    print("=" * 60)

    # ---- Organizacao dos dados -------------------------------------
    print("\n[1] ESTADO ATUAL DA BASE (tabela chave-valor):")
    for chave, valor in estado_atual.items():
        print("   ", chave, "=", valor)

    print("\n[1] HISTORICO DOS SENSORES (listas):")
    print("    vento   =", historico_vento)
    print("    energia =", historico_energia)

    print("\n[1] ORGANIZACAO HIERARQUICA (arvore de subsistemas):")
    mostrar_hierarquia(arvore_energetica)

    # ---- Cenarios de analise de uso de energia (Quadro 3) ----------
    print("\n[3] ANALISE DO USO DE ENERGIA:")
    cenarios = [
        (40, 70, 0),
        (80, 30, 0),
        (45, 60, 30),
        (55, 50, 80),
    ]
    for geracao, consumo, reserva in cenarios:
        situacao, saida = analisar_uso_energia(geracao, consumo, reserva)
        print(f"    geracao={geracao:<3} consumo={consumo:<3} reserva={reserva:<3}"
              f" -> {situacao}: {saida}")

    # ---- Regras de decisao (exemplo do relatorio) ------------------
    print("\n[2] REGRAS DE DECISAO  (entrada: energia=40, consumo=70):")
    mensagens, modo_economia = aplicar_regras_decisao(energia=40, consumo=70)
    for m in mensagens:
        print("    ->", m)
    if modo_economia:
        mantidos, desligados = priorizar_cargas(subsistemas)
        print("    -> R3 Priorizacao: MANTER", mantidos, "| DESLIGAR", desligados)

    # ---- Previsao por regressao (secao 4) --------------------------
    print("\n[4] PREVISAO POR REGRESSAO LINEAR:")
    a, b = calcular_regressao(historico_vento, historico_energia)
    print(f"    Reta ajustada: E(v) = {a} * v + {b}")
    vento_futuro = 11
    previsao = prever_energia(a, b, vento_futuro)
    print(f"    Para vento = {vento_futuro} m/s  ->  previsao = {previsao} kW"
          f"  (~{round(previsao)} kW)")

    # ---- Resumo dos cenarios (Quadro 5) ----------------------------
    print("\n[*] RESUMO DOS CENARIOS VERIFICADOS:")
    print("    1) geracao=40, consumo=70 ->", analisar_uso_energia(40, 70)[1])
    print("    2) geracao=80, consumo=30 ->", analisar_uso_energia(80, 30)[1])
    print("    3) energia=40, consumo=70 ->", aplicar_regras_decisao(40, 70)[0][0])
    print("    4) vento=11 m/s           -> previsao ~",
          round(prever_energia(a, b, 11), 1), "kW")

    print("\n" + "=" * 60)
    print(" Execucao concluida com sucesso.")
    print("=" * 60)


if __name__ == "__main__":
    main()
