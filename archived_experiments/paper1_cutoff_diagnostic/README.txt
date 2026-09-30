Paper 1 cutoff diagnostic

Protocol: PROTOCOL.md (frozen before formal runs)
Build: c++ -O3 -std=c++17 code/sim.cpp -o code/sim
Development checks: python3 code/run.py check
Formal batch: python3 code/run.py formal (refuses to overwrite validation/run.json)
Analysis: python3 code/analyze.py

Formal raw prefixes map to seeds, directions and regimes in validation/run.json.
Raw audit and event logs remain unchanged. Development seed 103000 is excluded.
A fresh rerun should use a copy with empty raw/ and without validation/run.json.
Do not treat the 160 runs as 160 independent seed units: there are 20 paired seeds.
