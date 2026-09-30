from pathlib import Path
import pandas as pd
R=Path(__file__).resolve().parents[1]
s=pd.read_csv(R/'summary.csv');e=pd.read_csv(R/'paired_effects.csv');i=pd.read_csv(R/'interaction_effects.csv')
labels={'continuous':'持续写回','count1024':'固定1,024次','time150':'共同150 sweep截止','time750':'共同750 sweep截止'}
s['regime']=s.regime.map(labels);s['mode']=s['mode'].map({7:'定向',8:'随机'})
pretty=s.rename(columns={'regime':'制度','mode':'方向','n':'种子数','time':'封顶建立时间','reached':'建立数','extinct':'灭绝数','auc':'全程占位AUC','late':'最后五点占位','updates':'实际写回次数','sum_norm':'累计L2','sum_sq':'累计平方量','births':'总出生数','cutoff':'实际截止时刻'})
html='''<!doctype html><html lang="zh-CN"><meta charset="utf-8"><title>Paper 1 截止规则诊断</title><style>body{max-width:1120px;margin:40px auto;padding:0 24px;font:17px/1.7 system-ui;color:#243341}h1,h2{line-height:1.3}table{border-collapse:collapse;font-size:14px;width:100%}th,td{border-bottom:1px solid #ccd6dd;padding:9px;text-align:right}th:first-child,td:first-child{text-align:left}img{width:100%}.scroll{overflow-x:auto}.lead{background:#edf7f7;padding:20px;border-left:4px solid #147d92}</style>
<h1>固定次数与共同时间截止：小型诊断结果</h1>
<p>2026-09-30 · 160/160条完成 · 20个新配对种子 · 单一预定生态条件</p>
<h2>Material Passport</h2><p>本地计算实验；协议在正式运行前冻结，代码与协议哈希已验证。条件来自旧结果，种子102000–102019为新运行；统计单位20个种子，不是160个独立样本。没有修改稿件。</p>
<p class="lead"><b>固定次数制度中的定向劣势在共同750 sweep截止时消失并转为定向优势。</b>共同150 sweep截止时两组均未建立，但定向全程占位更高。因此，反转依赖截止制度；尚不能归因为纯时间作用或新的普适继承机制。</p>
<h2>预定设计与主要结果</h2><p>L32、资源补给.06、子代能量份额.65、λ=1、η=.2、μ=0；双方使用相同参数范围和单步上限。达到指标为连续五个200-sweep采样点占位≥95%的第一个采样时刻；未达到者保留，封顶20000。没有学习关闭、遗传状态清除或中途扩样。</p>
'''
html+=pretty[['制度','方向','建立数','封顶建立时间','全程占位AUC','最后五点占位']].to_html(index=False,float_format=lambda x:f'{x:.4f}',border=0)
html+='''<p>全部运行无灭绝。共同150时的封顶时间并列20000表示都未达标，不能解释为等效；其定向−随机AUC差为0.1261，描述性95%区间[0.0991,0.1551]。</p>
<p>主要预定比较：时间750相对固定次数，随机−定向的封顶建立时间差改善15930 sweep，配对bootstrap描述性95%区间[13470,18190]。时间750内部，定向平均1000、随机7520，差6520 [4400,8990]。建立率差只有20/20对18/20，其描述性区间包含零，不单独宣称成功率显著提高。</p>
<img src="occupancy.png" alt="四制度全程占位曲线与逐时点bootstrap区间">
<h2>实际预算揭示的解释边界</h2>'''
html+='<div class="scroll">'+pretty[['制度','方向','实际截止时刻','实际写回次数','累计L2','累计平方量','总出生数']].to_html(index=False,float_format=lambda x:f'{x:.2f}',border=0)+'</div>'
html+='''<p>持续组截止时刻−1表示无截止。固定次数组实际在平均136与722.7 sweep耗尽额度。共同750时，定向获得约3910次写回、随机约1094次；定向累计L2也从89.23增加到256.12。这说明延后机会伴随新增更新，不是等次数或等幅度的纯时间干预。</p>
<p>共同150时，随机仅获约444次，定向约1073次；随机表现下降同样涉及其机会减少。两种共同截止均偏向定向的占位结果，不足以证明存在独立的关键时间窗口。</p>
<img src="outcomes_budget.png" alt="封顶建立时间与实际写回次数比较">
<h2>对解释与下一步的影响</h2><p>新种子重复了持续写回收益和固定次数反转，并支持预先提出的“较晚共同截止削弱定向劣势”预测。最稳妥表述是：<b>全种群固定写回次数与繁殖速度耦合，使截止时间内生；继承收益比较对资源配置制度敏感。</b>这比“停止继承导致能力退化”准确，因为已有遗传信息保留且学习一直开启。</p>
<p>本轮不是无混杂中介分析，也不是时间、次数、幅度、生态状态同时匹配的比较。学习奖励与繁殖目标偏差、状态覆盖和种群选择仍可能参与结果。持续与750定向平均建立时间同为1000，也不能据此宣称两策略等效或已找到最优预算。</p>
<p>建议将此结果作为原论文的机制边界和对照设计支持。若继续追问纯时机作用，下一步应在固定1,024次额度下预先规定跨时间分配计划，使用共同幅度并保留无法用完额度者；此轮没有自动开展该实验，也不据此扩大AI benchmark。</p>
<h2>验证与统计限制</h2><p>开发检查验证：默认时间参数与原模拟器逐文件一致；截止前数值轨迹完全相同；时间0两方向轨迹相同；截止后写回归零。正式160条全部通过出生死亡账本、累计更新账本、共同范围、候选范数匹配、有限值与能量检查。</p>
<p>开发阶段全零列的CSV整数/浮点推断造成校验器两次类型断言，已在正式冻结前改为忽略类型但要求数值精确相等，未改变模拟逻辑。作图出现字体缓存目录不可写提示，最终两张图已生成并检查。</p>
<p>20种子配对bootstrap共20000次，区间为描述性，未作多重比较校正；失败保留，未仅对成功运行计算均值；无提前停止、结果驱动扩样或指标替换。条件依据旧数据挑选，不能外推到其他λ、资源、寿命或学习器。图中带为逐时点区间，不是全曲线同时置信带。截止附近人口仅有200 sweep采样分辨率，在逐运行表中保留前后采样时间，未伪装成精确截止人口。</p>
<h2>文件</h2><p><a href="PROTOCOL.md">冻结方案</a> · <a href="run_summary.csv">160条运行汇总</a> · <a href="paired_effects.csv">配对效应</a> · <a href="interaction_effects.csv">制度间效应变化</a> · <a href="analysis_bundle.zip">代码、报告与分析包</a> · <a href="raw_results.zip">原始日志压缩包</a></p></html>'''
(R/'report.html').write_text(html)
print('REPORT SAVED')
