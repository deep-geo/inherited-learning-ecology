from pathlib import Path
import json,html,base64
import pandas as pd
R=Path(__file__).resolve().parents[1];s=pd.read_csv(R/'summary.csv');e=pd.read_csv(R/'paired_effects.csv');a=pd.read_csv(R/'run_summary.csv')
def table(frame,cols):
 x=frame[cols].copy()
 def fmt(v):
  if pd.isna(v):return '—'
  if isinstance(v,float):return f'{v:.4f}' if abs(v)<1 else f'{v:.1f}'
  return str(v)
 return '| '+' | '.join(cols)+' |\n| '+' | '.join(['---']*len(cols))+' |\n'+'\n'.join('| '+' | '.join(fmt(v) for v in row)+' |' for row in x.itertuples(index=False,name=None))
r=f'''# Paper 1：编码复核、生态机制干预与强对照稳健性

## Material Passport
状态：三个预定实验模块全部执行完毕。80次开发、800次正式条件运行（表示200、机制240、稳健性360），另完成3次新结果精确复跑和原程序/no-op等价检查。正式每条件20seed，三个模块种子分别61000–61019、62000–62019、63000–63019；重复条件不构成额外独立seed。开发60000–60001不用作正式证据。800是条件运行数，不是800个独立随机种子。本报告使用本地原始数据，不含本轮新的外部文献或新颖性认证。

## 结论先行

本轮补强了“继承学习成果可以减少后代重新学习负担”的机制证据，同时发现一个必须写进论文的优势反转。可支持的主张是：在本资源受限细胞模型及固定范数更新干预下，定向继承的动作偏好可以加速种群建立；该收益依赖后代学习动力学与繁殖能量分配，不能概括为普适的适应或生存优势。

更粗的状态编码中，方向优势继续出现。预算耗尽后，仅清除新生后代的表现型偏好就大幅拖慢建立；提高其学习率可补偿大部分损失。然而，当出生能量更多分给子代、亲代保留更少时，主要随机对照反而表现更好。取消出生奖励并没有消除基准能量分配下的定向速度优势。

## 设计与主要指标

沿用上轮32×32环面、rest/harvest/divide动作、资源回补.06、标准死亡概率.002、初始25%占位、20,000sweep观察窗。q=.1841261006694567冻结，不按新结果调节。aligned保留学习更新方向；state_rotated保留同一父代候选更新的逐状态共同值、动作对比范数和状态支持，仅随机化动作方向；none无遗传改变。后者仍保留状态信息，并非完全无信息的变异。

主要终点是首次连续5个200sweep采样点达到95%占位的起始时间，跨度800sweep，并非每步连续监测保证。未达到者记为20000进入封顶平均，同时独立报告达到率、灭绝、全过程占位均值（AUC/T）和最后1000sweep的五点平均占位。表中capped_time不能被解释为失败运行的真实建立时间。90/99%为预定辅助，不替换主终点。

配对bootstrap使用20,000次重采样，种子为单位；95%区间是描述性的，未做多重比较校正，不据此宣称整个实验族的显著性。柱图为均值、标签为达标数；轨迹阴影为种子均值标准误，均不是成功率的精确总体概率。

## A：第二种状态编码

新编码把能量×资源从8×8变为4×4，can_divide仍单列，Q值从384降至96。它改变状态混叠，属于编码敏感性复核；生态引擎、学习算法共用，不能冒充独立实现、不同任务或真实细胞验证。q不依参数数量重新校准；跨编码绝对成绩不能单独归因遗传方向，主要比较在编码内部进行。

{table(s[(s.stage=='representation')&(s.method!='none')],['bins','budget','method','n','reached','capped_time','extinctions','auc'])}

4×4编码：512预算的时间优势为780sweep，95%描述性区间[630,940]；1024预算为580，[500,660]。两组在两预算都20/20达标。两预算方向一致且区间下界为正，达到预定的局部复核标准。原8×8编码也在另一批种子中复现方向优势。两个编码的none都0/20达标。

局部学习门中，两个编码在20个开发seed、三个典型固定情境的正确动作概率最低都为0.9667。门只保证rest、harvest、divide的典型情境可学，不能保证粗编码在所有混叠状态都能实现最优控制。

## B：在真实生态轨迹中的表现型干预

B=512。每种方向内部，各干预分支在用完预算前完全相同，检查前512次更新以及触发时刻前的人口、寿命和学习记录。消耗第512次更新的出生及后续出生中：keep令theta_child=g_child；erase将theta的每个状态三动作值都置为该状态g的均值。g保持不变，遗传更新已停止；不补能量、不补资源。出生前已存在个体不受干预，学习率保持.2。只对之后出生的个体改变学习率为0、.2或.8。

此操作清除的是新生个体行为表达中的继承偏好，不是删除遗传参数。提高eta是提高单次更新权重，不是增加实际交互次数，也不是免费额外训练。不同方向消耗预算的时刻不同（定向平均428.05sweep，随机760.65），因此同方向内部的配对干预具有更直接的因果含义，不能假定两个方向在干预时处于相同生态状态。

{table(s[s.stage=='mechanism'],['intervention','child_eta','method','reached','capped_time','extinctions','auc','final_occupancy'])}

intervention=1为保留偏好，2为清除偏好。主要eta=.2下，定向组保留时20/20达标、2480sweep；清除后6/20、18280sweep。配对清除损失为15800sweep，[14240,17070]；全过程占位损失0.23168，[0.20864,0.25509]。两组均没有灭绝，所以这主要是建立速度/占位收益，而非生存必要性。

同状态随机组也受清除影响：18/20、6450sweep变为5/20、17900sweep。遗传偏好本身对两组都可能有帮助，不能把随机对照称为“没有可继承知识”。标准学习率下，方向的封顶时间优势从3970变成−380，后者区间[−2940,2020]。优势减少4350，[1499.75,7300]；但全过程占位优势减少0.05288的区间[−0.00110,0.09822]跨0，且清除组大量运行封顶，不能宣称已证明完全中介或精确解释比例。

快速学习救援：清除偏好且eta=.8时，定向组恢复20/20、1610sweep，随机组20/20、2240sweep。控制保留组同样改变学习率后，定向的清除时间损失从15800降至400，差中差15400，[13860,16680]；占位损失减少0.22083，[0.19798,0.24416]。这同时支持偏好清除的直接损失和学习速率对损失的补偿，而不只是两组天生不同的相关性。

eta=0是辅助极限：清除后两组全部灭绝；保留时定向20/20达标，随机6/20。这不能替代标准学习率的主要机制检验。另一个限制是学习率并非越大越好：定向保留组eta=0平均1390，比eta=.2的2480更快，因此不能声称一般的单调学习收益。

## C：强对照下的生态条件边界

B=1024，原8×8编码，每次只改变一个生态参数。low/high_death分别为每次被选择活体访问的死亡概率.0005/.01，不是硬寿命。low/high_child_energy为子代能量份额.35/.65；亲代份额同时变为.65/.35，总能量严格守恒。不能将其解释为只改变子代能量而不影响亲代。

{table(s[s.stage=='robustness'],['setting','method','reached','capped_time','extinctions','auc','final_occupancy','quota_used'])}

基准下定向1460、随机3190sweep。低死亡下1000对1730；子代份额.35下1530对3160；取消出生奖励后2160对3560，后三情境两组都20/20达标。故基准优势不完全由+.2出生奖励驱动。

**关键反例：子代份额.65时，定向0/20达标，随机18/20。** 定向20个种群仍存活，末期平均占位0.8525，随机0.9797；全过程占位为0.8137对0.9081，差值−0.09441，[−0.11084,−0.07602]。90%阈值下达标数仍为1/20对20/20，99%为0/20对9/20。因此反转不只来自选取95%阈值，也不能误写成定向组全部灭绝。

事后生态收支诊断显示，在该情境中定向平均出生109609次、能量死亡75540次，随机约65389次、27309次；提示更高周转与能量死亡可能有关。但这些是结果后的描述性诊断，尚未通过独立机制干预确认，不能直接归因为过度繁殖或奖励错误。

高死亡.01下，两组都0/20达标、20/20灭绝，实际遗传更新平均仅275.8和225.2次，均未用满1024额度。失败全部保留；这里不能声称两组实际累计更新预算相同，也不能把时间差0当成生态等效。其余正式主要变异条件都用满额度。低死亡情境中none也20/20达标、平均3340，进一步说明继承不是任何环境下建立种群的必要条件。

## 主要效应完整表

以下时间优势统一为随机减定向，正值偏向定向，负值偏向随机；机制损失/救援的详细区间另存paired_effects.csv，不据结果删选。

{table(e[(e.kind=='direction_advantage')&(e.metric=='capped0.95')],['stage','bins','setting','budget','intervention','child_eta','effect','low','high'])}

## 验证、预算与可复现性

所有80开发和800正式运行完成并通过人口收支、能量/分配、范数、逐状态随机化与不可达写入检查。两个维数各10,000组旋转测试通过。新引擎在原编码下精确复现旧引擎指标、更新、寿命和学习记录；keep/.2的no-op分支与原过程精确一致。三项正式代表运行的全部七种输出文件精确复跑一致。

开发到正式四批的模拟代码、测试代码、头文件、运行器与协议哈希一致。机制分支前512次更新和触发前历史完全一致；干预保持逐状态共同值，保留组theta=g误差为0。全部主要方法没有向物理不可达状态写入变化，所有条件零学习方向跳过数为0。高死亡的预算未用满是结果而非实现失败，单独记录。

遗传预算匹配仍针对同一父代候选的几何，不代表生态分叉后的状态访问或群体累计动作对比能量完全相同，也不是Shannon信息量或行为KL匹配。能量/遗传量审计不等同于生态适应度最优性的证明。

## Paper 1当前证据与停止边界

可写入主结果：更强对照下的方向速度优势；遗传改变量预算曲线；另一分箱表示的复核；出生后偏好清除与快速重学救援；繁殖能量分配导致优势反转，且高死亡与低死亡提供不同失败/替代边界。

适合的论文论点是“继承的后天行为偏好可以减少代际重复学习的负担，其种群收益受生态约束，甚至可能反转”。前缀应明确限定这个资源受限模型及固定范数干预，而不是通用定律。

本次承诺的三个实验模块已经完成，可据此组织方法和结果。尚未覆盖：独立生态软件实现/不同任务、真实细胞湿实验、自然lambda写回规则下对全部新结论的复核、全部速度收益的因果中介分解，以及能量分配反转的专门机制确认。相变与长期可进化性仍不在已支持主张内。新颖性与投稿准备度不能由这800次运行自动认证；本轮不追加参数扫描来隐藏反例。
'''
(R/'report.md').write_text(r)
parts=[];lines=r.splitlines();i=0
while i<len(lines):
 line=lines[i]
 if line.startswith('| '):
  block=[]
  while i<len(lines) and lines[i].startswith('| '):block.append(lines[i]);i+=1
  parts.append('<div class="table"><table>')
  for k,row in enumerate(block):
   if k==1:continue
   tag='th' if k==0 else 'td';parts.append('<tr>'+''.join(f'<{tag}>{html.escape(v.strip())}</{tag}>' for v in row.strip('|').split('|'))+'</tr>')
  parts.append('</table></div>');continue
 if line.startswith('# '):parts.append('<h1>'+html.escape(line[2:])+'</h1>')
 elif line.startswith('## '):parts.append('<h2>'+html.escape(line[3:])+'</h2>')
 elif line:parts.append('<p>'+html.escape(line).replace('**','')+'</p>')
 i+=1
for name,title in [('representation','状态编码复核'),('mechanism','偏好清除与快速重学救援'),('mechanism_trajectories','标准学习率下的完整占位轨迹'),('robustness','生态边界与反转')]:parts.append('<h2>'+title+'</h2><img alt="'+title+'" src="data:image/png;base64,'+base64.b64encode((R/'plots'/f'{name}.png').read_bytes()).decode()+'">')
(R/'report.html').write_text('<!doctype html><html lang="zh-CN"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Paper 1：剩余证据实验</title><style>body{max-width:1200px;margin:36px auto;padding:0 24px;font:17px/1.8 system-ui;color:#172334}h1,h2{line-height:1.35}h2{margin-top:2em}table{border-collapse:collapse;font-size:13px;white-space:nowrap}td,th{border:1px solid #ddd;padding:6px}th{background:#edf3f8}.table{overflow-x:auto}img{width:100%;height:auto}</style></head><body>'+''.join(parts)+'</body></html>')
print('Report saved')
