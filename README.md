# SIGEC — Sistema Integrado de Gestão Energética da Colônia

---

## Nome da "Equipe" e RM do Integrante.

| Nome | RM |
|------|----|
| João Pedro | 572908 |

---

## Resumo do Problema e Cenário Analisado

O SIGEC representa o funcionamento inteligente da infraestrutura energética da **Colônia Marte**. O cenário simula uma base espacial que precisa gerenciar de forma autônoma e determinística sua geração, consumo e reserva de energia, priorizando sempre o suporte à vida humana.

O sistema recebe dados dos sensores da colônia (velocidade do vento, energia gerada, consumo atual) e toma decisões automáticas sobre o modo de operação, desligamento de sistemas não essenciais e armazenamento de excedentes.

---

## Estruturas de Dados: Quais Foram Usadas e Por Quê

| Estrutura | Uso no Sistema | Justificativa |
|-----------|---------------|---------------|
| **Lista** | Histórico cronológico dos sensores (`vento`, `energia`) | Permite registrar e iterar dados ao longo do tempo para alimentar a regressão linear |
| **Dicionário (tabela chave-valor)** | Estado atual da base (`geração`, `consumo`, `reserva`, `clima`) | Acesso direto por chave; ideal para representar o estado instantâneo da colônia |
| **Árvore (hierarquia)** | Subsistemas separados em geração, armazenamento e consumo | Organiza os componentes de forma hierárquica, facilitando a priorização de cargas |

---

## Regras Lógicas Principais do Diagnóstico

O sistema aplica cinco regras booleanas determinísticas (R1 a R5):

- **R1** — Se `energia < 50` E `consumo > 60` → **MODO ECONOMIA ATIVADO**
- **R2** — Se `reserva < 20` → **ALERTA CRÍTICO DE RESERVA**
- **R3** — Priorização de cargas: manter `['LIFE', 'MED']` | desligar `['SCI', 'LOG']`
- **R4** — Se `geração > consumo` → **SUGESTÃO: armazenar energia excedente**
- **R5** — Se `geração < consumo` E `reserva > 0` → **USO DE RESERVA AUTORIZADO**

Toda decisão é **auditável**: a mesma entrada sempre produz a mesma saída.

---

## Técnica de Previsão Utilizada e Resultado

**Técnica:** Regressão Linear Simples pelo método dos Mínimos Quadrados, implementada manualmente sem bibliotecas externas.

**Como funciona:**  
A partir do histórico de pares `(vento, energia)`, o sistema ajusta uma reta `E(v) = a * v + b` e usa essa equação para prever a geração futura dado um novo valor de vento.

**Exemplo de resultado:**

```
Histórico: vento = [8, 10, 12]  |  energia = [20, 25, 30]
Reta ajustada:  E(v) = 2.5 * v + 0
Entrada:  vento = 11 m/s
Saída:    previsão ≈ 27,5 kW
```

---

## Como Executar

```bash
python src/sigec.py
```

O programa imprime no terminal:
- Organização dos dados da colônia
- Cenários de análise energética
- Regras de decisão aplicadas
- Previsão por regressão linear

---

## Exemplo de Entrada e Saída do Sistema

### Regra de Decisão
```
Entrada:  energia = 40, consumo = 70
Saída:    MODO ECONOMIA ATIVADO
          R3 -> MANTER ['LIFE', 'MED'] | DESLIGAR ['SCI', 'LOG']
```

### Análise de Balanço Energético
```
Entrada:  geração = 80, consumo = 30
Saída:    SUGESTÃO: armazenar energia excedente
```

### Previsão por Regressão Linear
```
Entrada:  vento = 11 m/s
Saída:    previsão ≈ 27,5 kW
```

---

## Recomendações Geradas pelo Sistema

Com base nas regras aplicadas, o sistema pode gerar as seguintes recomendações automáticas:

- Ativar **modo economia** quando energia disponível for baixa e consumo alto
- **Preservar sistemas de suporte à vida** (`LIFE`, `MED`) em qualquer cenário
- **Desligar sistemas não essenciais** (`SCI`, `LOG`) em situação crítica
- **Armazenar excedente** sempre que geração superar o consumo
- **Emitir alerta crítico** quando reserva cair abaixo do limiar seguro

---

## Link do Vídeo no YouTube

> Link para o video: `https://youtu.be/PKOqSEqW918`

---

## Conclusões e Aprendizados

O desenvolvimento do SIGEC demonstrou na prática como estruturas de dados simples listas, dicionários e árvores são suficientes para modelar sistemas complexos de tomada de decisão. A implementação manual da regressão linear reforçou o entendimento do método dos mínimos quadrados sem depender de bibliotecas externas.

Os principais aprendizados foram:
- A importância de sistemas **determinísticos e auditáveis** em ambientes críticos
- Como **priorização de cargas** pode ser implementada com lógica booleana direta
- A aplicação prática de **regressão linear** para previsão em séries de dados simples
- Organização de código em funções bem definidas melhora a legibilidade e manutenção

---

## Estrutura do Projeto

```
projeto/
│
├── README.md
│
├── src/
│   └── sigec.py
│
├── data/
│   └── dados.csv
│
└── docs/
    ├── relatorio.pdf
    ├── link_video.txt
    └── uso_ia.md
```