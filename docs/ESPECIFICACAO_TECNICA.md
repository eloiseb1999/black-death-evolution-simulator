# Especificação Técnica

## Visão Geral

O simulador implementa um algoritmo evolutivo para modelar a dinâmica populacional de *Yersinia pestis* sob pressões seletivas ambientais. A simulação combina genética quantitativa (12 genes abstratos), fenótipos emergentes, função de fitness multi-dimensional, e dinâmica ambiental temporal.

Desenvolvido em Python 3.9+ segundo princípios orientados a objetos, com três classes principais: `Bacteria` (indivíduo), `Population` (agregado), `Environment` (contexto), coordenadas pela classe `Simulation`.

---

## Representação Genética e Fenótipos

### Genoma

Cada indivíduo da classe `Bacteria` mantém um genoma de 12 genes contínuos, onde cada alelo $g_i \in [0,1]$ representa grau de divergência do genótipo selvagem. O valor 0 corresponde ao alelo ancestral; 1 ao alelo derivado mutante.

Os 12 genes organizam-se em cinco grupos funcionais (Tabela 1):

| Grupo | Índices | Fenótipo | Descrição Biológica |
|-------|---------|----------|-----------|
| A | 0-1 | Virulência | Fatores de invasão (LPS, toxinas, proteases) |
| B | 2-3 | Transmissibilidade | Capacidade de dispersão inter-hospedeiro |
| C | 4-5 | Sobrevivência | Evasão/tolerância a defesas imunológicas |
| D | 6-8 | Custo Metabólico | Investimento energético relativo |
| E | 9-11 | Adaptabilidade | Plasticidade fenotípica em ambientes variáveis |

### Fenótipos Emergentes

A propriedade `fenotipos` da classe `Bacteria` calcula cada característica como agregação linear dos genes do seu grupo:

$$\text{Fenótipo}_f = \frac{1}{n} \sum_{i \in \text{Grupo}_f} g_i$$

cada fenótipo resultante situa-se em [0,1]. A organização poligênica reflete realidade biológica onde características complexas envolvem múltiplos loci.

---

## Função de Fitness e Pressão Seletiva

### Fitness Base

O método `calcular_fitness(ambiente)` da classe `Bacteria` implementa:

$$F = S \times T \times (1 - C) \times A \times f_{amb}$$

onde $S$, $T$, $C$, $A$ são fenótipos calculados conforme seção anterior. A estrutura multiplicativa assegura que qualquer fenótipo severamente deficiente reduz drasticamente o fitness, capturando dependências biológicas críticas.

### Pressão Seletiva Ambiental

O método `calcular_pressao_seletiva(bacteria)` da classe `Environment` calcula o fator multiplicativo:

$$f_{amb} = f_{temp} \times f_{host} \times f_{imune} \times f_{nut}$$

onde cada componente é derivado de variáveis ambientais mantidas em `Environment`:

- $f_{temp}$: preferência térmica, ótimo em 18°C (máximo quando $|T - 18| < 5$)
- $f_{host}$: densidade de hospedeiros disponíveis (`densidade_hospedeiros`)
- $f_{imune}$: $(1 - \text{pressao\_imunologica} \times \text{virulencia})$, capturando que hospedeiros com resposta forte eliminam bactérias virulentas
- $f_{nut}$: disponibilidade de nutrientes (`nutrientes`)

Assim, o fitness final modula-se dinamicamente conforme condições ambientais evoluem durante simulação.

---

## Trade-offs Evolutivos

O modelo incorpora conflitos biológicos que emergem naturalmente da função de fitness.

**Virulência vs. Transmissibilidade**: Alta virulência causa dano intenso, reduzindo período de viabilidade no hospedeiro e ativando resposta imunológica forte (penalizando fitness via $f_{imune}$). Contrasta com estratégia de baixa virulência, que prolonga período de transmissão mas aumenta risco de eliminação pelo sistema imune prolongado.

**Transmissibilidade vs. Custo**: Elevada transmissibilidade demanda investimento em estruturas especializadas, aumentando $C$, que reduz fitness multiplicativamente.

