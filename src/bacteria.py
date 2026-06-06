from dataclasses import dataclass
import numpy as np
import random


@dataclass
class Bacteria:
    """
    Representa um indivíduo bacteriano de Yersinia pestis.

    Cada bactéria possui um genoma abstrato de 12 genes contínuos,
    onde cada alelo assume valores no intervalo [0, 1].
    Fenótipos emergem como agregações lineares dos genes.

    Attributes:
        genoma: Array numpy com 12 genes, valores em [0, 1]
        idade: Número de gerações de vida
        geracao_nascimento: Em qual geração nasceu
    """

    genoma: np.ndarray
    idade: int = 0
    geracao_nascimento: int = 0

    def __post_init__(self):
        """Validação após inicialização."""
        if len(self.genoma) != 12:
            raise ValueError("Genoma deve ter exatamente 12 genes")

        if not np.all((self.genoma >= 0) & (self.genoma <= 1)):
            raise ValueError("Todos os genes devem estar em [0, 1]")

    @property
    def fenotipos(self) -> dict:
        """
        Calcula fenótipos a partir do genoma.

        Fenótipos emergem como agregações lineares dos genes dentro
        de cada grupo funcional. Cada fenótipo está em [0, 1].

        Returns:
            dict com chaves: virulencia, transmissibilidade, sobrevivencia,
                           custo_metabolico, adaptabilidade
        """
        return {
            'virulencia': (self.genoma[0] + self.genoma[1]) / 2,
            'transmissibilidade': (self.genoma[2] + self.genoma[3]) / 2,
            'sobrevivencia': (self.genoma[4] + self.genoma[5]) / 2,
            'custo_metabolico': (self.genoma[6] + self.genoma[7] + self.genoma[8]) / 3,
            'adaptabilidade': (self.genoma[9] + self.genoma[10] + self.genoma[11]) / 3,
        }

    def calcular_fitness(self, ambiente) -> float:
        """
        Calcula fitness baseado em fenótipos e condições ambientais.

        A função de fitness é:
            F = S × T × (1 - C) × A × f_amb

        onde S, T, C, A são fenótipos e f_amb é o fator ambiental.

        Args:
            ambiente: Instance de Environment com condições atuais

        Returns:
            float em [0, 1] representando aptidão biológica
        """
        ft = self.fenotipos

        S = ft['sobrevivencia']
        T = ft['transmissibilidade']
        C = ft['custo_metabolico']
        A = ft['adaptabilidade']

        # Fitness base multiplicativo
        fitness_base = S * T * (1 - C) * A

        # Aplicar pressão ambiental
        f_amb = ambiente.calcular_pressao_seletiva(self)

        return fitness_base * f_amb

    def reproduzir(self, taxa_mutacao: float = 1e-7) -> 'Bacteria':
        """
        Realiza fissão binária com mutação.

        Cria um clone do genoma parental. Para cada gene, há uma
        probabilidade taxa_mutacao de sofrer uma mutação (pequeno
        passo gaussiano). O novo alelo é confinado ao intervalo [0, 1].

        Args:
            taxa_mutacao: Probabilidade de mutação por gene por divisão

        Returns:
            Nova instância de Bacteria (filha)
        """
        # Clone do genoma
        novo_genoma = self.genoma.copy()

        # Aplicar mutações
        for i in range(len(novo_genoma)):
            if random.random() < taxa_mutacao:
                # Mutação como passo gaussiano
                mutacao = random.gauss(0, 0.05)
                novo_genoma[i] += mutacao

                # Confinar em [0, 1]
                novo_genoma[i] = max(0, min(1, novo_genoma[i]))

        return Bacteria(
            genoma=novo_genoma,
            idade=0,
            geracao_nascimento=self.geracao_nascimento + 1
        )

    def clonar(self) -> 'Bacteria':
        """
        Cria um clone exato sem mutações.

        Returns:
            Nova instância de Bacteria idêntica
        """
        return Bacteria(
            genoma=self.genoma.copy(),
            idade=0,
            geracao_nascimento=self.geracao_nascimento
        )

    def sofrer_mutacao(self, indice_gene: int, magnitude: float = 0.1) -> None:
        """
        Sofre mutação em um gene específico.

        Método auxiliar para testes ou eventos específicos.

        Args:
            indice_gene: Qual gene sofre mutação (0-11)
            magnitude: Tamanho do passo da mutação (desvio padrão)
        """
        if not (0 <= indice_gene < 12):
            raise ValueError("Índice de gene deve estar entre 0 e 11")

        mutacao = np.random.gauss(0, magnitude)
        self.genoma[indice_gene] += mutacao
        self.genoma[indice_gene] = max(0, min(1, self.genoma[indice_gene]))

    def __repr__(self) -> str:
        """Representação em string da bactéria."""
        ft = self.fenotipos
        return (
            f"Bacteria(vir={ft['virulencia']:.2f}, "
            f"trn={ft['transmissibilidade']:.2f}, "
            f"svr={ft['sobrevivencia']:.2f}, "
            f"cst={ft['custo_metabolico']:.2f})"
        )