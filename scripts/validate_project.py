from __future__ import annotations

import json
import py_compile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

REQUIRED_FILES = [
    "app/app.py",
    "app/engine.py",
    "app/i18n.py",
    "requirements.txt",
    "INICIAR_AGENT.bat",
    "build_installer.iss",
    "README.md",
    "CHANGELOG.md",
    "VERSIO.txt",
    "SECURITY.md",
    "docs/PROTOCOL_TDR.md",
    "docs/DATA_SOURCE_ECB.md",
    "docs/MANUAL_USUARI.md",
    "docs/USER_MANUAL_EN.md",
    "data/plantilla_inversors_humans.csv",
]

FORBIDDEN_LEGACY_FILES = [
    "setup.ps1",
    "INSTAL_LAR_AGENT.bat",
    "DESINSTAL_LAR_AGENT.bat",
]

LOCALES = {
    "ca": ROOT / "app/locales/ca.json",
    "es": ROOT / "app/locales/es.json",
    "en": ROOT / "app/locales/en.json",
    "eu": ROOT / "app/locales/eu.json",
    "gl": ROOT / "app/locales/gl.json",
}


def fail(message: str) -> None:
    raise SystemExit(f"ERROR: {message}")


def main() -> None:
    missing = [path for path in REQUIRED_FILES if not (ROOT / path).exists()]
    if missing:
        fail("Falten fitxers obligatoris: " + ", ".join(missing))

    legacy = [path for path in FORBIDDEN_LEGACY_FILES if (ROOT / path).exists()]
    if legacy:
        fail("Encara hi ha fitxers del bootstrap antic: " + ", ".join(legacy))
    print("OK: el bootstrap PowerShell antic no forma part del projecte.")

    for path in ["app/app.py", "app/engine.py", "app/i18n.py"]:
        py_compile.compile(str(ROOT / path), doraise=True)
    print("OK: els mòduls Python compilen.")

    locale_data: dict[str, dict[str, str]] = {}
    for code, path in LOCALES.items():
        with path.open("r", encoding="utf-8") as fh:
            data = json.load(fh)
        if not isinstance(data, dict):
            fail(f"{path} no conté un objecte JSON.")
        locale_data[code] = data

    reference = set(locale_data["ca"])
    for code, data in locale_data.items():
        keys = set(data)
        missing_keys = sorted(reference - keys)
        extra_keys = sorted(keys - reference)
        if missing_keys or extra_keys:
            fail(f"Idioma {code}: claus absents={missing_keys}; claus sobreres={extra_keys}")

    print(f"OK: {len(LOCALES)} idiomes sincronitzats amb {len(reference)} claus cadascun.")

    requirements = (ROOT / "requirements.txt").read_text(encoding="utf-8").lower()
    for package in ["streamlit", "pandas", "numpy", "plotly"]:
        if package not in requirements:
            fail(f"requirements.txt no inclou {package}.")
    if "ccxt" in requirements:
        fail("La variant FX no ha de dependre de CCXT.")
    print("OK: dependències FX principals presents i CCXT absent.")

    engine = (ROOT / "app/engine.py").read_text(encoding="utf-8")
    if "ecb.europa.eu/stats/eurofxref/eurofxref-hist.csv" not in engine:
        fail("El motor FX no apunta a la sèrie històrica oficial del BCE.")
    if "list_fx_markets" not in engine or "available_reference_currencies" not in engine:
        fail("Falten funcions bàsiques del motor FX.")
    print("OK: motor configurat per als tipus de canvi de referència del BCE.")

    launcher = (ROOT / "INICIAR_AGENT.bat").read_text(encoding="utf-8").lower()
    forbidden = ["powershell", "executionpolicy", "invoke-webrequest", "curl ", "bitsadmin"]
    found = [term for term in forbidden if term in launcher]
    if found:
        fail("El launcher conté patrons no admesos per a la distribució segura: " + ", ".join(found))
    print("OK: el launcher no descarrega ni executa PowerShell.")

    print("VALIDACIÓ FX COMPLETADA CORRECTAMENT")


if __name__ == "__main__":
    main()
