#!/usr/bin/env python3
"""
Black Death Evolution Simulator - Script Principal

Executa simulações evolutivas de Yersinia pestis com configurações personalizáveis.

Uso:
    python scripts/run_simulation.py                    # Configuração padrão
    python scripts/run_simulation.py --pop-size 5000    # População customizada
    python scripts/run_simulation.py --help             # Ver todas as opções
"""

import argparse
import os
import sys
from pathlib import Path

# Adicionar raiz do projeto ao path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.simulation import Simulation
from src import utils


def criar_diretorios():
    """Cria estrutura de diretórios se não existir."""
    os.makedirs('outputs/data', exist_ok=True)
    os.makedirs('outputs/plots', exist_ok=True)


def main():
    """Função principal."""
    # ===== PARSE ARGUMENTOS =====
    parser = argparse.ArgumentParser(
        description='Black Death Evolution Simulator - Simula evolução de Yersinia pestis',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Exemplos:
  python scripts/run_simulation.py
  python scripts/run_simulation.py --pop-size 5000 --generations 2000
  python scripts/run_simulation.py --mutation-rate 1e-6 --seed 42
        """
    )

    parser.add_argument(
        '--pop-size',
        type=int,
        default=10000,
        help='Tamanho da população (padrão: 10000)'
    )

    parser.add_argument(
        '--generations',
        type=int,
        default=5000,
        help='Número de gerações (padrão: 5000)'
    )

    parser.add_argument(
        '--mutation-rate',
        type=float,
        default=1e-7,
        help='Taxa de mutação por gene por divisão (padrão: 1e-7)'
    )

    parser.add_argument(
        '--threshold',
        type=float,
        default=0.001,
        help='Threshold mínimo de fitness para sobreviver (padrão: 0.001)'
    )

    parser.add_argument(
        '--seed',
        type=int,
        default=None,
        help='Seed para reprodutibilidade (opcional)'
    )

    parser.add_argument(
        '--output-name',
        type=str,
        default='simulacao',
        help='Nome do arquivo de saída (padrão: simulacao)'
    )

    parser.add_argument(
        '--no-plots',
        action='store_true',
        help='Não gerar gráficos (apenas CSV)'
    )

    parser.add_argument(
        '--no-verbose',
        action='store_true',
        help='Modo silencioso (sem output durante execução)'
    )

    parser.add_argument(
        '--full-report',
        action='store_true',
        help='Gerar relatório completo em texto'
    )

    args = parser.parse_args()

    # ===== CRIAR DIRETÓRIOS =====
    criar_diretorios()

    # ===== HEADER =====
    print("\n" + "=" * 70)
    print("BLACK DEATH EVOLUTION SIMULATOR")
    print("=" * 70)
    print(f"\nConfigurações:")
    print(f"  População: {args.pop_size}")
    print(f"  Gerações: {args.generations}")
    print(f"  Taxa de mutação: {args.mutation_rate}")
    print(f"  Threshold fitness: {args.threshold}")
    if args.seed:
        print(f"  Seed: {args.seed}")
    print(f"\nOutput: outputs/data/{args.output_name}.csv")
    print("=" * 70 + "\n")

    # ===== CRIAR E EXECUTAR SIMULAÇÃO =====
    try:
        sim = Simulation(
            tamanho_populacao=args.pop_size,
            num_geracoes=args.generations,
            taxa_mutacao=args.mutation_rate,
            threshold_fitness=args.threshold,
            seed=args.seed
        )

        verbose = not args.no_verbose
        df = sim.executar(verbose=verbose)

        # ===== SALVAR RESULTADOS =====
        arquivo_csv = f'outputs/data/{args.output_name}.csv'
        sim.salvar_resultados(arquivo_csv)

        # ===== GERAR VISUALIZAÇÕES =====
        if not args.no_plots:
            print("\nGerando visualizações...")
            sim.gerar_visualizacoes('outputs/plots/')

        # ===== GERAR RELATÓRIO COMPLETO (OPCIONAL) =====
        if args.full_report:
            print("Gerando relatório completo...")
            arquivo_relatorio = f'outputs/data/{args.output_name}_relatorio.txt'
            utils.exportar_relatorio_texto(df, arquivo_relatorio)

            # Gráficos adicionais
            utils.plotar_comparacao_fenotipos(
                df,
                f'outputs/plots/{args.output_name}_fenotipos_comparacao.png'
            )
            utils.plotar_ambiente_temporal(
                df,
                f'outputs/plots/{args.output_name}_ambiente.png'
            )

        # ===== RESUMO FINAL =====
        sim.imprimir_resumo()

        # ===== ANÁLISES ADICIONAIS =====
        print("\nAnálises Adicionais:")
        print("-" * 70)

        # Crescimento de fitness por fase
        crescimento = utils.analisar_crescimento_fitness(df)
        print(f"\nCrescimento de Fitness por Fase:")
        print(f"  Fase I (0-500):       {crescimento['fase_I (0-500)']:.6f}")
        print(f"  Fase II (500-2500):   {crescimento['fase_II (500-2500)']:.6f}")
        print(f"  Fase III (2500+):     {crescimento['fase_III (2500+)']:.6f}")
        print(f"  Fase com maior crescimento: {crescimento['fase_com_maior_crescimento']}")

        # Estratégia dominante
        estrategia = utils.detectar_estrategia_dominante(df)
        print(f"\nEstratégia Evolutiva Dominante: {estrategia['estrategia']}")
        print(f"  Virulência: {estrategia['evidencias']['virulencia']:.4f}")
        print(f"  Transmissibilidade: {estrategia['evidencias']['transmissibilidade']:.4f}")
        print(f"  Sobrevivência: {estrategia['evidencias']['sobrevivencia']:.4f}")
        print(f"  Custo Metabólico: {estrategia['evidencias']['custo_metabolico']:.4f}")
        print(f"  Adaptabilidade: {estrategia['evidencias']['adaptabilidade']:.4f}")

        # Dinâmica de diversidade
        div = utils.calcular_dinamica_diversidade(df)
        print(f"\nDiversidade Genética:")
        print(f"  Inicial: {div['diversidade_inicial']:.4f}")
        print(f"  Final: {div['diversidade_final']:.4f}")
        print(f"  Taxa de queda média: {div['taxa_queda_media']:.6f}")
        if div['estabilizou'] is not None:
            status = "Sim" if div['estabilizou'] else "Não"
            print(f"  Estabilizou? {status}")

        print("\n" + "=" * 70)
        print("SIMULAÇÃO CONCLUÍDA COM SUCESSO!")
        print("=" * 70 + "\n")

    except KeyboardInterrupt:
        print("\n\nSimulação interrompida pelo usuário.")
        exit(1)

    except Exception as e:
        print(f"\n\nERRO: {str(e)}")
        import traceback
        traceback.print_exc()
        exit(1)


if __name__ == '__main__':
    main()