import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from typing import List, Tuple, Optional


def analisar_crescimento_fitness(df: pd.DataFrame) -> dict:
    """
    Analisa taxa de crescimento de fitness em diferentes fases.

    Divide a simulação em 3 fases e quantifica crescimento em cada uma.

    Args:
        df: DataFrame de histórico da simulação

    Returns:
        dict com: fase1, fase2, fase3 (crescimento em cada fase),
                 e fase_com_maior_crescimento
    """
    # Definir pontos de transição
    n_gens = len(df)
    gen_500 = min(500, n_gens - 1)
    gen_2500 = min(2500, n_gens - 1)

    # Extrair fitness em pontos críticos
    f_init = df['fitness_medio'].iloc[0]
    f_500 = df['fitness_medio'].iloc[gen_500]
    f_2500 = df['fitness_medio'].iloc[gen_2500]
    f_final = df['fitness_medio'].iloc[-1]

    # Calcular crescimento
    crescimento = {
        'fase_I (0-500)': f_500 - f_init,
        'fase_II (500-2500)': f_2500 - f_500,
        'fase_III (2500+)': f_final - f_2500,
        'crescimento_total': f_final - f_init,
    }

    # Qual fase teve maior crescimento?
    fases = ['fase_I (0-500)', 'fase_II (500-2500)', 'fase_III (2500+)']
    fase_maior = max(fases, key=lambda x: crescimento[x])
    crescimento['fase_com_maior_crescimento'] = fase_maior

    return crescimento


def analisar_trade_offs(df: pd.DataFrame) -> dict:
    """
    Analisa correlações entre fenótipos (trade-offs).

    Calcula correlação de Pearson entre pares de fenótipos.
    Trade-offs esperados aparecem como correlações negativas.

    Args:
        df: DataFrame de histórico da simulação

    Returns:
        dict com correlações entre pares de fenótipos
    """
    # Extrair colunas de fenótipos
    fenotipos_cols = [col for col in df.columns if col.startswith('fenotipos_medio_')]
    fenotipos_df = df[fenotipos_cols]

    # Renomear para mais legível
    fenotipos_df.columns = [col.replace('fenotipos_medio_', '') for col in fenotipos_cols]

    # Calcular correlações
    corr = fenotipos_df.corr()

    return corr.to_dict()


def detectar_estrategia_dominante(df: pd.DataFrame) -> dict:
    """
    Detecta qual estratégia evolutiva domina ao final.

    Classifica em: Transmissora, Virulenta, Equilibrada ou Adaptada
    baseado nos fenótipos finais.

    Args:
        df: DataFrame de histórico da simulação

    Returns:
        dict com: estrategia, evidencias (dict com scores)
    """
    # Usar último valor
    ultima_linha = df.iloc[-1]

    vir = ultima_linha['fenotipos_medio_virulencia']
    trn = ultima_linha['fenotipos_medio_transmissibilidade']
    svr = ultima_linha['fenotipos_medio_sobrevivencia']
    cst = ultima_linha['fenotipos_medio_custo_metabolico']
    adp = ultima_linha['fenotipos_medio_adaptabilidade']

    # Scoring para cada estratégia
    scores = {
        'Transmissora': (trn > 0.6) * 2 + (cst > 0.5) * 1 + (vir < 0.7) * 1,
        'Virulenta': (vir > 0.7) * 2 + (trn < 0.5) * 1 + (cst < 0.5) * 1,
        'Equilibrada': (
                               abs(vir - 0.5) < 0.2 and abs(trn - 0.5) < 0.2 and abs(svr - 0.5) < 0.2
                       ) * 3,
        'Adaptada': (adp > 0.7) * 2,
    }

    estrategia = max(scores, key=scores.get)

    return {
        'estrategia': estrategia,
        'evidencias': {
            'virulencia': vir,
            'transmissibilidade': trn,
            'sobrevivencia': svr,
            'custo_metabolico': cst,
            'adaptabilidade': adp,
        },
        'scores': scores,
    }


def calcular_dinamica_diversidade(df: pd.DataFrame) -> dict:
    """
    Analisa dinâmica da diversidade genética ao longo do tempo.

    Calcula: taxa de queda, fase de maior queda, estabilização.

    Args:
        df: DataFrame de histórico da simulação

    Returns:
        dict com: div_inicial, div_final, taxa_queda, estabilizou
    """
    div = df['diversidade_genetica'].values

    div_inicial = div[0]
    div_final = div[-1]

    # Taxa de queda (mudança média por geração)
    taxa_queda = (div_inicial - div_final) / len(div)

    # Detectar estabilização (últimas 500 gerações com mudança < 1%)
    if len(div) > 500:
        div_ultimas = div[-500:]
        mudanca_relativa = np.std(div_ultimas) / np.mean(div_ultimas)
        estabilizou = mudanca_relativa < 0.01
    else:
        estabilizou = None

    return {
        'diversidade_inicial': div_inicial,
        'diversidade_final': div_final,
        'taxa_queda_media': taxa_queda,
        'estabilizou': estabilizou,
    }


