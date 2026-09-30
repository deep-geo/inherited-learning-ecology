from pathlib import Path
import zipfile,json,hashlib
R=Path(__file__).resolve().parents[1]
with zipfile.ZipFile(R/'raw_results.zip','w',compression=zipfile.ZIP_DEFLATED,compresslevel=1) as z:
 for p in sorted((R/'raw').glob('*')):z.write(p,p.relative_to(R))
with zipfile.ZipFile(R/'analysis_bundle.zip','w',compression=zipfile.ZIP_DEFLATED,compresslevel=6) as z:
 for p in sorted(R.rglob('*')):
  if p.is_file() and p.suffix!='.zip' and 'raw' not in p.relative_to(R).parts and 'development' not in p.relative_to(R).parts and p.name!='sim':z.write(p,p.relative_to(R))
print('PACKAGED',flush=True)
