import importlib.util
spec = importlib.util.spec_from_file_location("gen", r"d:\software\cld_project\blog\scripts\gen_86_94_final.py")
gen = importlib.util.module_from_spec(spec)
spec.loader.exec_module(gen)
from pathlib import Path
Path(gen.ROOT / "86.hnsw-index-tutorial.md").write_text(gen.A86, encoding="utf-8")
print("hanzi", gen.hz(gen.A86))
