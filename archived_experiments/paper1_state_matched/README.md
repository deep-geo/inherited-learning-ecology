# 实验1与2复现

先读report.html/md和PROTOCOL.md。依赖C++17/clang++、Python3、numpy、pandas、matplotlib。四个模拟进程上限。

运行器拒绝覆盖已有批次。完整重跑应复制此目录到独立工作区，清空副本raw和validation中的文件并保留这两个目录，然后从项目目录执行：

```sh
mkdir -p work outputs/paper1_state_matched/raw outputs/paper1_state_matched/validation
clang++ -O2 -std=c++17 outputs/paper1_state_matched/code/test_rotation.cpp -o work/test_state_rotation
work/test_state_rotation
python3 outputs/paper1_state_matched/code/run.py development
python3 outputs/paper1_state_matched/code/check.py development
python3 outputs/paper1_state_matched/code/run.py confirmation
python3 outputs/paper1_state_matched/code/check.py confirmation
python3 outputs/paper1_state_matched/code/run.py budgets
python3 outputs/paper1_state_matched/code/check.py budgets
python3 outputs/paper1_state_matched/code/run.py replay
python3 outputs/paper1_state_matched/code/check.py replay
python3 outputs/paper1_state_matched/code/analyze.py
python3 outputs/paper1_state_matched/code/final_checks.py
python3 outputs/paper1_state_matched/code/plots.py
python3 outputs/paper1_state_matched/code/report.py
```

mode2是定向固定q，mode6是同状态零和动作平面随机方向，mode3为旧全表打乱，mode4为全表各向同性随机。none为mode0,lambda0。其余CLI继承前轮：prefix L T seed eta lambda mu mode probes regrowth mortality q cap child_fraction bonus。

state_rotated保留每个状态的共同位移及动作对比范数；不保留状态内每个动作的稀疏性。只保留原学习更新涉及的状态支持；没有向物理不可达状态写入。不同群体生态分叉后的学习量不相同，报告不声称逐状态群体累计预算完全匹配。

raw下metrics为每200sweep轨迹；updates为逐次出生更新及三个几何账（contrast_sq、common_sq、unreachable_sq）；lifetimes保留死亡/末期删失；learning为子代探针。audit包含累计预算及逐状态匹配最大误差。旧birth_probes在固定q条件下只有表头。

run_summary每seed一行；time0.95未达标为NaN，capped0.95未达标为20000，必须结合reached和extinct解释。预算0只用于none共享参照；预算-1为无上限。实验2的none不为每个预算重复运行，不能将该共享参照当作额外独立seed。

首个连续5采样点满足95%的起始点作为建立时间，需后续4点确认，跨度800sweep。完整20,000sweep都保留；90/99%为预定辅助。

精确复跑、预算前128次共同前缀、范数/支持/人口/能量核验见validation。新增零学习信号规则为跳过更新，本轮实际skip=0；额度只消耗非零更新。
