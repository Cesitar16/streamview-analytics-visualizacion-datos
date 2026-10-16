"""Build the local EP2 data attachment without adding source CSVs to Git."""

from hashlib import sha256
from pathlib import Path
from zipfile import ZIP_DEFLATED, ZipFile
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts.export_powerbi import export  # noqa: E402


RAW = (
    "data/raw/netflix_movies_detailed_up_to_2025.csv",
    "data/raw/netflix_tv_shows_detailed_up_to_2025.csv",
)
DERIVED = tuple(f"powerbi/data/{name}.csv" for name in (
    "catalogo", "generos", "paises", "directores", "actores", "finanzas",
))
OUTPUT = ROOT / "output/entrega/StreamView_EP2_Datos.zip"


def package() -> tuple[Path, dict[str, str]]:
    missing = [name for name in RAW if not (ROOT / name).is_file()]
    if missing:
        raise FileNotFoundError(f"Faltan los CSV oficiales: {missing}")

    export()  # Derive the six Power BI tables from the same raw files.
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    digests = {}
    with ZipFile(OUTPUT, "w", compression=ZIP_DEFLATED, compresslevel=6) as archive:
        for name in (*RAW, *DERIVED):
            path = ROOT / name
            content = path.read_bytes()
            digests[name] = sha256(content).hexdigest()
            archive.writestr(name, content)
        manifest = "".join(f"{digest}  {name}\n" for name, digest in digests.items())
        archive.writestr("MANIFEST.sha256", manifest.encode("utf-8"))
        archive.writestr(
            "LEEME_DATOS.txt",
            (
                "StreamView Analytics EP2 - datos para el encargo academico\n"
                "Extraer el ZIP en la raiz del repositorio, conservando data/raw/ y powerbi/data/.\n"
                "Los dos CSV de data/raw/ son las fuentes originales sin modificar.\n"
                "Las seis tablas de powerbi/data/ se reconstruyen desde esas fuentes.\n"
                "Consultar docs/reproduccion_ep2.md para ejecutar y verificar los dashboards.\n"
                "No publicar este ZIP ni los CSV en el repositorio publico.\n"
            ).encode("utf-8"),
        )
    with ZipFile(OUTPUT) as archive:
        if archive.testzip() is not None:
            raise ValueError("El ZIP de datos no pasó la verificación CRC")
        for name, expected in digests.items():
            if sha256(archive.read(name)).hexdigest() != expected:
                raise ValueError(f"El archivo empaquetado no coincide: {name}")
    return OUTPUT, digests


if __name__ == "__main__":
    target, hashes = package()
    print(f"Paquete: {target}")
    print(f"Archivos de datos: {len(hashes)}")
    print(f"SHA-256 del ZIP: {sha256(target.read_bytes()).hexdigest()}")
