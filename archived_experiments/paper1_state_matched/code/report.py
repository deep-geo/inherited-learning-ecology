from pathlib import Path
import pandas as pd,html,base64
R=Path(__file__).resolve().parents[1];s=pd.read_csv(R/'summary.csv');e=pd.read_csv(R/'paired_effects.csv')
def table(df):
 return '| '+' | '.join(df.columns)+' |\n| '+' | '.join(['---']*len(df.columns))+' |\n'+'\n'.join('| '+' | '.join(f'{v:.4f}' if isinstance(v,float) else str(v) for v in row)+' |' for row in df.itertuples(index=False,name=None))
main=s[s.stage=='confirmation'][['condition','n','reached','capped_time','extinctions','final_occupancy']]
pair=s[(s.stage=='budgets')&s.condition.isin(['aligned_q','state_rotated_q'])][['budget','condition','reached','capped_time','extinctions','budget_exhausted']]
eff=e[(e.comparison=='aligned_q vs state_rotated_q')&(e.metric=='capped0.95')][['stage','budget','advantage','low','high','positive']]
r=f'''# 同状态动作方向对照与遗传更新预算曲线

## Material Passport
实验1和2均已完成。开发45次、实验1独立确认100次、实验2预算曲线420次，共565次条件运行，另2次精确复跑。开发seed50000–50004；确认51000–51019；预算52000–52019。每个条件20seed，不把重复预算或每个时间点当成独立seed。没有启动实验3或4。

## 核心结论与必须修正的旧解释

同状态随机方向对照比原来的全空间随机对照强得多。无额度时，新对照20/20建立种群，平均3040sweep；定向组也是20/20、平均1290sweep。预算512时，定向20/20达到、新对照18/20达到，成功率差距远小于之前相对全空间随机的20/20对2或3/20。

因此，不应继续把旧的巨大建立率差异完全归因于动作方向。新对照同时保留更新位置、逐状态幅度与共同动作值，说明旧对照混合了这些因素；本轮没有进一步分离它们各自的贡献比例。

**更可靠的结论是：在控制更新状态位置、共同平移与逐状态动作对比范数后，定向动作偏好仍在所测足够预算范围内加快种群建立；不保证低预算下能够建立，也没有证明方向信息是建立种群的必要条件。**

## 实验1：同一状态内部随机化动作偏好

每个状态s的三动作遗传更新分解为d_s=m_s(1,1,1)+c_s，其中sum(c_s)=0。state_rotated_q保留m_s及||c_s||，在二维零和动作平面随机旋转c_s，不把更新搬到其他状态。先将整个父代学习位移归一到q=0.1841261006694567，再逐状态旋转。该对照保留了状态级的学习信息，并非完全无信息随机变异。

它与该父代的定向候选逐状态匹配：共同值、总范数、对比范数、零状态支持。三动作内部的零坐标可以改变，不声称保留逐动作稀疏性。共同平移虽不立即改变贪婪动作排序，却可能影响后续Q学习，因此明确保留。

能量bin0–3且can_divide=1对应32个物理不可达状态，即96/384参数。定向与新对照都完全不向这些参数写入变化。全空间随机对照仍保留为参照，而不是主证据。

固定低资源生态L32,T20000,r=.06,死亡概率.002，主结果如下：

{table(main)}

新对照时间减去定向时间的差值为1750sweep，配对bootstrap95%描述性区间[1650,1850]，20/20种子方向为正。两者终点占位都接近满员，所以主要证据是建立速度，不是独占的长期性能优势。

“建立”预先定义为连续5个200sweep采样点占位≥95%的首次起始时刻，跨度800sweep；不是逐步连续监测保证。未达到者封顶记20000并单列；实验1这两个主要条件均全部达到，故此处均值不含失败惩罚。

## 实验2：128到2048次非零遗传更新预算

使用另一批20个独立seed，同一seed跨预算配对。上限按实际非零遗传更新计数；原先若无可用学习方向的回退，在本轮预先规定为跳过而不注入不匹配支持的随机变化。实际565次条件运行都没有出现零方向跳过。

{table(pair)}

上述两个主要条件在每个预算、每个seed都用完额度，因此每一预算下实际更新次数、累计L2及累计平方范数均相同。每次q不变，累计L2为Bq、平方范数为Bq²。没有排除未用完者来人为匹配。

- B=128：两组都未达到，且全部灭绝。
- B=256：两组都未达到95%；定向仍有17/20存活，新对照7/20存活，故“都未达标”不等于整个轨迹相同。
- B=512：定向20/20达到，新对照18/20达到、没有灭绝。2290与7160是包含未达到者惩罚的封顶平均时间，不能把7160当成成功者的真实平均到达时间。
- B=1024及2048：两组都20/20达到，定向在全部配对seed上更快。

时间优势与区间：

{table(eff)}

这些结果支持足够预算下的速度优势，但不支持“任何预算下定向都更好”。128/256处的零时间差是终点封顶效应。20/20和18/20的成功率差异也不足以单独断言总体建立概率明显不同。两个主要方法在本预算网格上都从512开始达到至少80%的样本建立率；不能宣称已证明定向把这个预算需求减半。

在有限样本中，100%达到的最小已测预算分别是512和1024；它仅是样本/离散网格描述，不是群体成功概率100%的保证，也不是精确预算阈值或相变。

## 旧对照、未用完额度与预算口径

全空间打乱和各向同性随机的结果完整保留。在1024/2048上限各有1/20未用完额度；它们的灭绝和未达到保留在主要汇总中，不宣称这些组的实际总预算全部相等。它们向不可达参数写入约四分之一平方范数，而主要匹配对照的该值严格为0。

逐状态匹配针对同一父代的定向反事实候选。真实生态轨迹分叉后，不同群体并不会有完全相同的状态访问、共同值/对比能量比例、出生时间或选择过程。例如512预算下，定向与新对照的累计动作对比平方范数种子均值分别约11.926和12.286，而总平方范数都为17.358。新对照没有在平均意义上少用动作对比能量，但这也不是两群体逐状态累计预算完全相等的实验。

本轮不声称直接匹配行为策略变化的KL距离、Shannon信息量或所有生态路径。q固定幅度是方向机制干预，并非原生固定lambda写回规则的同义替换。

## 验证与复现

1万组独立向量测试通过。实际生态中最大逐状态均值误差约1.39e-17，状态范数平方误差2.78e-17，对比范数平方误差2.43e-17，空状态支持误差为0。人口/出生/死亡账、能量和父子分配、实际额度、逐次更新账均通过。

开发、确认、预算和复跑的模拟源码、控制函数、奖励头文件与协议哈希完全一致。所有预算在相同seed/条件的前128次出生更新前缀一致；两种主要方法在预算512的一个预算实验seed上精确复现指标、寿命、学习记录和更新账。

每次出生记录总L2、对比/共同平方范数、不可达状态写入量、是否用额度和零方向跳过。末期活体寿命右删失，灭绝占位0，空种群策略量NaN。图中曲线阴影为seed均值标准误；成功率图是20seed的样本比例，未画置信带，不表示总体精确概率。

所有配对区间为seed bootstrap95%描述性区间，未做多重比较校正。90/99%阈值结果与完整轨迹均保存，未取代预先指定95%主指标。本轮没有湿实验、第二表示、环境切换或长期可进化性测量。

## 对Paper 1的含义

论文应以新对照为主，把旧全空间随机对照作为辅助。现有结果更适合围绕“更新位置与动作方向的不同作用，以及足够但有限预算下的建立速度”组织，而非“定向信息决定能否存活”的宽泛叙事。

下一项待补证据仍是独立表示/生态实现中的关键结果复核；本轮没有执行，也没有把重复seed扩充冒充该复核。相变不是必要目标。
'''
(R/'report.md').write_text(r)
parts=[];lines=r.splitlines();i=0
while i<len(lines):
 line=lines[i]
 if line.startswith('| '):
  block=[]
  while i<len(lines) and lines[i].startswith('| '):block.append(lines[i]);i+=1
  parts.append('<div style="overflow-x:auto"><table>')
  for j,row in enumerate(block):
   if j==1:continue
   tag='th' if j==0 else 'td';parts.append('<tr>'+''.join(f'<{tag}>{html.escape(v.strip())}</{tag}>' for v in row.strip('|').split('|'))+'</tr>')
  parts.append('</table></div>');continue
 if line.startswith('# '):parts.append('<h1>'+html.escape(line[2:])+'</h1>')
 elif line.startswith('## '):parts.append('<h2>'+html.escape(line[3:])+'</h2>')
 elif line:parts.append('<p>'+html.escape(line).replace('**','')+'</p>')
 i+=1
for name,title in [('budget_curves','预算、达到率与预算使用'),('occupancy_curves','确认与512次上限的占位轨迹'),('paired_effects','主要配对时间优势')]:parts.append('<h2>'+title+'</h2><img src="data:image/png;base64,'+base64.b64encode((R/'plots'/f'{name}.png').read_bytes()).decode()+'">')
(R/'report.html').write_text('<!doctype html><html lang="zh"><meta charset="utf-8"><title>同状态随机方向对照</title><style>body{max-width:1200px;margin:36px auto;padding:0 24px;font:17px/1.75 system-ui;color:#172334}h1,h2{line-height:1.3}table{border-collapse:collapse;font-size:13px}td,th{border:1px solid #ddd;padding:6px}img{max-width:100%}</style>'+''.join(parts)+'</html>')
print('Report saved')
