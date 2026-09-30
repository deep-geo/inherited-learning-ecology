# Paper 1 剩余证据实验

先读report.html/md与运行前协议PROTOCOL.md。依赖C++17/clang++、Python3、numpy、pandas、matplotlib；四模拟进程上限。完整包包含原始数据；精简包不含raw。

复制整个目录到独立位置后复跑。不要覆盖原始结果：运行器遇到同批执行日志会拒绝运行。下列R指向副本，副本raw/validation需为空目录。编译、单元检查、开发检查通过后才运行正式批次。

```sh
R=/absolute/path/to/copied/paper1_completion
mkdir -p "$R/raw" "$R/validation" "$R/plots"
clang++ -O3 -std=c++17 -DBINS=8 "$R/code/sim.cpp" -o "$R/code/sim8"
clang++ -O3 -std=c++17 -DBINS=4 "$R/code/sim.cpp" -o "$R/code/sim4"
clang++ -O2 -std=c++17 -DBINS=8 "$R/code/test.cpp" -o "$R/code/test8"
clang++ -O2 -std=c++17 -DBINS=4 "$R/code/test.cpp" -o "$R/code/test4"
"$R/code/test8" > "$R/validation/test8.json"
"$R/code/test4" > "$R/validation/test4.json"
python3 "$R/code/equivalence.py"
python3 "$R/code/run.py" development
python3 "$R/code/check.py" development
python3 "$R/code/run.py" representation
python3 "$R/code/check.py" representation
python3 "$R/code/run.py" mechanism
python3 "$R/code/check.py" mechanism
python3 "$R/code/run.py" robustness
python3 "$R/code/check.py" robustness
python3 "$R/code/analyze.py"
python3 "$R/code/final_checks.py"
python3 "$R/code/diagnostics.py"
python3 "$R/code/plots.py"
python3 "$R/code/report.py"
```

原始记录：metrics每200sweep保存人口、出生/死亡、收支误差；updates逐出生记录范数与共同/对比能量、额度与不可达写入；lifetimes含末期删失；learning是每32出生个体的行为效用探针，不是生态适应度，且其效用仍使用原始奖励；interventions记录预算后出生的表现型干预；audit记录总账与干预时点。出生probe文件在固定q组为空表头，不能解读为漏跑。

run_summary每条件每seed一行；summary跨20seed汇总。未达到的time为NaN，capped为20000，需同时读取reached和extinct。none按表示或生态情境共享，不为每个预算重复。final_occupancy为最后1000sweep五个采样点均值，不是单一末帧。

paired_effects：direction_advantage为随机减定向时间（其他指标反向）；erasure_penalty为清除减保留时间；fast_learning_rescue_erased为清除组标准学习减快速学习时间；erasure_penalty_reduction_fast_learning为标准学习清除损失减快速学习清除损失；direction_advantage_reduction_erasure为保留条件方向优势减清除条件方向优势。对AUC统一取正值为相应机制预测。区间均描述性，不能用多个探索对比挑显著。

源码由上一轮审计引擎扩展，不声称是独立实现。保留新旧引擎精确等价、no-op等价、两种维数的旋转测试、开发及正式账检查、协议哈希。跨编码只比较本编码内部的方向效应。

code/reference保留上一轮三个源文件，用于完全独立于旧目录的等价复核；equivalence.py生成历史/无操作比较，final_checks.py核验并精确复跑三个代表条件。最终校验包包含每个文件的SHA256。
