from pathlib import Path
import html,base64,re,zipfile,json,hashlib,platform
R=Path(__file__).resolve().parents[1]
def inline(s):
 s=html.escape(s);return re.sub(r'\*\*(.+?)\*\*',r'<strong>\1</strong>',s)
out=[];in_table=False
for line in (R/'report.md').read_text().splitlines():
 if line.startswith('|'):
  if re.fullmatch(r'[| :\-]+',line):continue
  if not in_table:out.append('<div class="table"><table>');in_table=True
  out.append('<tr>'+''.join('<td>'+inline(v.strip())+'</td>' for v in line.strip('|').split('|'))+'</tr>');continue
 if in_table:out.append('</table></div>');in_table=False
 if line.startswith('!['):
  p=R/line.split('](')[1][:-1];out.append('<img src="data:image/png;base64,'+base64.b64encode(p.read_bytes()).decode()+'">')
 elif line.startswith('#'):
  n=len(line)-len(line.lstrip('#'));out.append(f'<h{n}>'+inline(line.lstrip('# '))+f'</h{n}>')
 elif line:out.append('<p>'+inline(line)+'</p>')
if in_table:out.append('</table></div>')
(R/'report.html').write_text('<!doctype html><html lang="zh"><meta charset="utf-8"><title>原始写回稳定性</title><style>body{font:16px/1.65 system-ui;max-width:1120px;margin:40px auto;padding:20px;color:#18342d;background:#fbfcfb}h1,h2{color:#12634d}img{width:100%}.table{overflow-x:auto}table{border-collapse:collapse;font-size:13px;width:100%}td{border:1px solid #cddbd5;padding:7px;white-space:nowrap}tr:first-child{background:#e4f0eb;font-weight:600}</style>'+''.join(out)+'</html>')
files=[]
for p in R.rglob('*'):
 if not p.is_file() or '__pycache__' in str(p) or p.suffix=='.zip':continue
 rel=p.relative_to(R)
 if rel.parts[0]=='raw' or 'development' in rel.parts or p.name.startswith('replay_'):continue
 if p.name=='manifest.json':continue
 files.append(p)
(R/'manifest.json').write_text(json.dumps({str(p.relative_to(R)):hashlib.sha256(p.read_bytes()).hexdigest() for p in files},indent=2))
with zipfile.ZipFile(R/'analysis_bundle.zip','w',zipfile.ZIP_DEFLATED) as z:
 for p in files+[R/'manifest.json']:z.write(p,Path(R.name)/p.relative_to(R))
 for name in ['sim','sim.cpp','rotation.hpp','local_rule.hpp']:
  p=R.parent/'paper1_native_writeback/code'/name;z.write(p,Path('paper1_native_writeback/code')/name)
with zipfile.ZipFile(R/'analysis_bundle.zip') as z:assert z.testzip() is None
print('analysis_bundle bytes', (R/'analysis_bundle.zip').stat().st_size)
