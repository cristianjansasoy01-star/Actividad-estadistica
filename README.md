# Simulador Unicauca Python Pro

Proyecto Python profesional para el simulador de Estadística Inferencial de la Universidad del Cauca.

## Características

- Clase principal `SimuladorUnicauca`.
- Motor TCL.
- Calculador de error de muestra y Error Estándar.
- Analista automático de Intervalos de Confianza.
- Selección automática entre Z, t y proporciones.
- Gráficas SVG generadas por Python.
- Interfaz visual local en navegador.
- Casos del PDF precargados.
- Sin dependencias externas.

## Cómo correrlo

En la carpeta del proyecto:

```powershell
python app.py
```

Si usas el Python de uv que vimos en tu computador:

```powershell
& "C:\Users\crist\AppData\Roaming\uv\python\cpython-3.14.4-windows-x86_64-none\python.exe" .\app.py
```

Luego abre:

```text
http://127.0.0.1:8000
```

## Estructura

```text
app.py
src/simulador_unicauca/
  core.py
  models.py
  distributions.py
  charts.py
  cases.py
  recommendations.py
  server.py
tests/
docs/
outputs/
```

## Para GitHub

Sube todo el proyecto al repositorio. Cada integrante puede clonarlo y ejecutar `python app.py`.
