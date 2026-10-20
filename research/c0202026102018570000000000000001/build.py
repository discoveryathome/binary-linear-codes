"""Build bounded one-thread search tools. Requires a C++17 compiler."""
import os,subprocess
from pathlib import Path
HERE=Path(__file__).resolve().parent
source=(HERE/'search.cpp').read_text()
needle='wall<=0||seconds()<wall'
assert source.count(needle)==1
(HERE/'search_cpu.cpp').write_text(source.replace(needle,'wall<=0||double(clock()-c0)/CLOCKS_PER_SEC<wall')
    .replace('WALL_SECONDS ITERATIONS','CPU_SECONDS ITERATIONS'))
for name in ['search','search_cpu','test_search','qc_search','coset_search']:
    subprocess.run([os.environ.get('CXX','c++'),'-O3','-std=c++17',str(HERE/f'{name}.cpp'),'-o',str(HERE/name)],check=True)
subprocess.run([str(HERE/'test_search')],check=True)