def plotar_comparacao_fenotipos(df: pd.DataFrame, arquivo_saida: Optional[str] = None) -> None:
    """
    Plota todos os fenótipos em um único gráfico para comparação.

    Args:
        df: DataFrame de histórico da simulação
        arquivo_saida: Caminho para salvar PNG (opcional)
    """
    fig, ax = plt.subplots(figsize=(14, 7))

    traits = [
        'virulencia',
        'transmissibilidade',
        'sobrevivencia',
        'custo_metabolico',
        'adaptabilidade'
    ]

    colors = ['red', 'blue', 'green', 'orange', 'purple']

    for trait, color in zip(traits, colors):
        col_name = f'fenotipos_medio_{trait}'
        ax.plot(
            df['geracao'],
            df[col_name],
            label=trait.replace('_', ' ').title(),
            linewidth=2,
            color=color,
            alpha=0.8
        )

    ax.set_xlabel('Geração', fontsize=12)
    ax.set_ylabel('Valor Médio', fontsize=12)
    ax.set_title('Evolução Comparada de Todos os Fenótipos', fontsize=14, fontweight='bold')
    ax.legend(loc='best', fontsize=10)
    ax.grid(True, alpha=0.3)
    ax.set_ylim([0, 1])

    plt.tight_layout()

    if arquivo_saida:
        plt.savefig(arquivo_saida, dpi=300)
        print(f"✅ Gráfico salvo em {arquivo_saida}")
    else:
        plt.show()

    plt.close()


def plotar_ambiente_temporal(df: pd.DataFrame, arquivo_saida: Optional[str] = None) -> None:
    """
    Plota variáveis ambientais ao longo do tempo.

    Args:
        df: DataFrame de histórico da simulação
        arquivo_saida: Caminho para salvar PNG (opcional)
    """
    fig, axes = plt.subplots(2, 2, figsize=(14, 10))

    # Temperatura
    ax = axes[0, 0]
    ax.plot(df['geracao'], df['temperatura'], color='red', linewidth=2)
    ax.fill_between(df['geracao'], df['temperatura'].min(), df['temperatura'], alpha=0.3, color='red')
    ax.set_title('Temperatura', fontweight='bold')
    ax.set_ylabel('°C')
    ax.grid(True, alpha=0.3)

    # Densidade de hospedeiros
    ax = axes[0, 1]
    ax.plot(df['geracao'], df['densidade_hospedeiros'], color='blue', linewidth=2)
    ax.fill_between(df['geracao'], 0, df['densidade_hospedeiros'], alpha=0.3, color='blue')
    ax.set_title('Densidade de Hospedeiros', fontweight='bold')
    ax.set_ylabel('Proporção [0,1]')
    ax.grid(True, alpha=0.3)

    # Pressão imunológica
    ax = axes[1, 0]
    ax.plot(df['geracao'], df['pressao_imunologica'], color='green', linewidth=2)
    ax.fill_between(df['geracao'], 0, df['pressao_imunologica'], alpha=0.3, color='green')
    ax.set_title('Pressão Imunológica', fontweight='bold')
    ax.set_ylabel('Força [0,1]')
    ax.grid(True, alpha=0.3)

    # Nutrientes
    ax = axes[1, 1]
    ax.plot(df['geracao'], df['nutrientes'], color='orange', linewidth=2)
    ax.fill_between(df['geracao'], 0, df['nutrientes'], alpha=0.3, color='orange')
    ax.set_title('Nutrientes', fontweight='bold')
    ax.set_ylabel('Disponibilidade [0,1]')
    ax.grid(True, alpha=0.3)

    # Eixo x comum
    for ax in axes.flat:
        ax.set_xlabel('Geração')

    plt.suptitle('Variáveis Ambientais ao Longo da Simulação', fontsize=14, fontweight='bold')
    plt.tight_layout()

    if arquivo_saida:
        plt.savefig(arquivo_saida, dpi=300)
        print(f"✅ Gráfico salvo em {arquivo_saida}")
    else:
        plt.show()

    plt.close()


