# Inherited Learning in an Artificial Ecology

Reproducibility materials for **Inherited Action Preferences in a Resource-Limited Artificial Ecology: Controls, Relearning, and Update Allocation**, by Xuening Wu.

This is a computational artificial ecology, not a biological cell experiment. Individuals learn action preferences and may transmit learned changes during local reproduction. The study distinguishes control geometry, newborn relearning, and allocation of hereditary updates. It does not establish a universal inheritance advantage, an evolutionary phase transition, or improved long-term evolvability.

## Evidence and limitations

- State-preserving random controls reduce the apparent benefit relative to weaker whole-table controls; conditional establishment-speed benefits remain.
- Newborn preference erasure and learning-rate compensation support a relearning-related mechanism in the tested fixed-norm regime.
- Symmetric step/range constraints retain continuous writeback benefits, but do not equalize cumulative changes across evolving populations.
- Event quotas and common-time cutoffs estimate different allocation policies.
- In the final equal-budget experiment all 80 runs use 1,024 steps with identical cumulative magnitudes. Staging improves directed occupancy, **but none of the four groups achieves the prespecified establishment threshold**. This is secondary mechanism support, not a successful faster-establishment prediction.

The 3,280 condition runs reuse paired seeds within blocks; they are not 3,280 independent experimental units. Each reported condition has 20 seeds. Bootstrap intervals are descriptive, not multiplicity-adjusted.

## Quick reproduction (no new simulations)

Python 3.10+ and a C++17 compiler are sufficient for the core scripts. For Python dependencies:

```sh
python -m pip install -r requirements.txt
python reproduce_endpoints.py
python verify_followups.py
python reproduce_figures.py
```

The first check recomputes establishment, capped times, occupancy area, late occupancy and extinction for 1,840 initial runs. The second checks the same endpoints and fixed-budget ledger summaries for 1,440 follow-up runs. These checks validate consistency of archived data, not an independent implementation of the model. The original figure script reproduces the three initial result figures; the current manuscript also includes an embedded TikZ overview and follow-up tables.

## Contents

| Directory or file | Purpose |
|---|---|
| `manuscript.tex` | Current standalone LaTeX manuscript; figures and bibliography embedded |
| `data/` | Initial 1,840-run seed-level data and population traces |
| `archived_experiments/paper1_state_matched/` | Strong random controls and event quotas |
| `archived_experiments/paper1_completion/` | Representation, newborn-expression and ecological interventions |
| `archived_experiments/paper1_native_writeback/` | Original proportional writeback |
| `archived_experiments/paper1_writeback_stability/` | 1,200-run symmetric-stability follow-up |
| `archived_experiments/paper1_cutoff_diagnostic/` | 160-run common-time cutoff diagnostic |
| `archived_experiments/paper1_budget_timing/` | 80-run equal-budget release experiment |

Each stage retains its own protocol, seed manifest, source snapshot and available validation records. Original experiment scripts are archived without rewriting their scientific implementation. Cross-stage development checks may require neighboring stages, compiled reference executables or omitted raw logs; see each stage's protocol rather than assuming every historical helper runs from an empty checkout.

## New simulation runs

Run simulations in a **fresh copy** of the relevant stage. Do not overwrite archived results or manifests. For the three follow-up stages, compile `code/sim.cpp` with `c++ -O3 -std=c++17 code/sim.cpp -o code/sim`; create `raw/` and `validation/`; consult `code/run.py` and `PROTOCOL.md`. The formal runner refuses to overwrite an existing `validation/run.json`. Full reruns generate large per-birth and lifetime logs and are not part of the quick reproduction path.

## Data scope

Large per-event logs, compiled binaries, caches, stale PDFs, and upload archives are deliberately excluded. Population trajectories and seed summaries are included. Full ledger validation of omitted logs requires regenerating events with the archived simulator or obtaining the original logs from the author. An arXiv identifier and permanent archive DOI have not yet been assigned.

## Authorship and reuse

Author: Xuening Wu. The manuscript describes AI assistance and author responsibility. This repository contains no claim of independent external validation. No open-source license has yet been selected; public availability alone does not grant an unrestricted reuse license. License selection is reserved for the author.
