"""Configuración de la app: ubicación de la fuente de datos.

La carpeta de datos se resuelve desde la variable de entorno ``ROKA_DATA_DIR``; si no
está definida, se usa la ruta por defecto (Dropbox local). De este modo se puede apuntar
la app a otra fuente de parquet (otro equipo, otra copia, un volumen montado) SIN tocar
código:

    PowerShell:  $env:ROKA_DATA_DIR = "D:/otra/ruta/data"
    bash:        export ROKA_DATA_DIR=/mnt/datos/data
"""
from __future__ import annotations
import os
from pathlib import Path

# Ruta por defecto a los .parquet (puede sobreescribirse con ROKA_DATA_DIR).
_DEFAULT_DATA_DIR = "C:/Users/LUIS VP.DESKTOP-BV9G17I/Dropbox/data/"

DATA_DIR: Path = Path(os.environ.get("ROKA_DATA_DIR", _DEFAULT_DATA_DIR))
