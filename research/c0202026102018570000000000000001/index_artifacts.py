"""Hash the local trial artifacts and the frozen scientific inputs."""
import hashlib,json
from pathlib import Path
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[1]
excluded={'.plot-venv','__pycache__','search','search_cpu','test_search','qc_search','coset_search'}
paths=[p for p in HERE.rglob('*') if p.is_file() and not any(part in excluded for part in p.relative_to(HERE).parts)
       and p.name!='artifact-index.json']
paths += [ROOT/'data/targets.json',ROOT/'results/closure.json',ROOT/'discover/catalog.json',ROOT/'discover/frontier.json']
paths += [ROOT/t['object'] for t in json.loads((ROOT/'data/targets.json').read_text())]
rows=[dict(path=str(p.relative_to(ROOT)),bytes=p.stat().st_size,sha256=hashlib.sha256(p.read_bytes()).hexdigest()) for p in sorted(paths)]
(HERE/'artifact-index.json').write_text(json.dumps(dict(schema='local-artifact-index-v1',
    note='Self-excluding index. Optional plotting environment and compiled binaries are excluded; C++ source and build script are included.',
    files=rows,total_bytes=sum(r['bytes'] for r in rows)),indent=2)+'\n')
print(len(rows),'hashed files;',sum(r['bytes'] for r in rows),'bytes')
