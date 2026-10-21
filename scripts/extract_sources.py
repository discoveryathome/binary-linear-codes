"""One-time extraction of the facts the checks use from third-party pages.

The code-table pages (codetables.de, Markus Grassl) and the Yu et al. arXiv HTML carry no open
license, so the repository keeps only the facts read from them: per-cell bound values, recipe
steps and displayed parameter triples, each with source URL, retrieval date, page SHA-256 and
credit. The pages themselves are cited in data/source-index.json ("stored": false).

To refresh, fetch the pages listed in data/source-index.json to their recorded paths (the
SHA-256 must match, or record a new snapshot deliberately) and run this from the repository root.
It reuses the parsers in closure.py and reconstruct.py, so checks see the same values.
"""
import json,hashlib,re
from pathlib import Path
import closure,reconstruct

OUT=Path('data/extracted')
GRASSL='Markus Grassl, "Bounds on the minimum distance of linear codes and quantum codes", online tables at https://www.codetables.de. The original authors of each construction are credited on its codetables.de page (URL in each record).'
YU='Cong Yu, Shixin Zhu, Hao Chen, Yang Li and Xiuyu Zhang, "New record-breaking binary linear codes constructed from group codes", arXiv:2412.15551v1 (2024).'

def source(entry):
    data=Path(entry['path']).read_bytes()
    if hashlib.sha256(data).hexdigest()!=entry['sha256']:raise ValueError('page hash differs from source index: '+entry['path'])
    return dict(path=entry['path'],url=entry['url'],retrieved_on=entry['retrieved_on'],sha256=entry['sha256'])

def dump(path,obj,rows_key):
    """JSON with one list item per line, for readable diffs."""
    head={k:v for k,v in obj.items() if k!=rows_key}
    text=json.dumps(head,indent=2)[:-2]+f',\n  "{rows_key}": [\n'
    text+=',\n'.join('    '+json.dumps(r,separators=(',',':')) for r in obj[rows_key])+'\n  ]\n}\n'
    assert json.loads(text)==obj
    path.write_text(text)

def run():
    index={e['path']:e for e in json.loads(Path('data/source-index.json').read_text())}
    OUT.mkdir(exist_ok=True)
    src=source(index['data/sources/table2.html'])
    t=closure.parse_table(Path(src['path']).read_text())
    if len(t)!=32896:raise ValueError('incomplete table snapshot')
    dump(OUT/'codetables-bounds.json',dict(description='Binary linear code bounds [n, k, lower, upper] for n,k=1..256, as displayed in the full GF(2) table.',
        credit=GRASSL,source=src,columns=['n','k','lower','upper'],bounds=[[n,k,a,b] for (n,k),(a,b) in sorted(t.items())]),'bounds')
    src=source(index['data/sources/yu2024.html'])
    dump(OUT/'yu2024-triples.json',dict(description='Every [n,k,d] triple displayed in the paper (new codes and comparison codes); used as conservative, not locally certified, closure seeds.',
        credit=YU,source=src,triples=[list(x) for x in closure.parse_triples(Path(src['path']).read_text())]),'triples')
    recipes={}
    for path,entry in index.items():
        m=re.fullmatch(r'data/sources/(\d+)_(\d+)\.html',path)
        if not m:continue
        recipes[f'{m[1]}_{m[2]}']=dict(source=source(entry),credit='codetables.de (Markus Grassl), construction of ['+m[1]+','+m[2]+']',steps=reconstruct.page_steps(path))
    recipes=dict(sorted(recipes.items(),key=lambda x:tuple(map(int,x[0].split('_')))))
    reconstruct.EXTRACTED.write_text(json.dumps(dict(description='Construction steps (index, parameters, recipe line) from codetables.de per-cell pages, keyed n_k.',
        credit=GRASSL,recipes=recipes),indent=1)+'\n')
    print(json.dumps(dict(bounds=len(t),recipes=len(recipes))))
if __name__=='__main__':run()
