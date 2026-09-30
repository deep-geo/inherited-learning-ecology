from pathlib import Path
import pandas as pd,html,base64
R=Path(__file__).resolve().parents[1];s=pd.read_csv(R/'summary.csv');s=s[s.stage=='confirmation'];e=pd.read_csv(R/'paired_effects.csv');a=pd.read_csv(R/'run_summary.csv')
def table(frame,cols):
 def fmt(v):
  if pd.isna(v):return '—'
  if isinstance(v,float):return f'{v:.4f}' if abs(v)<1 else f'{v:.1f}'
  return str(v)
 return '| '+' | '.join(cols)+' |\n| '+' | '.join(['---']*len(cols))+' |\n'+'\n'.join('| '+' | '.join(fmt(v) for v in row)+' |' for row in frame[cols].itertuples(index=False,name=None))
primary=s[(s.cap==-1)&(s.method!='none')];bounded=s[(s.cap==1024)&(s.method!='none')]
results=f'''### 原始比例写回下的建立速度

在持续写回、无更新次数上限的主要比较中，两种出生能量分配、三个非零lambda的全部定向与同状态随机条件均20/20达到持续95%占位。定向组在每个预定组合的20个配对seed中都更快，且全过程占位均更高。基准能量对半时，lambda=.25、.5、1的定向/随机平均建立时间依次为2490/4040、1490/2840、930/2330sweep。子代份额.65时，依次为2060/2730、1170/1940、660/1520。

{table(primary,['fraction','lam','method','reached','capped_time','auc','late'])}

基准时间优势为1550[1450,1650]、1350[1250,1450]和1400[1310,1490]sweep；子代份额.65时为670[560,790]、770[710,830]和860[770,950]。方括号为配对95%描述性区间，未做多重比较校正。两环境的无写回参照均0/20达到、20/20灭绝。这支持定向收益不只存在于固定q归一化规则，但仍限于所测模型和参数范围。

### 更新截止规则改变了相对表现

在1024次非零更新上限下，子代份额.65、lambda=.5时，定向0/20达到，对照17/20；lambda=1时为5/20对20/20。lambda=.25时两组均0/20达到，但全过程占位为0.6863对0.7339，故终点封顶相同不代表轨迹相同。这些种群均未灭绝。

{table(bounded,['fraction','lam','method','reached','capped_time','auc','late'])}

同一能量份额在持续原始写回下并未反转，因此不能把上一轮的反例仅归因于能量分配。更新是否提前终止与写回强度共同限定观察到的生态结果。本轮在每个seed/方向/lambda/环境下验证了有限与无限额度分支到第1024次非零更新的完整更新记录相同，共240对；这不是用不同初始条件替换了比较。

基准份额.5、lambda=.25且截止1024次时，也出现建立终点上的反转：定向7/20达到、封顶均值17790，对照20/20、4900。然而全过程占位定向0.8444略高于对照0.8303，末期占位则较低（0.9482对0.9878）。90%阈值两组都20/20达到、均值5330对4520；99%为0/20对8/20。不能把这个条件简化为“随机在所有指标上更好”，也不能用辅助阈值替换预定95%主终点。

### 自然累计遗传量并未匹配

在原始写回中，每次位移由父代学习状态决定。即使1024次额度全部用满，两组累计L2和平方量仍不同。例如基准lambda=.5有限额度下，定向/随机累计L2均值约99.10/158.09，平方量13.28/30.03。此轮比较证明的是原始过程中的总体表现差，不是相同累计变异预算下的效率差。

持续写回时随机组的遗传幅度可明显放大。在子代份额.65、lambda=1时，累计平方量的随机组中位数约15343，定向约567；随机均值约480899，被一个9.31e6的运行明显拉高。该运行最大单次L2约1664.48，保留在全部主分析中。定向原始规则在lambda介于0和1时是g与theta的凸组合，旋转更新不保留同样的逐坐标凸包性质；因此不能把自然过程中的全部差异仅解释为幅度相同的遗传信息效果。
'''
r=f'''# Paper 1：原始比例写回连接实验

## Material Passport
状态：52次开发、520次正式条件运行已完成，另2次正式代表条件精确复跑及1次带数值断言的诊断复跑。每正式条件20seed，全部条件共享81000–81019进行配对，不是520个独立seed。开发80000–80001不计入正式证据。本轮使用mu=0，未扫描突变与写回的交互。方法与结果工作初稿已单独保存，不含新的外部文献或新颖性认证。

## 结论与对旧解释的修正

**原始规则下的关键收益得到支持。** 取消固定幅度归一化、允许持续写回后，两种能量分配和三个预定lambda中，定向继承都加快了建立，且全过程占位更高。

**先前反转需要更精确地限定。** 在子代份额.65下，原始持续写回没有反转，但1024次遗传更新截止后仍在部分lambda出现反转。因此不能写成“高子代能量份额本身使定向继承更差”；应表述为写回强度、更新截止与生态分配共同限定收益。

此轮完成固定q干预与原始lambda模型的连接，但自然群体的累计遗传量不同，不能替代之前固定q的幅度匹配证据。出生后偏好清除与快速重学救援仍来自上一轮固定q机制实验，本轮未在原始lambda下重做该机制干预。

## 冻结设计与统计口径

L32,T20000，8×8×2状态，eta=.2、epsilon=.05、资源回补.06、背景死亡.002、出生奖励.2。lambda={{.25,.5,1}}，子代能量份额{{.5,.65}}，更新额度{{无限,1024}}，方向{{定向,同状态随机}}。none为lambda0，每环境每seed共享一次。随机对照保留该父代候选的逐状态共同值、动作对比范数及状态支持，不对位移归一化。所有原始位移均保存，不裁剪大变化，不对近零变化设置人为下限。

主要终点为连续5个200sweep采样点占位>=95%的首次起始时刻。未达到者封顶20000，不能当作其真实建立时间；同时报告灭绝、全过程占位AUC/T和末1000sweep五点平均。所有正式变异组均未灭绝，无写回参照均灭绝。所有有限额度的主要组都用满1024次更新，但累计变化幅度并不相等。

种子为统计单位，20000次配对bootstrap区间为描述性，未校正多重比较。所有lambda均报告，不筛选最佳lambda或删除失败样本。90/99%仅辅助。

## 实验结果

{results}

## 全部主要时间效应

正值为随机时间减定向时间，偏向定向；负值偏向随机。

{table(e[e.metric=='capped0.95'],['fraction','cap','lam','effect','low','high','positive','negative'])}

## 遗传变化总账

sum_norm和sum_sq分别为每run累计L2和累计平方量的种子均值；mean_nonzero_norm先按run计算每次非零更新均值，再跨seed平均。max_write_norm为该条件所有seed中的最大单次值。无上限cap=-1、有限cap=1024。

{table(s[s.method!='none'],['fraction','cap','lam','method','births','updates','sum_norm','sum_sq','mean_nonzero_norm','max_write_norm'])}

## 验证与数值审计

人口、能量分配、公式与原始norm核验通过。旧mode0与新原始定向的生态、寿命、学习输出精确一致；把旧q参数改为99不改变两个原始方法的结果，确认没有隐含归一化。lambda0在方向间不变；eta0在写回参数和方向间不变。lambda1时定向子代与父代表现型的公式误差在容差内。开发到正式的模拟代码和协议哈希一致，两个正式代表条件七类输出精确复跑。

实现检查初次误将eta0过程与eta=.2/lambda0过程比较，后来纠正为各自学习率内部比较。初始错误断言保留在validation，模拟器、指标和正式方案未据此调整。初次编排未fail-fast，开发运行仍执行；正式批次在修正检查通过后使用fail-fast执行。

seed81006、子代份额.65、lambda1、无上限随机组的逐状态平方范数误差4.66e-10超过原绝对阈值1e-10。对原源码仅添加逐行相对误差断言的诊断构建复跑，要求均值/范数/对比误差不超过对应行尺度的256倍double机器精度，全部通过；七类输出逐字节一致。因此是大幅度下的舍入误差，不是匹配几何失败。该运行没有被删除、缩幅或替换；数值通过不代表大位移没有科学意义。

## Paper 1应采用的证据链

固定q强对照支持：在特定预算与生态下，任务相关方向本身有建立速度优势。原始lambda连接实验支持：该收益不只来自人工固定幅度归一化，持续比例写回也出现优势。后代清除/救援实验支持：在所测固定q设置中，继承偏好减轻重新学习负担。有限更新反例支持：优势不是无条件的，截止规则、写回强度、能量分配与评价指标均影响结论。

可以开始围绕“后天行为偏好的代际保留及其生态收益边界”组织稿件。不能据此写成普适适应优势、独立突变相图、真实细胞证据或完整因果中介。反转的具体机制和跨任务普适性未在本轮补做，符合本轮只完成连接实验的范围。
'''
(R/'report.md').write_text(r)
base=(R/'code/methods_base.md').read_text();before=base.split('## 结果')[0].replace('当前先冻结方法表述；本轮原始比例写回结果完成后追加结果节。','已整合完成本轮原始比例写回结果。');declarations=base.split('## 声明与待补内容')[1]
prior='''### 固定幅度强对照与预算机制

在前一轮同状态强对照的无上限确认中，定向与随机均20/20建立，平均1290对3040sweep。预算512时为20/20对18/20，封顶平均2290对7160。更粗4×4编码下，预算512时两组均20/20建立，1180对1960；预算1024时1020对1600。该编码复核共用生态引擎。

在独立的出生后机制实验中，定向组标准学习率下保留偏好时20/20建立、平均2480；清除后6/20、封顶均值18280。清除条件将后代学习率提高到.8后恢复20/20、平均1610。这支持偏好表达的生态作用及更快重新学习对其损失的补偿，不能据此宣称完整中介比例。该机制干预使用固定q，不是本轮原始lambda规则。

先前固定q、预算1024且子代份额.65时，定向0/20建立、随机18/20，定向种群仍存活。下文的新连接实验将这一反例限定到写回规则、额度和生态共同决定的范围。

这些先前数值分别来自paper1_state_matched与paper1_completion的冻结批次，与本轮81000–81019种子不同。跨批次表格不是配对比较。

'''
limitations='''## 讨论与适用范围

结果支持一个有条件的论点：生命周期获得的动作偏好可以通过遗传初始化减少后代重新学习的负担，并在所测持续比例写回过程中加快种群建立。该论点由幅度匹配干预、出生后偏好清除及学习救援、原始写回连接三类证据共同支持，但各证据适用的具体规则必须分别标明。

生态边界应围绕信息更新机会与生存繁殖过程的相互作用表述，而不能将一次能量份额反例写成单因素普遍规律。在持续写回下，所测高子代能量份额并未使定向组更差；有限更新后则可出现相反排序。达到高占位、全过程占位和末期占位也不总给出相同排序。

本研究未把局部奖励等同于适应度，未把参数L2等同于Shannon信息，未检验相变或长期可进化性。另一分箱表示并非独立生态实现。原始比例写回实验中的随机对照可产生更大的累计变化，其长期几何不受定向凸组合的相同约束；自然过程的结果不能直接替代固定总变化预算下的方向效应。本稿的新颖性与近邻文献比较仍待单独完成。

'''
(R/'METHODS_RESULTS_DRAFT.md').write_text(before+'## 结果\n\n'+prior+results+'\n\n'+limitations+'## 声明与待补内容'+declarations)
def render(md):
 parts=[];lines=md.splitlines();i=0
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
  if line.startswith('#'):
   level=len(line)-len(line.lstrip('#'));parts.append(f'<h{level}>'+html.escape(line[level:].strip())+f'</h{level}>')
  elif line:parts.append('<p>'+html.escape(line).replace('**','')+'</p>')
  i+=1
 return ''.join(parts)
head='<!doctype html><html lang="zh-CN"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Paper 1 原始写回连接实验</title><style>body{max-width:1200px;margin:36px auto;padding:0 24px;font:17px/1.8 system-ui;color:#172334}h1,h2,h3{line-height:1.35}h2{margin-top:2em}table{border-collapse:collapse;font-size:13px;white-space:nowrap}td,th{border:1px solid #ddd;padding:6px}th{background:#edf3f8}.table{overflow-x:auto}img{width:100%;height:auto}</style></head><body>'
figs=''.join('<h2>'+title+'</h2><img alt="'+title+'" src="data:image/png;base64,'+base64.b64encode((R/'plots'/f'{name}.png').read_bytes()).decode()+'">' for name,title in [('establishment','建立时间与达到数'),('occupancy','全过程占位'),('variation_budget','实际累计遗传位移'),('trajectories','持续写回的完整占位轨迹')])
(R/'report.html').write_text(head+render(r)+figs+'</body></html>');(R/'METHODS_RESULTS_DRAFT.html').write_text(head+render((R/'METHODS_RESULTS_DRAFT.md').read_text())+'</body></html>');print('Report and methods/results draft saved')