def exportar_relatorio_texto(df: pd.DataFrame, arquivo_saida: str) -> None:
    """
    Exporta relatório completo em texto com análises.

    Args:
        df: DataFrame de histórico da simulação
        arquivo_saida: Caminho para salvar arquivo .txt
    """
    with open(arquivo_saida, 'w', encoding='utf-8') as f:
        f.write("=" * 70 + "\n")
        f.write("RELATÓRIO COMPLETO DA SIMULAÇÃO\n")
        f.write("=" * 70 + "\n\n")

        # Resumo geral
        f.write("RESUMO GERAL\n")
        f.write("-" * 70 + "\n")
        f.write(f"Gerações executadas: {len(df)}\n")
        f.write(f"População inicial: {df['tamanho'].iloc[0]}\n")
        f.write(f"População final: {df['tamanho'].iloc[-1]}\n\n")

        # Fitness
        f.write("FITNESS\n")
        f.write("-" * 70 + "\n")
        crescimento = analisar_crescimento_fitness(df)
        f.write(f"Fitness inicial: {df['fitness_medio'].iloc[0]:.4f}\n")
        f.write(f"Fitness final: {df['fitness_medio'].iloc[-1]:.4f}\n")
        f.write(f"Melhoria total: {crescimento['crescimento_total']:.4f}\n")
        f.write(f"Fase com maior crescimento: {crescimento['fase_com_maior_crescimento']}\n\n")

        # Diversidade
        f.write("DIVERSIDADE GENÉTICA\n")
        f.write("-" * 70 + "\n")
        div = calcular_dinamica_diversidade(df)
        f.write(f"Diversidade inicial: {div['diversidade_inicial']:.4f}\n")
        f.write(f"Diversidade final: {div['diversidade_final']:.4f}\n")
        f.write(f"Taxa de queda média: {div['taxa_queda_media']:.6f}\n\n")

        # Estratégia dominante
        f.write("ESTRATÉGIA EVOLUTIVA DOMINANTE\n")
        f.write("-" * 70 + "\n")
        estrategia = detectar_estrategia_dominante(df)
        f.write(f"Estratégia: {estrategia['estrategia']}\n")
        f.write(f"Virulência: {estrategia['evidencias']['virulencia']:.4f}\n")
        f.write(f"Transmissibilidade: {estrategia['evidencias']['transmissibilidade']:.4f}\n")
        f.write(f"Sobrevivência: {estrategia['evidencias']['sobrevivencia']:.4f}\n")
        f.write(f"Custo Metabólico: {estrategia['evidencias']['custo_metabolico']:.4f}\n")
        f.write(f"Adaptabilidade: {estrategia['evidencias']['adaptabilidade']:.4f}\n\n")

        # Ambiente final
        f.write("CONDIÇÕES AMBIENTAIS FINAIS\n")
        f.write("-" * 70 + "\n")
        ultima = df.iloc[-1]
        f.write(f"Temperatura: {ultima['temperatura']:.2f}°C\n")
        f.write(f"Densidade de hospedeiros: {ultima['densidade_hospedeiros']:.4f}\n")
        f.write(f"Pressão imunológica: {ultima['pressao_imunologica']:.4f}\n")
        f.write(f"Nutrientes: {ultima['nutrientes']:.4f}\n\n")

        f.write("=" * 70 + "\n")

    print(f"✅ Relatório salvo em {arquivo_saida}")


def comparar_simulacoes(dfs: List[pd.DataFrame], labels: List[str], arquivo_saida: Optional[str] = None) -> None:
    """
    Compara fitness de múltiplas simulações em um único gráfico.

    Útil para comparar efeito de diferentes parâmetros.

    Args:
        dfs: Lista de DataFrames (uma por simulação)
        labels: Lista de rótulos para cada simulação
        arquivo_saida: Caminho para salvar PNG (opcional)
    """
    if len(dfs) != len(labels):
        raise ValueError("Número de DataFrames deve ser igual a número de labels")

    fig, ax = plt.subplots(figsize=(14, 7))

    colors = ['steelblue', 'coral', 'green', 'purple', 'red']

    for df, label, color in zip(dfs, labels, colors[:len(dfs)]):
        ax.plot(
            df['geracao'],
            df['fitness_medio'],
            label=label,
            linewidth=2,
            color=color,
            alpha=0.8
        )

    ax.set_xlabel('Geração', fontsize=12)
    ax.set_ylabel('Fitness Médio', fontsize=12)
    ax.set_title('Comparação de Fitness entre Simulações', fontsize=14, fontweight='bold')
    ax.legend(loc='lower right', fontsize=10)
    ax.grid(True, alpha=0.3)

    plt.tight_layout()

    if arquivo_saida:
        plt.savefig(arquivo_saida, dpi=300)
        print(f"✅ Gráfico salvo em {arquivo_saida}")
    else:
        plt.show()

    plt.close()