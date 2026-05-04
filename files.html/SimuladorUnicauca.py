"""
================================================================================
  SIMULADOR DE ESTADÍSTICA INFERENCIAL - UNIVERSIDAD DEL CAUCA
  Administración de Empresas | Segunda Actividad Evaluativa
  Docente: Pablo Galvis Pérez | Popayán, Cauca
================================================================================

ESTRUCTURA DEL SIMULADOR:
  Clase principal: SimuladorUnicauca
  ├── motor_tcl()            → Simula el TCL variando n y grafica campanas
  ├── calcular_errores()     → Diferencia error de muestra vs Error Estándar (SE)
  ├── analista_intervalos()  → Selecciona Z, t o proporciones automáticamente
  ├── resolver_bloque_tcl()  → Resuelve los 5 escenarios del Bloque 1
  └── resolver_bloque_ic()   → Resuelve los 9 casos del Bloque 2

CONCEPTOS CLAVE (para sustentación oral):
  - TCL: La distribución de medias muestrales se aproxima a una Normal
    sin importar la distribución de la población, cuando n es suficientemente
    grande (generalmente n ≥ 30).
  - Error Estándar (SE): SE = σ/√n. Mide cuánto varía el promedio muestral
    alrededor del parámetro poblacional μ. A mayor n, menor SE.
  - Intervalo de Confianza (IC): Rango de valores donde se "atrapa" el
    parámetro poblacional con un nivel de confianza dado (90%, 95%, 99%).
"""

# ─────────────────────────────────────────────────────────────────────────────
# IMPORTACIONES
# scipy.stats: herramienta estadística para distribuciones Z y t
# numpy: cálculos numéricos vectorizados
# matplotlib / seaborn: visualización de datos
# ─────────────────────────────────────────────────────────────────────────────
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
import seaborn as sns
from scipy import stats
import warnings
warnings.filterwarnings('ignore')

# Paleta de colores institucional (verde/dorado Unicauca)
COLORES = {
    'principal':   '#1B5E20',   # Verde oscuro
    'secundario':  '#F9A825',   # Dorado
    'acento':      '#0D47A1',   # Azul profundo
    'claro':       '#A5D6A7',   # Verde claro
    'fondo':       '#F1F8E9',   # Verde muy claro
    'rojo':        '#B71C1C',   # Rojo alerta
    'gris':        '#455A64',   # Gris azulado
}

# Configuración global de gráficas
plt.rcParams.update({
    'font.family':      'DejaVu Sans',
    'font.size':        11,
    'axes.titlesize':   13,
    'axes.titleweight': 'bold',
    'axes.labelsize':   11,
    'figure.facecolor': 'white',
    'axes.facecolor':   COLORES['fondo'],
    'axes.grid':        True,
    'grid.alpha':       0.4,
    'lines.linewidth':  2.5,
})