**Adaptabilidade vs. Eficiência**: Alta adaptabilidade permite ajuste a ambientes variáveis, porém reduz eficiência em nicho específico. Esta dicotomia força trade-off entre robustez e otimalidade local.

Estes conflitos geram espaço fenotípico multidimensional onde múltiplas estratégias evolutivas podem coexistir com sucesso variável conforme contexto ambiental.

---

## Dinâmica Mutacional

O método `reproduzir(taxa_mutacao)` implementa fissão binária assexuada. Cada divisão produz um clone do genoma parental. Para cada gene, há probabilidade $\mu$ de ocorrer mutação:

$$g'_i = \text{clamp}(g_i + \Delta g_i, 0, 1), \quad \text{onde} \quad \Delta g_i \sim \mathcal{N}(0, \sigma^2)$$

com $\mu = 10^{-7}$ (padrão) e $\sigma = 0.05$. Esta taxa aproxima estimativas empíricas para *Yersinia pestis* real (~10⁻⁷ por nucleotídeo por divisão). A distribuição normal com pequeno desvio padrão permite mutações pequenas (ajustes finos) e maiores (explorações), equilibrando micro e macroevolução.

---

## Classe Bacteria

Representa um genótipo individual. Implementada como dataclass para imutabilidade parcial.

```python
@dataclass
class Bacteria:
    genoma: np.ndarray          # 12 genes, cada um em [0, 1]
    idade: int = 0
    geracao_nascimento: int = 0
```

**Propriedades:**
- `fenotipos`: dict que calcula as cinco características agregando genes por grupo funcional

**Métodos:**
- `calcular_fitness(ambiente: Environment) → float`: computa aptidão conforme modelagem, considerando genótipo e contexto ambiental
- `reproduzir(taxa_mutacao: float) → Bacteria`: fissão binária com mutação estocástica
- `clonar() → Bacteria`: produz cópia exata (sem alterações)

---

## Classe Population

Gerencia conjunto de indivíduos e implementa operações coletivas.

```python
class Population:
    individuos: List[Bacteria]
    tamanho_inicial: int
```

**Métodos:**
- `selecionar_naturalmente(ambiente: Environment, threshold: float) → List[Bacteria]`: filtra indivíduos com fitness ≥ threshold
- `reproduzir(taxa_mutacao: float, tamanho_alvo: int) → Population`: cria nova geração; sobreviventes se dividem até restaurar tamanho
- `calcular_estatisticas(ambiente: Environment) → dict`: retorna agregações (média, desvio padrão, máximo, mínimo de fitness; diversidade genética; fenótipos médios)
- `melhor_individuo(ambiente: Environment) → Bacteria`: retorna indivíduo com máximo fitness
- `diversidade_genetica() → float`: calcula variância inter-populacional nos genes

---

## Classe Environment

Modela parâmetros contextuais que variam ao longo das gerações.

```python
class Environment:
    geracao: int
    temperatura: float              # [10, 30] °C
    densidade_hospedeiros: float    # [0, 1]
    pressao_imunologica: float      # [0, 1]
    nutrientes: float               # [0, 1]
```

**Métodos:**
- `avanca_tempo(delta_geracao: int = 1)`: atualiza parâmetros ambientais segundo dinâmica temporal
  - Temperatura: ciclo sazonal sinusoidal
  - Densidade de hospedeiros: crescimento em epidemia (0-2500), colapso posterior (2500+)
  - Pressão imunológica: aumenta progressivamente com o tempo
  - Nutrientes: flutuações aleatórias

- `calcular_pressao_seletiva(bacteria: Bacteria) → float`: retorna fator multiplicativo ambiental para o indivíduo

### Dinâmica Ambiental Temporal

| Fase | Gerações | $f_{host}$ | $f_{imune}$ | Contexto |
|------|----------|-----------|-----------|-----------|
| I | 0-500 | 0.1→0.2 | 0.1 | Introdução |
| II | 500-2500 | 0.2→0.7 | 0.3→0.6 | Epidemia |
| III | 2500+ | 0.7→0.05 | 0.6→0.9 | Controle/colapso |

