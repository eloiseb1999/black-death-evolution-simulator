import numpy as np
import random
from typing import List, Optional
from src.bacteria import Bacteria


class Population:
    """
    Gerencia uma população de bactérias.

    Implementa operações coletivas como seleção natural, reprodução
    e cálculo de estatísticas populacionais.

    Attributes:
        individuos: Lista de instâncias de Bacteria
        tamanho_inicial: Tamanho target da população
    """

    def __init__(
            self,
            tamanho: int,
            genoma_aleatorio: bool = True,
            seed: Optional[int] = None
    ):
        """
        Inicializa população.

        Args:
            tamanho: Número de indivíduos na população
            genoma_aleatorio: Se True, genomas aleatórios; False, todos com valor 0.5
            seed: Seed para reprodutibilidade (opcional)
        """
        if seed is not None:
            np.random.seed(seed)
            random.seed(seed)

        self.individuos: List[Bacteria] = []
        self.tamanho_inicial = tamanho

        if genoma_aleatorio:
            # Genomas aleatórios uniformes em [0, 1]
            for _ in range(tamanho):
                genoma = np.random.uniform(0, 1, 12)
                self.individuos.append(Bacteria(genoma=genoma))
        else:
            # Genoma padrão (todos com valor 0.5)
            genoma_padrao = np.full(12, 0.5)
            for _ in range(tamanho):
                self.individuos.append(
                    Bacteria(genoma=genoma_padrao.copy())
                )

    @property
    def tamanho(self) -> int:
        """Retorna tamanho atual da população."""
        return len(self.individuos)

    def selecionar_naturalmente(
            self,
            ambiente,
            threshold: float = 0.1
    ) -> List[Bacteria]:
        """
        Filtra apenas bactérias com fitness acima do threshold.

        Simula morte de linhagens menos aptas. Bactérias com fitness
        menor que threshold não sobrevivem.

        Args:
            ambiente: Instance de Environment com condições atuais
            threshold: Mínimo fitness para sobreviver (padrão: 0.1)

        Returns:
            Lista de indivíduos sobreviventes
        """
        sobreviventes = [
            b for b in self.individuos
            if b.calcular_fitness(ambiente) >= threshold
        ]
        return sobreviventes

    def reproduzir(
            self,
            taxa_mutacao: float = 1e-7,
            tamanho_alvo: Optional[int] = None
    ) -> 'Population':
        """
        Cria nova geração via reprodução assexuada.

        Cada indivíduo se divide (em média) gerando clones com possíveis
        mutações até atingir o tamanho alvo.

        Args:
            taxa_mutacao: Taxa de mutação por gene por divisão
            tamanho_alvo: Tamanho da nova população. Se None, usa tamanho_inicial

        Returns:
            Nova instância de Population com a geração filha
        """
        if tamanho_alvo is None:
            tamanho_alvo = self.tamanho_inicial

        # Reproduzir até atingir tamanho alvo
        nova_populacao = []
        while len(nova_populacao) < tamanho_alvo:
            pai = random.choice(self.individuos)
            filha = pai.reproduzir(taxa_mutacao=taxa_mutacao)
            nova_populacao.append(filha)

        # Criar nova Population
        pop_nova = Population(tamanho=0)
        pop_nova.individuos = nova_populacao[:tamanho_alvo]
        pop_nova.tamanho_inicial = tamanho_alvo

        return pop_nova

    def calcular_estatisticas(self, ambiente) -> dict:
        """
        Calcula estatísticas agregadas da população.

        Inclui: fitness (média, desvio, max, min), diversidade genética,
        e fenótipos médios.

        Args:
            ambiente: Instance de Environment com condições atuais

        Returns:
            dict com chaves: fitness_medio, fitness_desvio, fitness_max,
                           fitness_min, diversidade_genetica, tamanho,
                           fenotipos_medio (dict aninhado)
        """
        # Calcular fitness de todos
        fitness_values = [
            b.calcular_fitness(ambiente) for b in self.individuos
        ]

        # Diversidade genética como variância média dos genes
        genomas = np.array([b.genoma for b in self.individuos])
        diversidade = np.mean(np.var(genomas, axis=0))

        # Fenótipos médios
        fenotipos_all = [b.fenotipos for b in self.individuos]
        fenotipos_medio = {
            key: np.mean([f[key] for f in fenotipos_all])
            for key in fenotipos_all[0].keys()
        }

        return {
            'fitness_medio': np.mean(fitness_values),
            'fitness_desvio': np.std(fitness_values),
            'fitness_max': np.max(fitness_values),
            'fitness_min': np.min(fitness_values),
            'diversidade_genetica': diversidade,
            'tamanho': self.tamanho,
            'fenotipos_medio': fenotipos_medio,
        }

    def melhor_individuo(self, ambiente) -> Bacteria:
        """
        Retorna o indivíduo com maior fitness.

        Args:
            ambiente: Instance de Environment com condições atuais

        Returns:
            Bacteria com máximo fitness
        """
        return max(
            self.individuos,
            key=lambda b: b.calcular_fitness(ambiente)
        )

    def pior_individuo(self, ambiente) -> Bacteria:
        """
        Retorna o indivíduo com menor fitness.

        Args:
            ambiente: Instance de Environment com condições atuais

        Returns:
            Bacteria com mínimo fitness
        """
        return min(
            self.individuos,
            key=lambda b: b.calcular_fitness(ambiente)
        )

    def diversidade_genetica(self) -> float:
        """
        Retorna medida de diversidade genética da população.

        Calcula como a variância média dos genes.

        Returns:
            float em [0, 1]. 1.0 = muito heterogênea, 0.0 = todos idênticos
        """
        genomas = np.array([b.genoma for b in self.individuos])
        return np.mean(np.var(genomas, axis=0))

    def fenotipos_medios(self) -> dict:
        """
        Calcula fenótipos médios da população.

        Returns:
            dict com chaves: virulencia, transmissibilidade, sobrevivencia,
                           custo_metabolico, adaptabilidade
        """
        fenotipos_all = [b.fenotipos for b in self.individuos]
        return {
            key: np.mean([f[key] for f in fenotipos_all])
            for key in fenotipos_all[0].keys()
        }

    def distribuicao_fitness(self, ambiente, num_bins: int = 10) -> dict:
        """
        Calcula distribuição de fitness em bins.

        Útil para análise de histograma.

        Args:
            ambiente: Instance de Environment com condições atuais
            num_bins: Número de bins para histograma

        Returns:
            dict com chaves: bins (valores), counts (frequências)
        """
        fitness_values = [
            b.calcular_fitness(ambiente) for b in self.individuos
        ]
        counts, bin_edges = np.histogram(fitness_values, bins=num_bins)
        bins = (bin_edges[:-1] + bin_edges[1:]) / 2  # Centros dos bins

        return {
            'bins': bins.tolist(),
            'counts': counts.tolist(),
        }

    def __repr__(self) -> str:
        """Representação em string da população."""
        return f"Population(tamanho={self.tamanho})"

    def __len__(self) -> int:
        """Permite usar len() na população."""
        return self.tamanho