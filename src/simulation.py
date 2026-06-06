import pandas as pd
import numpy as np
import random
from typing import Optional, List
from src.population import Population
from src.environment import Environment


class Simulation:
    """
    Orquestra a execução completa da simulação evolutiva.

    Coordena Population e Environment através de múltiplas gerações,
    implementando o ciclo: seleção → reprodução → evolução ambiental.

    Attributes:
        populacao: Instance de Population
        ambiente: Instance de Environment
        historico: Lista de dicts com estatísticas por geração
        parametros: Dict com configuração da simulação
    """

    def __init__(
            self,
            tamanho_populacao: int = 10000,
            num_geracoes: int = 5000,
            taxa_mutacao: float = 1e-7,
            threshold_fitness: float = 0.001,
            seed: Optional[int] = None
    ):
        """
        Inicializa simulação.

        Args:
            tamanho_populacao: Indivíduos por geração (padrão: 10000)
            num_geracoes: Número total de gerações (padrão: 5000)
            taxa_mutacao: Prob. de mutação/gene/divisão (padrão: 1e-7)
            threshold_fitness: Mínimo fitness para sobreviver (padrão: 0.001)
            seed: Seed para reprodutibilidade (opcional)
        """
        if seed is not None:
            np.random.seed(seed)
            random.seed(seed)

        self.populacao = Population(
            tamanho=tamanho_populacao,
            genoma_aleatorio=True,
            seed=seed
        )
        self.ambiente = Environment(geracao_inicial=0, seed=seed)
        self.historico: List[dict] = []

        self.parametros = {
            'tamanho_populacao': tamanho_populacao,
            'num_geracoes': num_geracoes,
            'taxa_mutacao': taxa_mutacao,
            'threshold_fitness': threshold_fitness,
        }

    def executar(self, verbose: bool = True) -> pd.DataFrame:
        """
        Executa a simulação por todas as gerações.

        Fluxo por geração:
        1. Selecionar indivíduos com fitness ≥ threshold
        2. Reproduzir sobreviventes (fissão + mutação)
        3. Avançar tempo ambiental
        4. Registrar estatísticas

        Args:
            verbose: Se True, printa progresso a cada 100 gerações

        Returns:
            DataFrame pandas com histórico de estatísticas
        """
        for gen in range(self.parametros['num_geracoes']):
            # ===== 1. SELEÇÃO NATURAL =====
            sobreviventes = self.populacao.selecionar_naturalmente(
                self.ambiente,
                self.parametros['threshold_fitness']
            )

            # Verificar extinção
            if not sobreviventes:
                if verbose:
                    print(
                        f"Geração {gen}: EXTINÇÃO da população "
                        f"(nenhum fitness ≥ {self.parametros['threshold_fitness']})"
                    )
                break

            # ===== 2. REPRODUÇÃO =====
            # Criar nova população a partir dos sobreviventes
            self.populacao = Population(tamanho=0)
            self.populacao.individuos = sobreviventes
            self.populacao.tamanho_inicial = self.parametros['tamanho_populacao']

            nova_pop = self.populacao.reproduzir(
                taxa_mutacao=self.parametros['taxa_mutacao'],
                tamanho_alvo=self.parametros['tamanho_populacao']
            )
            self.populacao = nova_pop

            # ===== 3. EVOLUÇÃO AMBIENTAL =====
            self.ambiente.avanca_tempo(delta_geracao=1)

            # ===== 4. REGISTRAR ESTATÍSTICAS =====
            stats = self.populacao.calcular_estatisticas(self.ambiente)
            stats['geracao'] = gen

            # Adicionar variáveis ambientais
            stats.update(self.ambiente.obter_estado_atual())

            # Achatar fenótipos_medio para CSV
            fenotipos = stats.pop('fenotipos_medio')
            for key, value in fenotipos.items():
                stats[f'fenotipos_medio_{key}'] = value

            self.historico.append(stats)

            # ===== 5. OUTPUT =====
            if verbose and (gen % 100 == 0 or gen == 0):
                self._imprimir_progresso(gen, stats)

        return pd.DataFrame(self.historico)

    def _imprimir_progresso(self, geracao: int, stats: dict) -> None:
        """
        Imprime progresso da simulação de forma formatada.

        Args:
            geracao: Número da geração atual
            stats: Dict de estatísticas da geração
        """
        fase = self.ambiente.get_fase_epidemia()

        print(
            f"Gen {geracao:5d} | "
            f"Pop: {stats['tamanho']:6d} | "
            f"F: {stats['fitness_medio']:.4f} | "
            f"Div: {stats['diversidade_genetica']:.4f} | "
            f"Fase: {fase}"
        )

    def salvar_resultados(self, arquivo_csv: str) -> None:
        """
        Salva histórico em arquivo CSV.

        O CSV contém uma linha por geração com todas as métricas:
        fitness (média, desvio, max, min), diversidade, tamanho,
        variáveis ambientais, e fenótipos médios.

        Args:
            arquivo_csv: Caminho do arquivo de saída
        """
        df = pd.DataFrame(self.historico)
        df.to_csv(arquivo_csv, index=False)
        print(f"Resultados salvos em {arquivo_csv}")

    def gerar_visualizacoes(self, pasta_saida: str = './outputs/plots/') -> None:
        """
        Gera gráficos principais da simulação.

        Produz três gráficos:
        1. Evolução temporal de fitness (média ± desvio)
        2. Dinâmica populacional (tamanho ao longo do tempo)
        3. Evolução dos cinco fenótipos médios

        Args:
            pasta_saida: Diretório para salvar PNGs (padrão: './outputs/plots/')
        """
        import matplotlib.pyplot as plt
        import os

        os.makedirs(pasta_saida, exist_ok=True)

        df = pd.DataFrame(self.historico)

        # ===== GRÁFICO 1: EVOLUÇÃO DE FITNESS =====
        fig, ax = plt.subplots(figsize=(12, 6))

        ax.plot(
            df['geracao'],
            df['fitness_medio'],
            label='Fitness Médio',
            linewidth=2,
            color='steelblue'
        )
        ax.fill_between(
            df['geracao'],
            df['fitness_medio'] - df['fitness_desvio'],
            df['fitness_medio'] + df['fitness_desvio'],
            alpha=0.3,
            color='steelblue',
            label='±1 Desvio Padrão'
        )
        ax.plot(
            df['geracao'],
            df['fitness_max'],
            label='Máximo',
            linewidth=1,
            color='green',
            linestyle='--',
            alpha=0.7
        )

        ax.set_xlabel('Geração', fontsize=12)
        ax.set_ylabel('Fitness', fontsize=12)
        ax.set_title('Evolução do Fitness Médio da População', fontsize=14)
        ax.legend(loc='lower right')
        ax.grid(True, alpha=0.3)

        plt.tight_layout()
        plt.savefig(os.path.join(pasta_saida, 'fitness_evolution.png'), dpi=300)
        plt.close()

        # ===== GRÁFICO 2: DINÂMICA POPULACIONAL =====
        fig, ax = plt.subplots(figsize=(12, 6))

        ax.plot(
            df['geracao'],
            df['tamanho'],
            linewidth=2,
            color='coral'
        )
        ax.axhline(
            y=self.parametros['tamanho_populacao'],
            color='red',
            linestyle='--',
            alpha=0.5,
            label='Tamanho Alvo'
        )

        ax.set_xlabel('Geração', fontsize=12)
        ax.set_ylabel('Número de Indivíduos', fontsize=12)
        ax.set_title('Dinâmica Populacional', fontsize=14)
        ax.legend()
        ax.grid(True, alpha=0.3)

        plt.tight_layout()
        plt.savefig(os.path.join(pasta_saida, 'population_dynamics.png'), dpi=300)
        plt.close()

        # ===== GRÁFICO 3: EVOLUÇÃO DOS FENÓTIPOS =====
        fig, axes = plt.subplots(2, 3, figsize=(16, 10))

        traits = [
            'virulencia',
            'transmissibilidade',
            'sobrevivencia',
            'custo_metabolico',
            'adaptabilidade'
        ]

        for i, trait in enumerate(traits):
            ax = axes[i // 3, i % 3]
            col_name = f'fenotipos_medio_{trait}'

            ax.plot(
                df['geracao'],
                df[col_name],
                linewidth=2,
                color='purple'
            )
            ax.fill_between(
                df['geracao'],
                0,
                df[col_name],
                alpha=0.2,
                color='purple'
            )

            ax.set_title(
                trait.replace('_', ' ').title(),
                fontsize=12,
                fontweight='bold'
            )
            ax.set_xlabel('Geração', fontsize=10)
            ax.set_ylabel('Valor Médio', fontsize=10)
            ax.set_ylim([0, 1])
            ax.grid(True, alpha=0.3)

        # Remover subplot vazio
        axes[1, 2].axis('off')

        plt.tight_layout()
        plt.savefig(os.path.join(pasta_saida, 'trait_distribution.png'), dpi=300)
        plt.close()

        print(f"Visualizações salvas em {pasta_saida}")

    def obter_resumo_final(self) -> dict:
        """
        Retorna resumo final da simulação.

        Calcula métricas agregadas do resultado final.

        Returns:
            dict com: fitness_inicial, fitness_final, melhoria,
                     diversidade_inicial, diversidade_final,
                     tamanho_final, geracao_final, fase_final
        """
        if not self.historico:
            return {}

        primeiro = self.historico[0]
        ultimo = self.historico[-1]

        return {
            'fitness_inicial': primeiro['fitness_medio'],
            'fitness_final': ultimo['fitness_medio'],
            'melhoria_fitness': ultimo['fitness_medio'] - primeiro['fitness_medio'],
            'diversidade_inicial': primeiro['diversidade_genetica'],
            'diversidade_final': ultimo['diversidade_genetica'],
            'tamanho_final': ultimo['tamanho'],
            'geracao_final': ultimo['geracao'],
            'fase_final': self.ambiente.get_fase_epidemia(),
        }

    def imprimir_resumo(self) -> None:
        """Imprime resumo final da simulação de forma formatada."""
        resumo = self.obter_resumo_final()

        if not resumo:
            print("Sem dados para resumir")
            return

        print("\n" + "=" * 60)
        print("RESUMO FINAL DA SIMULAÇÃO")
        print("=" * 60)
        print(f"Gerações executadas: {resumo['geracao_final']}")
        print(f"Fase final: {resumo['fase_final']}")
        print(f"\nFitness:")
        print(f"  Inicial: {resumo['fitness_inicial']:.4f}")
        print(f"  Final:   {resumo['fitness_final']:.4f}")
        print(f"  Melhoria: {resumo['melhoria_fitness']:.4f}")
        print(f"\nDiversidade Genética:")
        print(f"  Inicial: {resumo['diversidade_inicial']:.4f}")
        print(f"  Final:   {resumo['diversidade_final']:.4f}")
        print(f"\nPopulação Final: {resumo['tamanho_final']} indivíduos")
        print("=" * 60 + "\n")

    def __repr__(self) -> str:
        """Representação em string da simulação."""
        return (
            f"Simulation(pop={self.parametros['tamanho_populacao']}, "
            f"gens={self.parametros['num_geracoes']}, "
            f"μ={self.parametros['taxa_mutacao']})"
        )