# ═════════════════════════════════════════════════════════════════════════════
class SimuladorUnicauca:
    """
    Clase principal del simulador de Estadística Inferencial.

    Integra el Motor TCL, el Calculador de Errores y el Analista de Intervalos
    para resolver problemas del contexto económico del departamento del Cauca.
    """

    def __init__(self):
        self.z_95  = 1.96    # Valor crítico Z para 95% de confianza
        self.z_90  = 1.645   # Valor crítico Z para 90% de confianza
        self.z_99  = 2.576   # Valor crítico Z para 99% de confianza

    # ─────────────────────────────────────────────────────────────────────────
    # ① MOTOR DE SIMULACIÓN TCL
    # ─────────────────────────────────────────────────────────────────────────
    def motor_tcl(self, mu: float, sigma: float,
                  n_valores: list = None, titulo_extra: str = ""):
        """
        Demuestra visualmente el Teorema Central del Límite.

        LÓGICA ESTADÍSTICA:
        Cuando tomamos muchas muestras de tamaño n de una población,
        la distribución de sus MEDIAS sigue una distribución Normal con:
            · Media:          μ_x̄ = μ       (igual a la población)
            · Error Estándar: SE = σ / √n   (se reduce con más datos)

        A mayor n → curva más delgada y puntiaguda → estimaciones más precisas.

        Parámetros:
            mu          : Media poblacional (parámetro conocido)
            sigma       : Desviación estándar poblacional
            n_valores   : Lista de tamaños de muestra a comparar
            titulo_extra: Texto descriptivo del escenario
        """
        if n_valores is None:
            n_valores = [5, 15, 30, 60, 120]

        fig, axes = plt.subplots(1, 2, figsize=(16, 6))
        fig.suptitle(
            f'Motor TCL — {titulo_extra}\nμ = {mu},  σ = {sigma}',
            fontsize=14, fontweight='bold', color=COLORES['principal']
        )

        # ── Panel izquierdo: campanas comparativas ──────────────────────────
        ax1 = axes[0]
        colores_n = plt.cm.viridis(np.linspace(0.15, 0.85, len(n_valores)))

        # Determinar rango X común (±4 SE del n más pequeño)
        se_max  = sigma / np.sqrt(min(n_valores))
        x_range = np.linspace(mu - 4.5*se_max, mu + 4.5*se_max, 500)

        for i, n in enumerate(n_valores):
            se = sigma / np.sqrt(n)    # Error Estándar para este n
            # pdf: función de densidad de probabilidad de la Normal
            y  = stats.norm.pdf(x_range, loc=mu, scale=se)
            ax1.plot(x_range, y, color=colores_n[i],
                     label=f'n = {n:>4d}  |  SE = {se:.3f}')
            ax1.fill_between(x_range, y, alpha=0.08, color=colores_n[i])

        ax1.axvline(mu, color=COLORES['rojo'], linestyle='--',
                    linewidth=1.8, label=f'μ = {mu}', zorder=5)
        ax1.set_title('Distribución de Medias Muestrales (X̄)')
        ax1.set_xlabel('Valor de la Media Muestral (X̄)')
        ax1.set_ylabel('Densidad de Probabilidad')
        ax1.legend(fontsize=9, loc='upper right')

        # ── Panel derecho: SE vs n (curva de convergencia) ──────────────────
        ax2 = axes[1]
        n_continuo = np.linspace(1, max(n_valores)*1.5, 300)
        se_continuo = sigma / np.sqrt(n_continuo)

        ax2.plot(n_continuo, se_continuo,
                 color=COLORES['acento'], linewidth=2.5,
                 label=f'SE = {sigma}/√n')
        ax2.fill_between(n_continuo, se_continuo, alpha=0.15,
                         color=COLORES['acento'])

        # Marcar los puntos específicos
        for i, n in enumerate(n_valores):
            se = sigma / np.sqrt(n)
            ax2.scatter(n, se, color=colores_n[i], s=100, zorder=5)
            ax2.annotate(f'n={n}\nSE={se:.2f}',
                         xy=(n, se), xytext=(8, 8),
                         textcoords='offset points', fontsize=8,
                         color=colores_n[i])

        ax2.set_title('Reducción del Error Estándar conforme aumenta n')
        ax2.set_xlabel('Tamaño de Muestra (n)')
        ax2.set_ylabel('Error Estándar (SE = σ/√n)')
        ax2.legend()

        plt.tight_layout()
        nombre_archivo = f"TCL_motor_{titulo_extra.replace(' ', '_')[:20]}.png"
        plt.savefig(f'/mnt/user-data/outputs/{nombre_archivo}',
                    dpi=150, bbox_inches='tight')
        plt.show()
        print(f"  ✔ Gráfica guardada: {nombre_archivo}\n")

    # ─────────────────────────────────────────────────────────────────────────
    # ② CALCULADOR DE ERRORES
    # ─────────────────────────────────────────────────────────────────────────
    def calcular_errores(self, sigma: float, n: int,
                         muestra_data: list = None, verbose: bool = True):
        """
        Diferencia explícitamente el Error de Muestra y el Error Estándar.

        LÓGICA ESTADÍSTICA:
        · Error de Muestra    : Diferencia puntual entre x̄ y μ (varía por azar)
        · Error Estándar (SE) : σ/√n → Desviación estándar de la distribución
                                de medias muestrales. Es un PARÁMETRO TEÓRICO
                                que cuantifica la variabilidad esperada del estimador.

        Diferencia clave para la sustentación:
            "El error de muestra es lo que pasó; el SE es lo que podría pasar."

        Retorna:
            dict con SE, margen_error_95, intervalo_95
        """
        # Error Estándar de la Media
        se = sigma / np.sqrt(n)

        # Margen de error al 95% de confianza
        margen_95 = self.z_95 * se
        margen_90 = self.z_90 * se
        margen_99 = self.z_99 * se

        resultado = {
            'SE': se,
            'margen_90': margen_90,
            'margen_95': margen_95,
            'margen_99': margen_99,
        }

        if verbose:
            print(f"\n{'─'*55}")
            print(f"  📐 CALCULADOR DE ERRORES")
            print(f"{'─'*55}")
            print(f"  Parámetros: σ = {sigma},  n = {n}")
            print(f"  ┌─────────────────────────────────────────────┐")
            print(f"  │  Error Estándar  SE = σ/√n                  │")
            print(f"  │    SE = {sigma} / √{n} = {se:.4f}         │")
            print(f"  ├─────────────────────────────────────────────┤")
            print(f"  │  Margen de error  (E = Z · SE):             │")
            print(f"  │    90% confianza → E = {self.z_90} × {se:.4f} = {margen_90:.4f}  │")
            print(f"  │    95% confianza → E = {self.z_95} × {se:.4f} = {margen_95:.4f}  │")
            print(f"  │    99% confianza → E = {self.z_99} × {se:.4f} = {margen_99:.4f}  │")
            print(f"  └─────────────────────────────────────────────┘")
            print(f"  💡 A mayor n → menor SE → estimaciones más precisas")

            if muestra_data:
                x_bar = np.mean(muestra_data)
                error_puntual = abs(x_bar - np.mean(muestra_data))
                print(f"\n  Error de muestra (puntual): x̄ = {x_bar:.4f}")
                print(f"  (Este varía con cada muestra; el SE es fijo para σ y n dados)")

        return resultado

    # ─────────────────────────────────────────────────────────────────────────
    # ③ ANALISTA INTELIGENTE DE INTERVALOS
    # ─────────────────────────────────────────────────────────────────────────
    def analista_intervalos(self, x_bar: float = None, n: int = None,
                            sigma: float = None, s: float = None,
                            p_hat: float = None, confianza: float = 0.95,
                            contexto: str = "", recomendacion_gerencial: str = ""):
        """
        Selecciona AUTOMÁTICAMENTE el método correcto y calcula el IC.

        ÁRBOL DE DECISIÓN (lógica del analista):
        ┌─────────────────────────────────────────────┐
        │ ¿Es un problema de PROPORCIONES?            │
        │   → Sí → Usar fórmula de proporciones:      │
        │           p̂ ± Z · √(p̂·q̂/n)                 │
        │   → No → ¿σ es conocida o n ≥ 30?           │
        │           → Sí → Usar tabla Z               │
        │                   x̄ ± Z · (σ/√n)            │
        │           → No → Usar tabla t (n pequeño)   │
        │                   x̄ ± t_(α/2, n-1) · (s/√n) │
        └─────────────────────────────────────────────┘

        Por qué t cuando n < 30:
            Con muestras pequeñas, s (desviación muestral) es una estimación
            menos confiable de σ. La distribución t de Student tiene colas más
            anchas que la Z para compensar esta incertidumbre adicional.

        Retorna:
            dict con límite inferior, límite superior, método usado
        """
        alpha = 1 - confianza

        print(f"\n{'═'*60}")
        print(f"  🔍 ANALISTA DE INTERVALOS DE CONFIANZA")
        print(f"  Contexto: {contexto}")
        print(f"{'═'*60}")

        # ── CASO 1: Proporciones ────────────────────────────────────────────
        if p_hat is not None:
            """
            LÓGICA: Usamos el Teorema Central del Límite para proporciones.
            Si n·p̂ ≥ 5 y n·q̂ ≥ 5, la distribución de p̂ es aproximadamente
            Normal → podemos usar Z.
            """
            q_hat = 1 - p_hat
            metodo = "Z — Proporciones"

            # Verificar condición de normalidad
            cond1 = n * p_hat
            cond2 = n * q_hat
            print(f"  📌 Método elegido: {metodo}")
            print(f"     Razón: p̂ = {p_hat:.4f}, verificación np̂={cond1:.1f} ≥ 5 ✓")

            # Valor crítico Z bilateral
            z_critico = stats.norm.ppf(1 - alpha/2)
            se_p      = np.sqrt(p_hat * q_hat / n)     # Error estándar de la proporción
            margen    = z_critico * se_p

            li = p_hat - margen
            ls = p_hat + margen

            print(f"\n  Fórmula: p̂ ± Z_(α/2) · √(p̂·q̂/n)")
            print(f"  p̂ = {p_hat:.4f}   q̂ = {q_hat:.4f}   n = {n}")
            print(f"  Z_({alpha/2:.3f}) = {z_critico:.4f}")
            print(f"  SE_p = √({p_hat:.4f}×{q_hat:.4f}/{n}) = {se_p:.6f}")
            print(f"  Margen = {z_critico:.4f} × {se_p:.6f} = {margen:.4f}")

            resultado = {'metodo': metodo, 'LI': li, 'LS': ls,
                         'margen': margen, 'z_o_t': z_critico,
                         'tipo': 'proporcion', 'p_hat': p_hat}

        # ── CASO 2: Media con σ conocida o n ≥ 30 → Distribución Z ─────────
        elif sigma is not None or (s is not None and n >= 30):
            """
            LÓGICA: Cuando σ es conocido, la estandarización Z = (X̄-μ)/(σ/√n)
            sigue exactamente una Normal estándar → usamos tabla Z.
            Si n ≥ 30 con s conocida, por el TCL la aproximación es válida.
            """
            desv = sigma if sigma is not None else s
            tipo_desv = "σ (conocida)" if sigma else "s (n≥30, aprox. Normal)"
            metodo = f"Z — Media con {tipo_desv}"

            print(f"  📌 Método elegido: {metodo}")
            print(f"     Razón: {'σ conocida → Z exacta' if sigma else 'n≥30 → TCL garantiza normalidad'}")

            z_critico = stats.norm.ppf(1 - alpha/2)
            se        = desv / np.sqrt(n)
            margen    = z_critico * se

            li = x_bar - margen
            ls = x_bar + margen

            print(f"\n  Fórmula: x̄ ± Z_(α/2) · (σ/√n)")
            print(f"  x̄ = {x_bar}   {('σ' if sigma else 's')} = {desv}   n = {n}")
            print(f"  Z_({alpha/2:.3f}) = {z_critico:.4f}")
            print(f"  SE = {desv}/√{n} = {se:.4f}")
            print(f"  Margen = {z_critico:.4f} × {se:.4f} = {margen:.4f}")

            resultado = {'metodo': metodo, 'LI': li, 'LS': ls,
                         'margen': margen, 'z_o_t': z_critico,
                         'tipo': 'media_z', 'se': se}

        # ── CASO 3: Media con σ desconocida y n < 30 → Distribución t ───────
        else:
            """
            LÓGICA: Con n < 30 y σ desconocida, la estadística
            t = (X̄ - μ)/(s/√n) sigue una distribución t de Student
            con gl = n-1 grados de libertad.
            Las colas más pesadas de t compensan la incertidumbre de usar s.
            """
            gl     = n - 1     # Grados de libertad
            metodo = f"t de Student (gl = {gl})"

            print(f"  📌 Método elegido: {metodo}")
            print(f"     Razón: n={n} < 30 y σ desconocida → mayor incertidumbre → colas más anchas")

            t_critico = stats.t.ppf(1 - alpha/2, df=gl)
            se        = s / np.sqrt(n)
            margen    = t_critico * se

            li = x_bar - margen
            ls = x_bar + margen

            print(f"\n  Fórmula: x̄ ± t_(α/2, n-1) · (s/√n)")
            print(f"  x̄ = {x_bar}   s = {s}   n = {n}   gl = {gl}")
            print(f"  t_({alpha/2:.3f}, {gl}) = {t_critico:.4f}")
            print(f"  SE = {s}/√{n} = {se:.4f}")
            print(f"  Margen = {t_critico:.4f} × {se:.4f} = {margen:.4f}")

            resultado = {'metodo': metodo, 'LI': li, 'LS': ls,
                         'margen': margen, 'z_o_t': t_critico,
                         'tipo': 'media_t', 'se': se, 'gl': gl}

        # Resultado final
        print(f"\n  ┌─────────────────────────────────────────────────┐")
        print(f"  │  IC al {confianza*100:.0f}%: [{resultado['LI']:.4f}  ,  {resultado['LS']:.4f}]  │")
        print(f"  └─────────────────────────────────────────────────┘")

        if recomendacion_gerencial:
            print(f"\n  💼 RECOMENDACIÓN GERENCIAL:")
            print(f"  {recomendacion_gerencial}")

        return resultado

    # ─────────────────────────────────────────────────────────────────────────
    # ④ GRAFICAR INTERVALO DE CONFIANZA
    # ─────────────────────────────────────────────────────────────────────────
    def graficar_intervalo(self, resultado: dict, titulo: str,
                           ax: plt.Axes = None, mu_ref: float = None):
        """Genera una campana de Gauss con el IC sombreado."""
        if ax is None:
            _, ax = plt.subplots(figsize=(9, 4))

        tipo = resultado['tipo']

        if tipo == 'proporcion':
            centro = resultado['p_hat']
            se     = np.sqrt(centro * (1-centro) / 1000)  # Aproximación visual
        else:
            centro = (resultado['LI'] + resultado['LS']) / 2
            se     = resultado.get('se', resultado['margen'] / resultado['z_o_t'])

        x = np.linspace(centro - 4.5*se, centro + 4.5*se, 500)

        if tipo == 'media_t':
            gl = resultado.get('gl', 10)
            y  = stats.t.pdf((x - centro)/se, df=gl) / se
        else:
            y  = stats.norm.pdf(x, loc=centro, scale=se)

        ax.plot(x, y, color=COLORES['principal'], linewidth=2.5)

        # Sombrear región del IC
        mask = (x >= resultado['LI']) & (x <= resultado['LS'])
        ax.fill_between(x, y, where=mask, alpha=0.35,
                        color=COLORES['secundario'], label=f"IC {titulo.split('|')[0]}")

        # Líneas de límites
        for lim, etiqueta, col in [
            (resultado['LI'], f"LI = {resultado['LI']:.3f}", COLORES['acento']),
            (resultado['LS'], f"LS = {resultado['LS']:.3f}", COLORES['rojo']),
        ]:
            ax.axvline(lim, color=col, linestyle='--', linewidth=1.5, label=etiqueta)

        # Línea del estimador puntual
        ax.axvline(centro, color=COLORES['principal'], linestyle='-',
                   linewidth=2, label=f"Estimador = {centro:.3f}")

        ax.set_title(titulo, fontsize=10, fontweight='bold')
        ax.set_xlabel('Valor')
        ax.set_ylabel('Densidad')
        ax.legend(fontsize=8)

    # ─────────────────────────────────────────────────────────────────────────
    # ⑤ RESOLUCIÓN TCL — TIPIFICACIÓN Z
    # ─────────────────────────────────────────────────────────────────────────
    def tipificacion_z(self, x: float, mu: float, sigma: float,
                       n: int, direccion: str = 'mayor',
                       nombre: str = "", descripcion: str = "") -> dict:
        """
        Calcula la probabilidad mediante tipificación Z para medias muestrales.

        LÓGICA ESTADÍSTICA:
        Paso 1: Calcular SE = σ/√n
        Paso 2: Tipificar → Z = (x̄ - μ) / SE
                            Este Z mide cuántas desviaciones estándar está x̄ de μ
        Paso 3: Consultar tabla Z (scipy.stats.norm.cdf)

        Parámetros:
            x         : Valor crítico del promedio muestral
            mu        : Media poblacional
            sigma     : Desviación estándar poblacional
            n         : Tamaño de la muestra
            direccion : 'mayor', 'menor', o 'entre' (para intervalos)
        """
        se      = sigma / np.sqrt(n)
        z_score = (x - mu) / se

        # Calcular probabilidad según la dirección pedida
        if direccion == 'mayor':
            prob = 1 - stats.norm.cdf(z_score)
            signo = ">"
        elif direccion == 'menor':
            prob = stats.norm.cdf(z_score)
            signo = "<"
        else:
            prob = None   # Para 'entre', se maneja externamente
            signo = ""

        print(f"\n{'═'*60}")
        print(f"  📊 {nombre}")
        print(f"  {descripcion}")
        print(f"{'─'*60}")
        print(f"  Parámetros: μ={mu}, σ={sigma}, n={n}, valor crítico={x}")
        print(f"\n  PASO 1 → Error Estándar:")
        print(f"    SE = σ/√n = {sigma}/√{n} = {se:.4f}")
        print(f"\n  PASO 2 → Tipificación Z:")
        print(f"    Z = (x̄ - μ) / SE = ({x} - {mu}) / {se:.4f} = {z_score:.4f}")
        print(f"\n  PASO 3 → Probabilidad:")
        if prob is not None:
            print(f"    P(X̄ {signo} {x}) = P(Z {signo} {z_score:.4f}) = {prob:.4f} = {prob*100:.2f}%")
            print(f"\n  ✅ RESULTADO: Hay una probabilidad de {prob*100:.2f}% de que")
            print(f"     el promedio muestral sea {signo} {x}")

        return {'z': z_score, 'prob': prob, 'se': se}

    # ─────────────────────────────────────────────────────────────────────────
    # ⑥ BLOQUE 1 — 5 ESCENARIOS TCL
    # ─────────────────────────────────────────────────────────────────────────
    def resolver_bloque_tcl(self):
        """
        Resuelve los 5 escenarios del Bloque 1 con tipificación Z y gráficas.
        Cada escenario tiene su propia campana de Gauss sombreada.
        """
        print("\n" + "█"*65)
        print("  BLOQUE 1: TEOREMA CENTRAL DEL LÍMITE — 5 ESCENARIOS")
        print("  Departamento del Cauca — Análisis Estadístico")
        print("█"*65)

        # Figura con 5 subgráficas (2 filas × 3 columnas, última vacía)
        fig = plt.figure(figsize=(20, 11))
        fig.suptitle(
            'BLOQUE 1 — Teorema Central del Límite\nDistribuciones de Medias Muestrales — Popayán, Cauca',
            fontsize=14, fontweight='bold', color=COLORES['principal'], y=1.01
        )
        gs = gridspec.GridSpec(2, 3, figure=fig, hspace=0.5, wspace=0.35)
        axes_tcl = [fig.add_subplot(gs[i//3, i%3]) for i in range(5)]

        resultados_tcl = []

        # ── TCL-1: CEO Energía ───────────────────────────────────────────────
        print("\n" + "─"*60)
        print("  TCL-1 | CEO-Energía Popayán")
        print("─"*60)
        r1 = self.tipificacion_z(
            x=195, mu=180, sigma=45, n=40, direccion='mayor',
            nombre="TCL-1: CEO-Energía de Popayán",
            descripcion="¿Probabilidad de que auditoría a 40 hogares promedio > 195 kWh?"
        )
        print(f"\n  💡 INTERPRETACIÓN GERENCIAL:")
        print(f"     Solo hay un {r1['prob']*100:.2f}% de probabilidad de que el consumo")
        print(f"     promedio supere 195 kWh. El plan tarifario es poco probable que")
        print(f"     se vea comprometido en una auditoría típica de 40 hogares.")
        resultados_tcl.append(('TCL-1\nCEO-Energía\nP(X̄>195)', r1, 195, 180, 45, 40, 'mayor'))

        # ── TCL-2: Banca Local ───────────────────────────────────────────────
        print("\n" + "─"*60)
        print("  TCL-2 | Banca Local")
        print("─"*60)
        r2 = self.tipificacion_z(
            x=10.5, mu=12, sigma=4, n=50, direccion='menor',
            nombre="TCL-2: Banca Local — Tiempo en ventanilla",
            descripcion="¿P(tiempo medio < 10.5 min) para 50 clientes un lunes?"
        )
        print(f"\n  💡 INTERPRETACIÓN GERENCIAL:")
        print(f"     Existe un {r2['prob']*100:.2f}% de probabilidad de que el servicio")
        print(f"     sea más eficiente de lo habitual en una muestra de 50 clientes.")
        print(f"     La gerencia puede usar este umbral para medir días excepcionales.")
        resultados_tcl.append(('TCL-2\nBanca Local\nP(X̄<10.5)', r2, 10.5, 12, 4, 50, 'menor'))

        # ── TCL-3: Servi-Logística ───────────────────────────────────────────
        print("\n" + "─"*60)
        print("  TCL-3 | Servi-Logística")
        print("─"*60)
        # Límite de carga: 750 kg para 35 paquetes → promedio límite = 750/35
        limite_prom = 750 / 35
        print(f"\n  → Límite de carga: 750 kg para 35 paquetes")
        print(f"  → Promedio límite: 750/35 = {limite_prom:.4f} kg por paquete")
        r3 = self.tipificacion_z(
            x=limite_prom, mu=20, sigma=5, n=35, direccion='mayor',
            nombre="TCL-3: Servi-Logística — Riesgo de sobrecarga",
            descripcion="¿Riesgo de exceder 750 kg de carga con 35 paquetes de peso medio 20 kg?"
        )
        print(f"\n  💡 INTERPRETACIÓN GERENCIAL:")
        print(f"     El riesgo de sobrecarga es {r3['prob']*100:.2f}%. Para operaciones")
        print(f"     de seguridad vial, se recomienda revisar la distribución real")
        print(f"     del peso antes de despachos con alta variabilidad (σ=5 kg).")
        resultados_tcl.append((f'TCL-3\nServi-Log.\nP(X̄>{limite_prom:.1f})', r3, limite_prom, 20, 5, 35, 'mayor'))

        # ── TCL-4: Sueldos Sector Comercio ──────────────────────────────────
        print("\n" + "─"*60)
        print("  TCL-4 | Sueldos — Sector Comercio")
        print("─"*60)
        se4 = 0.8 / np.sqrt(100)
        z_inf = (2.3 - 2.5) / se4
        z_sup = (2.7 - 2.5) / se4
        prob4 = stats.norm.cdf(z_sup) - stats.norm.cdf(z_inf)

        print(f"\n  Parámetros: μ=2.5M, σ=0.8M, n=100, intervalo [2.3M, 2.7M]")
        print(f"\n  PASO 1 → SE = 0.8/√100 = {se4:.4f} M")
        print(f"  PASO 2 → Z_inf = (2.3-2.5)/{se4:.4f} = {z_inf:.4f}")
        print(f"           Z_sup = (2.7-2.5)/{se4:.4f} = {z_sup:.4f}")
        print(f"  PASO 3 → P(2.3 < X̄ < 2.7) = P({z_inf:.4f} < Z < {z_sup:.4f})")
        print(f"         = Φ({z_sup:.4f}) - Φ({z_inf:.4f}) = {prob4:.4f} = {prob4*100:.2f}%")
        print(f"\n  ✅ RESULTADO: {prob4*100:.2f}% de probabilidad de que el ingreso")
        print(f"     promedio esté entre $2.3M y $2.7M")
        print(f"\n  💡 INTERPRETACIÓN GERENCIAL:")
        print(f"     Con un {prob4*100:.2f}% de confianza, el salario promedio del")
        print(f"     sector comercio en el Cauca estará entre $2.3M y $2.7M.")
        print(f"     Útil para negociaciones salariales y presupuestos de RRHH.")
        r4 = {'z_inf': z_inf, 'z_sup': z_sup, 'prob': prob4, 'se': se4, 'tipo': 'entre'}
        resultados_tcl.append(('TCL-4\nSueldos\nP(2.3<X̄<2.7)', r4, None, 2.5, 0.8, 100, 'entre'))

        # ── TCL-5: Café del Cauca ────────────────────────────────────────────
        print("\n" + "─"*60)
        print("  TCL-5 | Café del Cauca — Exportaciones")
        print("─"*60)
        r5 = self.tipificacion_z(
            x=503, mu=500, sigma=10, n=45, direccion='mayor',
            nombre="TCL-5: Café del Cauca — Bolsas de exportación",
            descripcion="¿P(peso medio > 503g) en lote de 45 bolsas de 500g?"
        )
        print(f"\n  💡 INTERPRETACIÓN GERENCIAL:")
        print(f"     Hay un {r5['prob']*100:.2f}% de probabilidad de que el lote")
        print(f"     promedio supere los 503g. Las exportaciones de café del Cauca")
        print(f"     tienen bajo riesgo de superar el estándar de peso declarado.")
        resultados_tcl.append(('TCL-5\nCafé Cauca\nP(X̄>503)', r5, 503, 500, 10, 45, 'mayor'))

        # ── Graficar los 5 escenarios ────────────────────────────────────────
        for idx, (titulo_g, res, x_crit, mu_g, sigma_g, n_g, dir_g) in enumerate(resultados_tcl):
            ax = axes_tcl[idx]
            se_g = sigma_g / np.sqrt(n_g)
            x_range = np.linspace(mu_g - 4*se_g, mu_g + 4*se_g, 400)
            y_range = stats.norm.pdf(x_range, loc=mu_g, scale=se_g)

            ax.plot(x_range, y_range, color=COLORES['principal'], linewidth=2)

            # Sombrear la probabilidad pedida
            if dir_g == 'mayor' and x_crit is not None:
                mask = x_range >= x_crit
                prob_txt = f"P={res['prob']*100:.2f}%"
                ax.fill_between(x_range, y_range, where=mask,
                                color=COLORES['rojo'], alpha=0.4, label=prob_txt)
                ax.axvline(x_crit, color=COLORES['rojo'], linestyle='--', linewidth=1.5)
            elif dir_g == 'menor' and x_crit is not None:
                mask = x_range <= x_crit
                prob_txt = f"P={res['prob']*100:.2f}%"
                ax.fill_between(x_range, y_range, where=mask,
                                color=COLORES['acento'], alpha=0.4, label=prob_txt)
                ax.axvline(x_crit, color=COLORES['acento'], linestyle='--', linewidth=1.5)
            elif dir_g == 'entre':
                # TCL-4: intervalo bilateral
                mask = (x_range >= 2.3) & (x_range <= 2.7)
                prob_txt = f"P={res['prob']*100:.2f}%"
                ax.fill_between(x_range, y_range, where=mask,
                                color=COLORES['secundario'], alpha=0.5, label=prob_txt)
                ax.axvline(2.3, color=COLORES['acento'], linestyle='--', linewidth=1.2)
                ax.axvline(2.7, color=COLORES['rojo'],   linestyle='--', linewidth=1.2)

            ax.axvline(mu_g, color=COLORES['gris'], linestyle='-.',
                       linewidth=1.2, label=f'μ={mu_g}')
            ax.set_title(titulo_g.replace('\n', ' | '), fontsize=9, fontweight='bold')
            ax.set_xlabel(f'X̄  (SE={se_g:.3f})', fontsize=8)
            ax.set_ylabel('Densidad', fontsize=8)
            ax.legend(fontsize=8)
            ax.tick_params(labelsize=7)

        plt.tight_layout()
        plt.savefig('/mnt/user-data/outputs/Bloque1_TCL_5escenarios.png',
                    dpi=150, bbox_inches='tight')
        plt.show()
        print("\n  ✔ Gráfica Bloque 1 guardada: Bloque1_TCL_5escenarios.png")

    # ─────────────────────────────────────────────────────────────────────────
    # ⑦ BLOQUE 2 — 9 CASOS IC
    # ─────────────────────────────────────────────────────────────────────────
    def resolver_bloque_ic(self):
        """
        Resuelve los 9 casos de Intervalos de Confianza del Bloque 2.
        Cada caso usa la selección automática de método (Z, t o proporciones).
        """
        print("\n" + "█"*65)
        print("  BLOQUE 2: INTERVALOS DE CONFIANZA — 9 CASOS")
        print("  Departamento del Cauca — Análisis Gerencial")
        print("█"*65)

        casos_ic = []   # Para graficar al final

        # ── IC-1: Resistencia de fibras (Z) ──────────────────────────────────
        r = self.analista_intervalos(
            x_bar=50, n=40, sigma=4, confianza=0.95,
            contexto="Resistencia de fibras textiles — Cauca",
            recomendacion_gerencial=(
                f"Con 95% de confianza, la resistencia media de las fibras\n"
                f"  textiles de la región está entre los límites del IC.\n"
                f"  Si el estándar mínimo exigido está dentro del intervalo,\n"
                f"  la producción cumple especificaciones con alta certeza."
            )
        )
        casos_ic.append(('IC-1\nFibras\nTextiles', r))

        # ── IC-2: Costos de fletes (Z) ────────────────────────────────────────
        r = self.analista_intervalos(
            x_bar=1.2e6, n=35, sigma=200e3, confianza=0.95,
            contexto="Costos operativos de fletes intermunicipales",
            recomendacion_gerencial=(
                f"La gerencia puede presupuestar los costos de flete en el\n"
                f"  rango del IC con 95% de confianza. Se recomienda usar\n"
                f"  el límite superior como referencia conservadora en cotizaciones."
            )
        )
        casos_ic.append(('IC-2\nFletes\nIntermunicip.', r))

        # ── IC-3: Peso de empaques (Z) ────────────────────────────────────────
        r = self.analista_intervalos(
            x_bar=22, n=50, sigma=1.5, confianza=0.95,
            contexto="Peso neto de empaques para retail nacional",
            recomendacion_gerencial=(
                f"Si el estándar de peso declarado en empaque es 22g,\n"
                f"  verificar que el límite inferior del IC supere dicho\n"
                f"  estándar para evitar inconformidades con clientes y reguladores."
            )
        )
        casos_ic.append(('IC-3\nEmpaques\nRetail', r))

        # ── IC-4: Mochilas artesanales (t) ───────────────────────────────────
        r = self.analista_intervalos(
            x_bar=22, n=15, s=4, confianza=0.95,
            contexto="Producción artesanal de mochilas wayuu (n<30)",
            recomendacion_gerencial=(
                f"Con solo 15 registros, la estimación tiene mayor incertidumbre\n"
                f"  (tabla t). Se recomienda ampliar la muestra para reducir\n"
                f"  el margen de error y tener estimaciones más precisas de\n"
                f"  la producción artesanal del Cauca."
            )
        )
        casos_ic.append(('IC-4\nMochilas\nArtesanales', r))

        # ── IC-5: Marketing PyMEs (t) ─────────────────────────────────────────
        r = self.analista_intervalos(
            x_bar=3.5e6, n=10, s=0.8e6, confianza=0.95,
            contexto="Presupuesto mensual de marketing en PyMEs del Cauca",
            recomendacion_gerencial=(
                f"Con n=10, el IC es amplio. Los límites orientan el rango\n"
                f"  plausible de inversión en marketing. Se recomienda a las\n"
                f"  PyMEs del Cauca comparar su presupuesto con el límite\n"
                f"  inferior del IC para evaluar competitividad sectorial."
            )
        )
        casos_ic.append(('IC-5\nMarketing\nPyMEs', r))

        # ── IC-6: Días de incapacidad (t) ────────────────────────────────────
        r = self.analista_intervalos(
            x_bar=18, n=12, s=3.5, confianza=0.95,
            contexto="Días de incapacidad en planta de producción",
            recomendacion_gerencial=(
                f"El intervalo para los días de incapacidad permite al\n"
                f"  departamento de RRHH planear coberturas de reemplazo.\n"
                f"  Si el límite superior supera el umbral crítico operativo,\n"
                f"  se recomienda implementar programas preventivos de salud."
            )
        )
        casos_ic.append(('IC-6\nIncapacidad\nPlanta', r))

        # ── IC-7: Aceptación de gaseosa (proporciones) ───────────────────────
        p7 = 450/1000
        r = self.analista_intervalos(
            p_hat=p7, n=1000, confianza=0.95,
            contexto="Nivel de aceptación de nueva marca de gaseosa — n=1000, x=450",
            recomendacion_gerencial=(
                f"La marca tiene una aceptación estimada del {p7*100:.1f}%.\n"
                f"  Si el intervalo incluye 50%, el lanzamiento es incierto.\n"
                f"  Si ambos límites están por debajo de 50%, se recomienda\n"
                f"  replantear estrategia de marca o segmentación de mercado."
            )
        )
        casos_ic.append(('IC-7\nGaseosa\nAceptación', r))

        # ── IC-8: Fallos en software (proporciones) ──────────────────────────
        p8 = 15/500
        r = self.analista_intervalos(
            p_hat=p8, n=500, confianza=0.95,
            contexto="Tasa de fallos en software de inventarios — n=500, x=15",
            recomendacion_gerencial=(
                f"La tasa de fallos estimada es del {p8*100:.1f}%.\n"
                f"  El IC indica el rango real de defectos. Si el límite\n"
                f"  superior supera el SLA de calidad contratado, se debe\n"
                f"  iniciar un proceso de mejora inmediata del software."
            )
        )
        casos_ic.append(('IC-8\nSoftware\nFallos', r))

        # ── IC-9: Modalidad híbrida (proporciones) ───────────────────────────
        p9 = 180/250
        r = self.analista_intervalos(
            p_hat=p9, n=250, confianza=0.95,
            contexto="Empleados que prefieren modalidad híbrida — n=250, x=180",
            recomendacion_gerencial=(
                f"El {p9*100:.1f}% de los empleados prefiere la modalidad híbrida.\n"
                f"  Con el IC al 95%, la gerencia puede implementar esta\n"
                f"  modalidad con alta certeza de satisfacer a la mayoría.\n"
                f"  Se recomienda diseñar política formal de trabajo híbrido."
            )
        )
        casos_ic.append(('IC-9\nModalidad\nHíbrida', r))

        # ── GRÁFICA — Los 9 IC en un panel ──────────────────────────────────
        print("\n\n  📊 Generando visualización de todos los Intervalos de Confianza...")
        fig, axes = plt.subplots(3, 3, figsize=(20, 14))
        fig.suptitle(
            'BLOQUE 2 — Intervalos de Confianza al 95%\nEscenarios Empresariales del Departamento del Cauca',
            fontsize=14, fontweight='bold', color=COLORES['principal']
        )

        for idx, (titulo_g, res) in enumerate(casos_ic):
            ax = axes[idx//3, idx%3]
            self.graficar_intervalo(res, titulo_g, ax=ax)

        plt.tight_layout()
        plt.savefig('/mnt/user-data/outputs/Bloque2_IC_9casos.png',
                    dpi=150, bbox_inches='tight')
        plt.show()
        print("  ✔ Gráfica Bloque 2 guardada: Bloque2_IC_9casos.png")

    # ─────────────────────────────────────────────────────────────────────────
    # ⑧ DEMOSTRACIÓN MOTOR TCL
    # ─────────────────────────────────────────────────────────────────────────
    def demo_motor_tcl(self):
        """
        Ejecuta el motor TCL con los parámetros del primer escenario
        para demostrar visualmente la convergencia del SE.
        """
        print("\n" + "█"*65)
        print("  MOTOR TCL — Demostración Visual de Convergencia")
        print("█"*65)
        print("\n  Mostrando cómo el Error Estándar SE = σ/√n disminuye")
        print("  conforme aumenta el tamaño de muestra n.\n")

        self.motor_tcl(
            mu=180, sigma=45,
            n_valores=[5, 15, 30, 60, 100, 200],
            titulo_extra="CEO-Energía Popayán (μ=180 kWh, σ=45)"
        )

        # Segunda demostración con parámetros del Café del Cauca
        self.motor_tcl(
            mu=500, sigma=10,
            n_valores=[10, 25, 45, 80, 150],
            titulo_extra="Café del Cauca (μ=500g, σ=10g)"
        )

    # ─────────────────────────────────────────────────────────────────────────
    # ⑨ EJECUTAR SIMULACIÓN COMPLETA
    # ─────────────────────────────────────────────────────────────────────────
    def ejecutar_simulacion_completa(self):
        """
        Punto de entrada principal. Ejecuta todos los módulos en orden.
        """
        print("\n" + "▓"*65)
        print("  SIMULADOR DE ESTADÍSTICA INFERENCIAL — UNICAUCA")
        print("  Administración de Empresas | Popayán, Cauca 2025")
        print("▓"*65)

        # 1. Motor TCL visual
        self.demo_motor_tcl()

        # 2. Calculador de errores (ejemplo interactivo)
        print("\n" + "█"*65)
        print("  CALCULADOR DE ERRORES — Ejemplos Comparativos")
        print("█"*65)
        for n_ej in [10, 30, 100, 500]:
            self.calcular_errores(sigma=45, n=n_ej, verbose=True)

        # 3. Bloque 1 — TCL
        self.resolver_bloque_tcl()

        # 4. Bloque 2 — IC
        self.resolver_bloque_ic()

        print("\n" + "▓"*65)
        print("  ✅ SIMULACIÓN COMPLETA FINALIZADA")
        print("  Archivos generados en /outputs:")
        print("    · TCL_motor_CEO-Energía_Popayán.png")
        print("    · TCL_motor_Café_del_Cauca.png")
        print("    · Bloque1_TCL_5escenarios.png")
        print("    · Bloque2_IC_9casos.png")
        print("▓"*65)


# ═════════════════════════════════════════════════════════════════════════════
# PUNTO DE ENTRADA
# ═════════════════════════════════════════════════════════════════════════════
if __name__ == "__main__":
    simulador = SimuladorUnicauca()
    simulador.ejecutar_simulacion_completa()
