import argparse,json,secrets,hashlib,subprocess
from pathlib import Path
p=argparse.ArgumentParser();p.add_argument('--seed');a=p.parse_args();seed=a.seed or secrets.token_hex(16)
if len(seed)!=32 or any(c not in '0123456789abcdefABCDEF' for c in seed):raise SystemExit('seed must be 32 hex digits')
c=json.loads(Path('discover/catalog.json').read_text())
def draw(label):return int(hashlib.sha256(json.dumps([seed,label],separators=(',',':')).encode()).hexdigest(),16)
r=draw('track')%100
for track in c['tracks']:
    r-=track['weight']
    if r<0:break
task=track['tasks'][draw('card:0')%len(track['tasks'])]
print(json.dumps(dict(seed=seed,track=track['id'],task=task,notice='LOCAL proposal only; no reservation or public posting'),indent=2))
