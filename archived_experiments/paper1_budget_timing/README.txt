Paper 1 fixed-budget timing diagnostic
Build: c++ -O3 -std=c++17 code/sim.cpp -o code/sim
Checks: python3 code/run.py check
Run: python3 code/run.py formal
Analyze: python3 code/analyze.py
Formal run refuses to overwrite validation/run.json; use a clean copy for rerun.
Raw prefixes map to seeds/directions/schedules in validation/run.json.
20 paired independent seeds, 80 simulations. Protocol frozen before formal batch.
