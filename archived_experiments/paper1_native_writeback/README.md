# 原始比例写回连接实验

先读report.html/md与PROTOCOL.md；METHODS_RESULTS_DRAFT.md为当前方法和结果工作初稿，不是已完成文献审查的投稿成稿。依赖C++17/clang++、Python3、numpy、pandas、matplotlib，最多4模拟进程。

将目录复制到独立位置，保留code和协议，副本raw/validation/plots为空目录。运行器拒绝覆盖已有阶段日志。以下R为副本目录。

```sh
set -e
R=/absolute/path/to/copied/paper1_native_writeback
mkdir -p "$R/raw" "$R/validation" "$R/plots"
clang++ -O3 -std=c++17 "$R/code/sim.cpp" -o "$R/code/sim"
python3 "$R/code/verify.py"
python3 "$R/code/run.py" development
python3 "$R/code/check.py" development
python3 "$R/code/run.py" confirmation
python3 "$R/code/check.py" confirmation
python3 "$R/code/analyze.py"
python3 "$R/code/final_checks.py"
python3 "$R/code/plots.py"
python3 "$R/code/report.py"
```

mode7原始定向，mode8原始同状态随机。无q归一化、无最小幅度。lambda0共享none，mu0，cap=-1表示持续写回，1024为非零更新次数上限。零学习位移产生零更新，不花额度；没有故意注入随机变化填满额度。

metrics每200sweep采样；updates逐出生记录candidate_norm（原始lambda位移范数）与write_norm（额度截断后的真实范数），还有逐状态共同/对比平方量；lifetimes含死亡和末期删失；learning只针对每32次出生采样的个体，不是总体适应度；audit为汇总账。固定mode7/8的birth_probes与本轮未启用的interventions均仅有表头。

run_summary每条件每seed一行。time0.95未达到为NaN，capped0.95为20000；需要同时看reached和extinct。summary为种子均值，不同lambda/预算重复同一批seed，不能当作独立样本增加n。paired_effects时间差为随机减定向，其他指标为定向减随机。

实现检查中曾错误比较eta0与eta.2/lambda0的整个生态轨迹；修正为各自学习率内部的写回不变性，原失败记录与修正说明保留。模拟器与正式参数未据此修改。
