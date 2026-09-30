from pathlib import Path
import hashlib,zipfile
R=Path(__file__).resolve().parents[1]
files=sorted(p for p in R.rglob('*') if p.is_file() and '__pycache__' not in p.parts and p.name!='checksums.sha256')
(R/'checksums.sha256').write_text(''.join(hashlib.sha256(p.read_bytes()).hexdigest()+'  '+str(p.relative_to(R))+'\n' for p in files));files.append(R/'checksums.sha256')
for label,full in [('results',False),('full',True)]:
 target=R.parent/f'paper1_native_writeback_{label}.zip'
 with zipfile.ZipFile(target,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=3) as z:
  for p in files:
   if full or 'raw' not in p.relative_to(R).parts:z.write(p,str(p.relative_to(R.parent)))
 with zipfile.ZipFile(target) as z:assert z.testzip() is None
 print(target.name,round(target.stat().st_size/1024**2,2),'MiB; CRC verified',flush=True)
