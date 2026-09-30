from pathlib import Path
import json,html,base64
import pandas as pd
R=Path(__file__).resolve().parents[1];s=pd.read_csv(R/'summary.csv');e=pd.read_csv(R/'paired_effects.csv');d=pd.read_csv(R/'effect_change.csv')
names={0:'原始',1:'仅幅度上限',2:'共同范围[-.62,.42]',3:'共同范围[-1,1]'}
def table(df):
 cols=list(df.columns);lines=['| '+' | '.join(cols)+' |','| '+' | '.join(['---']*len(cols))+' |']
 for row in df.itertuples(index=False,name=None):lines.append('| '+' | '.join(f'{v:.4g}' if isinstance(v,float) else str(v) for v in row)+' |')
 return '\n'.join(lines)
out=['# 原始写回的对称稳定性约束实验','## Material Passport','2026-09-29；run＋descriptive validation；1200条正式运行完成，20个新种子；预定设计与源码在正式批次前冻结。未修改论文或上传包。没有独立系统或学习时间预测实验。','## 预定问题与解释边界','本轮检验定向与随机方向的表现差，能否在双方相同的实际单次幅度约束及共同参数范围下保留。它解决一个可测的稳定性替代解释，不构成把自然历史中的幅度、方向与选择效应全部分离的证明。详细结论见本文最后的判读，完整原始数据全部保留。','## 设计','每个父代构造定向d与逐状态旋转r。norm共同乘min(1,Q/||d||)，Q=0.1841261006694567；小更新不放大。box/wide逐状态再使用双方均合法的共同步长，在需要约束时留1%的内部余量。box范围[-.62,.42]来自此模型奖励界与零初始化；wide范围[-1,1]是预定敏感性。共同缩放保留同父代候选的逐状态均值、对比范数、实际L2与零支持。完整计算方法与局限在PROTOCOL.md。','两能量份额×三lambda×四规则×两方向×20种子=960持续写回运行；box另有240条B=1024辅助运行。模拟时间20000sweep，L32，eta=.2，mu=0。种子101000–101019，未按结果追加。没有把1200运行当作1200个独立种子。','## 匹配与不匹配','| 属性 | 状态 |\n|---|---|\n| 同一父代两个候选的逐状态实际步长、均值、对比范数、零支持 | 匹配，几何与日志验证 |\n| 单次全表更新上限 | norm/box/wide相同 |\n| 参数坐标范围 | box/wide双方相同；norm不保证长期有界 |\n| 两个种群实际更新分布、出生数、累计L2及平方量 | 不匹配，逐项报告 |\n| 子代参数范数、动作概率变化、未来探索与生态轨迹 | 不匹配 |\n| 未修改原始凸组合规则 | 仅native保持；稳定规则是干预变体 |','行为变化以所有128个表示状态等权的epsilon-greedy动作概率总变差计算，包含不可达状态，不能替代实际访问加权行为稳定性。离散贪心行为可能在很小参数变化时跳变，因此参数有界不等于行为匹配。native未计算双候选行为指标，汇总为缺失，不填零。','## 主要终点：持续95%占位的封顶建立时间','连续5个200sweep采样点≥95%记为达到；未达到保留在20000封顶。效果正值表示定向更快。区间为20种子配对bootstrap20000次的描述性95%区间，未作多重比较校正。不是成功者条件均值，也不是所有失败者的真实达到时间。']
v=e[(e.cap==-1)&(e.metric=='time0.95')].copy();v['规则']=v.rule.map(names)
out.append(table(v[['fraction','lam','规则','effect','low','high','positive','negative']]))
out+=['![建立时间差](figures/time_effects.png)','## 全过程占位与达到数','与时间一起报告AUC和失败，避免封顶并列被误称等效。']
v=s.copy();v['规则']=v.rule.map(names);v['方向']=v['mode'].map({7:'定向',8:'随机'})
out.append(table(v[['fraction','lam','规则','cap','方向','reached','extinct','time','auc','late']]))
out+=['## 实际稳定性与变异账目','以下max_step/max_abs_child为每条件跨种子最大值；sum_norm/sum_sq为每run累计量的种子均值；p99_step为每run出生步长99%分位数再取均值。上限触发比例在仍允许写回的出生中计算；原始无约束的触发率为零不表示其候选满足约束。',table(v[['fraction','lam','规则','cap','方向','births','updates','sum_norm','sum_sq','p99_step','max_step','max_abs_child','norm_hit','box_hit']]),'![稳定性最大值](figures/stability.png)','## 规则改变后，方向收益变化','以下是约束规则的配对方向收益减原始规则收益；负值表示方向收益缩小。每个单元先在同seed上作差，再bootstrap。约束同时改变学习遗传信号与生态历史，不能据此计算“原收益多少百分比来自不稳定”。',table(d),'## 提前停止写回的辅助检查','仅box规则B1024；不把它与持续写回合并。出生次数额度相同仍不代表累计改变量相同。', '![有限写回](figures/quota.png)','## 验证','开发：原mode7/8七类输出精确复现；lambda0与eta0生态负控一致；30000个合成父代约束与零支持检查通过。正式：人口、能量、不可达状态写入、所有逐出生改变量账目、共同几何与参数界验证；代表性运行八类输出精确复跑；240对连续/有限分支在第1024个非零更新前一致。原协议和源码哈希未变化。', '分析验证：'+json.dumps(json.loads((R/'validation/analysis.json').read_text()),ensure_ascii=False),'复跑验证：'+json.dumps(json.loads((R/'validation/final_checks.json').read_text()),ensure_ascii=False),'## 推断限制','这是同一生态系统中的稳定性干预，不能声称独立迁移。阈值、规则、种子和终点先固定，没有筛掉大幅更新、灭绝或未建立运行。未进行事后功效推断；未把区间跨零当作等效；未把多条件描述性区间当家族错误率控制。正式原始规则复现的新种子结果与既有种子结果应分别解释，不能通过选择种子或规则维持正结论。','数据使用：run_summary.csv为种子级统计，summary.csv为分组均值，paired_effects.csv和effect_change.csv为配对效应；raw/保存所有逐出生、寿命、轨迹和审计，validation/保存协议哈希及验证记录。']
text='\n\n'.join(out)+'\n'
if (R/'INTERPRETATION.md').exists():text=text.replace('## 预定问题与解释边界',(R/'INTERPRETATION.md').read_text()+'## 预定问题与解释边界')
(R/'report.md').write_text(text)
print('Base report saved; add verified interpretation before packaging.')