---

## Classe Simulation

Orquestra a execução completa da simulação através de múltiplas gerações.

```python
class Simulation:
    populacao: Population
    ambiente: Environment
    historico: List[Dict]
    parametros: Dict
```

**Fluxo de execução:**

```
Para cada geração g = 0 até num_geracoes:
    1. sobreviventes ← populacao.selecionar_naturalmente(ambiente, threshold)
    2. populacao ← sobreviventes.reproduzir(taxa_mutacao, tamanho_alvo)
    3. ambiente.avanca_tempo()
    4. stats ← populacao.calcular_estatisticas(ambiente)
    5. historico.append(stats)
```

**Métodos:**
- `executar(verbose: bool = True) → pd.DataFrame`: roda simulação; retorna DataFrame com histórico
- `salvar_resultados(arquivo_csv: str)`: persiste histórico em CSV
- `gerar_visualizacoes(pasta_saida: str)`: produz gráficos matplotlib

---

## Parâmetros de Configuração

| Parâmetro | Default | Intervalo | Descrição |
|-----------|---------|-----------|-----------|
| `tamanho_populacao` | 10000 | [100, 1M] | Indivíduos por geração |
| `num_geracoes` | 5000 | [100, 10k] | Ciclos reprodutivos totais |
| `taxa_mutacao` | 1e-7 | [1e-9, 1e-5] | Probabilidade por gene por divisão |
| `threshold_fitness` | 0.1 | [0.0, 1.0] | Mínimo fitness para sobrevivência |
| `seed` | None | int ou None | Reprodutibilidade estocástica |

---

## Padrões Evolutivos Esperados

Simulações sob configuração padrão produzem padrões previsíveis:

**Fase inicial (0-500 gerações)**: Crescimento rápido de fitness. População inicial aleatória, não-otimizada. Diversidade genética elevada.

**Fase de exploração (500-2000 gerações)**: Taxa de crescimento desacelera. População razoavelmente otimizada. Linhagens especializadas emergem e competem.

**Fase de convergência (2000-4000 gerações)**: Crescimento lento. Uma ou poucas estratégias dominam. Diversidade genética diminui.

**Platô (4000+ gerações)**: Fitness estabiliza. População próxima a máximo local.

Este padrão (rápido → moderado → lento → platô) replica comportamentos de linhagens bacterianas sob seleção laboratorial, validando a estrutura do modelo.

---

## Formato de Output

Resultados persistem em CSV com uma linha por geração:

```
geracao, fitness_medio, fitness_desvio, fitness_max, fitness_min,
diversidade_genetica, tamanho, temperatura, densidade_hospedeiros,
pressao_imunologica, nutrientes, fenotipos_medio_virulencia,
fenotipos_medio_transmissibilidade, [...]
```

Visualizações incluem: (i) série temporal de fitness; (ii) dinâmica populacional; (iii) evolução dos cinco fenótipos.

---

## Análise de Complexidade

Complexidade por geração: O(P log P), onde P é tamanho populacional.

Complexidade total para N gerações: O(N · P log P)

Exemplo: P = 10⁴, N = 5000 → ~10⁹ operações, ~2-5 minutos em CPU moderna.

Uso de memória: ~10 MB.

---

## Dependências

```
numpy >= 1.24
pandas >= 2.0
matplotlib >= 3.7
scipy >= 1.11
```

---

## Validação e Limitações

O modelo é validado biologicamente por (i) replicar padrões de crescimento de fitness esperados; (ii) demonstrar redução em diversidade genética com aumento em aptidão; (iii) permitir emergência espontânea de trade-offs.

Limitações: (i) dimensionalidade reduzida (12 genes vs. ~4600 reais); (ii) interações gênicas aditivas, ignorando epistasia; (iii) população bem-misturada, ignorando estrutura espacial; (iv) dinâmica de hospedeiro abstrata.

Estas simplificações são necessárias para viabilidade computacional, preservando porém princípios essenciais de evolução por seleção natural.