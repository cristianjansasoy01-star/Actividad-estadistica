#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Entrada principal del Simulador Unicauca Python Pro."""

from __future__ import annotations

import sys
import threading
import time
import webbrowser
from pathlib import Path

ROOT = Path(__file__).resolve().parent
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from simulador_unicauca.server import run_server


def main() -> None:
    host = "127.0.0.1"
    port = 8000
    url = f"http://{host}:{port}"

    def abrir_navegador() -> None:
        time.sleep(0.8)
        webbrowser.open(url)

    threading.Thread(target=abrir_navegador, daemon=True).start()

    print("=" * 80)
    print("SIMULADOR UNICAUCA PYTHON PRO")
    print("=" * 80)
    print(f"Aplicación disponible en: {url}")
    print("Si no se abre automáticamente, copia esa URL en Chrome o Edge.")
    print("Presiona Ctrl+C para detener el servidor.")
    print("=" * 80)

    try:
        run_server(host=host, port=port)
    except KeyboardInterrupt:
        print("\nServidor detenido correctamente.")


if __name__ == "__main__":
    main()
