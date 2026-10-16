"""Point the existing PBIP model at this checkout's six exported CSV files.

Close Power BI Desktop before running this script against the real project.
Only the File.Contents paths change; measures and report visuals are preserved.
"""

import argparse
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
TABLES = ("catalogo", "generos", "paises", "directores", "actores", "finanzas")
SOURCE = re.compile(r'File\.Contents\("([^"]*)"\)')


def rebase(project_root: Path, data_root: Path) -> int:
    table_dir = project_root / "StreamView_EP2.SemanticModel/definition/tables"
    replacements = []
    for name in TABLES:
        source_file = (data_root / f"{name}.csv").resolve()
        model_file = table_dir / f"{name}.tmdl"
        if not source_file.is_file() or not model_file.is_file():
            raise FileNotFoundError(source_file if not source_file.is_file() else model_file)
        old = model_file.read_text(encoding="utf-8")
        matches = SOURCE.findall(old)
        if len(matches) != 1 or Path(matches[0].replace('""', '"')).name.lower() != source_file.name.lower():
            raise ValueError(f"Origen inesperado en {model_file}: {matches}")
        new_path = str(source_file).replace('"', '""')
        new = SOURCE.sub(lambda _: f'File.Contents("{new_path}")', old, count=1)
        replacements.append((model_file, old, new))
    for model_file, old, new in replacements:
        if new != old:
            model_file.write_text(new, encoding="utf-8")
    return sum(new != old for _, old, new in replacements)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--project-root", type=Path, default=ROOT / "powerbi")
    parser.add_argument("--data-root", type=Path, default=ROOT / "powerbi/data")
    args = parser.parse_args()
    print(f"Rutas de Power BI actualizadas: {rebase(args.project_root, args.data_root)}")
