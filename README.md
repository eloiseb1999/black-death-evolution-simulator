<div align="center">

# Black Death Evolution Simulator

<img src="./assets/plague_doctorII.png" width="220" alt="Plague Doctor">

<br><br>

*A computational evolutionary model inspired by the epidemiological dynamics of* **Yersinia pestis**.

</div>


Overview

This project implements an evolutionary simulation inspired by the historical spread of the Black Death. The model investigates how populations of Yersinia pestis may evolve under changing environmental conditions, selective pressures, host availability, immune responses, and resource constraints.

Rather than attempting to reproduce historical events with epidemiological accuracy, the objective is to explore how evolutionary mechanisms shape adaptive strategies over long timescales through computational experimentation.

The simulation combines concepts from evolutionary computation, quantitative genetics, population dynamics, and biological adaptation into a unified framework.

---

Scientific Motivation

The Black Death has always been one of the historical and biological subjects that captured my attention the most.

What initially began as an interest in medieval history gradually evolved into a curiosity about the evolutionary mechanisms operating behind large-scale epidemics. While reading about Yersinia pestis, host-pathogen interactions, and historical outbreaks, I became increasingly interested in a simple question:

How do selective pressures shape the evolutionary trajectory of a pathogen population over time?

This project emerged as an attempt to explore that question through computation.

The simulator is not intended to recreate the Black Death itself. Instead, it serves as a controlled environment where evolutionary processes can be observed, analyzed, and experimented with. By combining mutation, selection, environmental variability, and competing biological traits, the model provides a simplified framework for studying how adaptive strategies emerge and stabilize across generations.

Beyond its historical inspiration, the project reflects my personal interest in evolutionary systems, complex adaptive behavior, and computational models capable of generating emergent outcomes from relatively simple rules.

---

Key Concepts

The simulation is built around five fundamental principles:

- Quantitative genetics
- Emergent phenotypes
- Environmental selection pressure
- Evolutionary trade-offs
- Adaptive population dynamics

Together, these components create a system where evolutionary behavior emerges naturally rather than being explicitly programmed.

---

Model Architecture

The simulation is organized into four main components.

Bacteria

Represents an individual pathogen.

Each bacterium contains:

- A genome composed of 12 continuous genes
- Emergent phenotypic traits
- Fitness evaluation methods
- Mutation and replication mechanisms

Population

Manages collections of individuals and implements:

- Natural selection
- Reproduction
- Population statistics
- Genetic diversity analysis

Environment

Models dynamic environmental conditions:

- Temperature variation
- Host density
- Immune pressure
- Nutrient availability

Environmental variables evolve continuously and directly affect individual fitness.

Simulation

Coordinates the complete evolutionary cycle:

1. Selection
2. Reproduction
3. Mutation
4. Environmental update
5. Statistical recording

---

Genetic Representation

Each individual contains a genome composed of twelve continuous genes:

Genome = [g₁, g₂, ..., g₁₂]

Each gene assumes a value within:

g ∈ [0,1]

Genes are organized into functional groups:

Trait| Genes
Virulence| 0–1
Transmissibility| 2–3
Survival| 4–5
Metabolic Cost| 6–8
Adaptability| 9–11

Phenotypes emerge as aggregated expressions of the genes belonging to each functional group.

---

Fitness Function

The evolutionary objective is determined through a multidimensional fitness function:

F = S × T × (1 − C) × A × E

Where:

- S = Survival
- T = Transmissibility
- C = Metabolic Cost
- A = Adaptability
- E = Environmental Pressure

This formulation naturally creates evolutionary trade-offs between competing strategies.

---

Environmental Dynamics

The environment progresses through three epidemic stages:

Phase| Description
Introduction| Low host density and weak immune pressure
Epidemic| High transmission opportunities
Control| Host collapse and stronger immune response

Additional environmental factors include:

- Seasonal temperature cycles
- Resource fluctuations
- Progressive immune adaptation

---

Features

- Evolutionary simulation across thousands of generations
- Dynamic environmental pressures
- Phenotype emergence from genetic architecture
- Mutation-driven adaptation
- Fitness tracking
- Genetic diversity metrics
- Population-level statistics
- Automated visualization generation
- CSV export of simulation history
- Comparative evolutionary analysis

---

Project Structure

black-death-evolution/
│
├── README.md
├── requirements.txt
├── LICENSE
├── .gitignore
│
├── assets/
│   └── plague_doctor.png
│
├── docs/
│   ├── ESPECIFICACAO_TECNICA.md
│   └── HISTORIA_PESTE_NEGRA.md
│
├── src/
│   ├── bacteria.py
│   ├── environment.py
│   ├── population.py
│   ├── simulation.py
│   └── utils.py
│
└── scripts/
    └── run_simulation.py

---

Installation

git clone https://github.com/eloiseb1999/black-death-evolution-simulator.git

cd black-death-evolution

pip install -r requirements.txt

---

Usage

Run the simulation using default parameters:

python scripts/run_simulation.py

Custom configuration:

python scripts/run_simulation.py \
    --pop-size 10000 \
    --generations 5000 \
    --mutation-rate 1e-7 \
    --seed 42

Generate additional reports:

python scripts/run_simulation.py --full-report

---

Output

The simulator produces:

Data

- Evolutionary history
- Population statistics
- Environmental variables
- Phenotypic measurements

Visualizations

- Fitness evolution
- Population dynamics
- Phenotype trajectories
- Environmental variation

---

Limitations

This model is intentionally simplified and should not be interpreted as a predictive epidemiological system.

Its primary purpose is educational, exploratory, and computational, providing a framework for studying evolutionary dynamics under changing environmental conditions.

---

References

- Benedictow, O. J. The Black Death 1346–1353
- Perry, R. D. & Fetherston, J. D. Yersinia pestis
- Literature on evolutionary computation and quantitative genetics


