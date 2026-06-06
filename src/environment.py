import numpy as np
from typing import Optional


class Environment:
    """
    Modela condições ambientais dinâmicas que variam ao longo do tempo.

    Implementa evolução temporal de parâmetros que afetam fitness:
    temperatura, densidade de hospedeiros, pressão imunológica e nutrientes.

    Attributes:
        geracao: Geração atual
        temperatura: Temperatura em °C [10, 30]
        densidade_hospedeiros: Proporção de hospedeiros disponíveis [0, 1]
        pressao_imunologica: Força do sistema imune do hospedeiro [0, 1]
        nutrientes: Disponibilidade de nutrientes [0, 1]
    """

    def __init__(self, geracao_inicial: int = 0, seed: Optional[int] = None):
        """
        Inicializa environment.

        Args:
            geracao_inicial: Geração inicial (padrão: 0)
            seed: Seed para reprodutibilidade (opcional)
        """
        if seed is not None:
            np.random.seed(seed)

        self.geracao = geracao_inicial
        self.temperatura = 15.0
        self.densidade_hospedeiros = 0.1
        self.pressao_imunologica = 0.3
        self.nutrientes = 0.8

    def avanca_tempo(self, delta_geracao: int = 1) -> None:
        """
        Simula passagem de tempo e mudanças ambientais.

        Modela três fases epidêmicas:

        Fase I (0-500): Introdução. Densidade baixa, imunidade mínima.
        Fase II (500-2500): Epidemia. Densidade cresce, imunidade aumenta.
        Fase III (2500+): Controle. Densidade colapsa, imunidade forte.

        Implementa:
        - Temperatura com ciclo sazonal sinusoidal
        - Densidade de hospedeiros com crescimento e colapso
        - Pressão imunológica progressiva
        - Nutrientes com flutuações aleatórias

        Args:
            delta_geracao: Número de gerações a avançar (padrão: 1)
        """
        self.geracao += delta_geracao

        # ===== TEMPERATURA: Ciclo sazonal =====
        # Ciclo anual de 365 gerações (aproximadamente)
        ciclo_sazonal = np.sin(self.geracao * 2 * np.pi / 365)
        self.temperatura = 18 + 7 * ciclo_sazonal

        # ===== DENSIDADE DE HOSPEDEIROS =====
        # Fase I (0-500): Crescimento lento de 0.1 a 0.2
        if self.geracao < 500:
            self.densidade_hospedeiros = 0.1 * (1 + 0.002 * self.geracao)

        # Fase II (500-2500): Epidemia, platô alto
        elif self.geracao < 2500:
            self.densidade_hospedeiros = 0.3

        # Fase III (2500+): Colapso exponencial
        else:
            self.densidade_hospedeiros = 0.3 * np.exp(
                -(self.geracao - 2500) / 500
            )

        # Confinir em [0, 1]
        self.densidade_hospedeiros = max(0, min(1, self.densidade_hospedeiros))

        # ===== PRESSÃO IMUNOLÓGICA =====
        # Aumenta progressivamente com o tempo
        self.pressao_imunologica = 0.2 * np.sqrt(self.geracao / 1000 + 1)
        self.pressao_imunologica = min(self.pressao_imunologica, 0.9)

        # ===== NUTRIENTES =====
        # Flutuações aleatórias ao redor de 0.8
        self.nutrientes = max(0.5, 0.8 + np.random.normal(0, 0.1))
        self.nutrientes = min(self.nutrientes, 1.0)

    def calcular_pressao_seletiva(self, bacteria) -> float:
        """
        Calcula fator multiplicativo de fitness baseado no ambiente.

        Implementa a função:
            f_amb = f_temp × f_host × f_imune × f_nut

        onde cada componente modula o fitness base conforme
        características da bactéria e estado ambiental.

        Args:
            bacteria: Instance de Bacteria a ser avaliada

        Returns:
            float em [0, 1] que modula o fitness base
        """
        ft = bacteria.fenotipos

        # ===== FATOR TEMPERATURA =====
        # Ótimo em 18°C, cai conforme afasta
        temp_otima = 18.0
        desvio_temp = abs(self.temperatura - temp_otima)
        fator_temp = max(0, 1 - (desvio_temp / 20))

        # ===== FATOR HOSPEDEIRO =====
        # Quanto mais hospedeiros, melhor oportunidade de transmissão
        fator_transmissao = self.densidade_hospedeiros

        # ===== FATOR IMUNIDADE =====
        # Bactérias virulentas sofrem mais com imunidade forte
        # f_imune = 1 - (pressao_imunologica × virulencia)
        fator_sobrevivencia = (
                1 - (self.pressao_imunologica * ft['virulencia'])
        )
        fator_sobrevivencia = max(0, fator_sobrevivencia)

        # ===== FATOR NUTRIENTES =====
        # Nutrientes aumentam disponibilidade de recursos
        fator_metabolico = self.nutrientes

        # ===== COMBINAÇÃO MULTIPLICATIVA =====
        f_ambiente = (
                fator_temp *
                fator_transmissao *
                fator_sobrevivencia *
                fator_metabolico
        )

        return f_ambiente

    def obter_estado_atual(self) -> dict:
        """
        Retorna dicionário com estado atual do ambiente.

        Returns:
            dict com chaves: geracao, temperatura, densidade_hospedeiros,
                           pressao_imunologica, nutrientes
        """
        return {
            'geracao': self.geracao,
            'temperatura': self.temperatura,
            'densidade_hospedeiros': self.densidade_hospedeiros,
            'pressao_imunologica': self.pressao_imunologica,
            'nutrientes': self.nutrientes,
        }

    def get_fase_epidemia(self) -> str:
        """
        Retorna qual fase epidêmica está em progresso.

        Returns:
            str: "Introdução", "Epidemia" ou "Controle"
        """
        if self.geracao < 500:
            return "Introdução"
        elif self.geracao < 2500:
            return "Epidemia"
        else:
            return "Controle"

    def __repr__(self) -> str:
        """Representação em string do environment."""
        return (
            f"Environment(gen={self.geracao}, "
            f"temp={self.temperatura:.1f}°C, "
            f"dens={self.densidade_hospedeiros:.2f}, "
            f"imun={self.pressao_imunologica:.2f})"
        )