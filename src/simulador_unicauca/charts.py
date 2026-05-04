"""Gráficas SVG generadas con Python puro."""

from __future__ import annotations

from math import sqrt

from .distributions import normal_pdf


def grafica_campana(mu: float, sigma: float, tipo: str, limite: float | None = None, li: float | None = None, ls: float | None = None, titulo: str = "Área de probabilidad", unidad: str = "") -> str:
    width, height = 900, 360
    x_min, x_max = mu - 4 * sigma, mu + 4 * sigma
    xs = [x_min + i * (x_max - x_min) / 260 for i in range(261)]
    ys = [normal_pdf(x, mu, sigma) for x in xs]
    y_max = max(ys) * 1.14

    def sx(x): return 60 + (x - x_min) / (x_max - x_min) * (width - 100)
    def sy(y): return height - 45 - y / y_max * (height - 85)

    points = " ".join(f"{sx(x):.2f},{sy(y):.2f}" for x, y in zip(xs, ys))

    shaded = []
    for x, y in zip(xs, ys):
        include = False
        if tipo == "mayor":
            include = limite is not None and x >= limite
        elif tipo == "menor":
            include = limite is not None and x <= limite
        elif tipo == "entre":
            include = li is not None and ls is not None and li <= x <= ls
        if include:
            shaded.append((sx(x), sy(y)))

    shade_path = ""
    if len(shaded) > 1:
        start, end = shaded[0], shaded[-1]
        middle = " L ".join(f"{x:.2f} {y:.2f}" for x, y in shaded)
        shade_path = f'<path d="M {start[0]:.2f} {height-45} L {middle} L {end[0]:.2f} {height-45} Z" fill="#7dd3fc" opacity="0.55"/>'

    limit_lines = ""
    if tipo in {"mayor", "menor"} and limite is not None:
        x_l = sx(limite)
        limit_lines += f'<line x1="{x_l:.2f}" y1="25" x2="{x_l:.2f}" y2="{height-45}" stroke="#d62728" stroke-dasharray="7,6" stroke-width="2"/>'
        limit_lines += f'<text x="{x_l + 6:.2f}" y="60" font-size="14">Límite {limite:g} {unidad}</text>'

    if tipo == "entre" and li is not None and ls is not None:
        x_li, x_ls = sx(li), sx(ls)
        limit_lines += f'<line x1="{x_li:.2f}" y1="25" x2="{x_li:.2f}" y2="{height-45}" stroke="#d62728" stroke-dasharray="7,6" stroke-width="2"/>'
        limit_lines += f'<line x1="{x_ls:.2f}" y1="25" x2="{x_ls:.2f}" y2="{height-45}" stroke="#d62728" stroke-dasharray="7,6" stroke-width="2"/>'
        limit_lines += f'<text x="{x_li + 6:.2f}" y="60" font-size="14">LI={li:g}</text>'
        limit_lines += f'<text x="{x_ls + 6:.2f}" y="82" font-size="14">LS={ls:g}</text>'

    x_mu = sx(mu)
    return f"""
    <div class="svg-wrap">
    <svg viewBox="0 0 {width} {height}" width="100%">
      <rect x="0" y="0" width="{width}" height="{height}" fill="#fff"/>
      <text x="60" y="22" font-size="16" font-weight="bold">{titulo}</text>
      <line x1="60" y1="{height-45}" x2="{width-40}" y2="{height-45}" stroke="#444" stroke-width="1.5"/>
      <line x1="60" y1="25" x2="60" y2="{height-45}" stroke="#444" stroke-width="1.5"/>
      {shade_path}
      <polyline points="{points}" fill="none" stroke="#1f77b4" stroke-width="3"/>
      <line x1="{x_mu:.2f}" y1="25" x2="{x_mu:.2f}" y2="{height-45}" stroke="#111" stroke-dasharray="4,5" stroke-width="2"/>
      <text x="{x_mu + 7:.2f}" y="42" font-size="14">Media = {mu:.3f}</text>
      {limit_lines}
      <text x="{width/2 - 105}" y="{height-12}" font-size="14">Variable analizada</text>
      <text x="16" y="30" font-size="14">Densidad</text>
    </svg>
    </div>
    """


def grafica_campanas_comparativas(mu: float, sigma: float, ns: list[int], unidad: str = "") -> str:
    width, height = 900, 360
    x_min, x_max = mu - 3 * sigma, mu + 3 * sigma
    xs = [x_min + i * (x_max - x_min) / 240 for i in range(241)]
    all_y = []
    for n in ns:
        se = sigma / sqrt(n)
        all_y.extend(normal_pdf(x, mu, se) for x in xs)
    y_max = max(all_y) * 1.14

    def sx(x): return 60 + (x - x_min) / (x_max - x_min) * (width - 100)
    def sy(y): return height - 45 - y / y_max * (height - 85)

    colors = ["#1f77b4", "#ff7f0e", "#2ca02c", "#9467bd", "#d62728", "#0f766e"]
    paths, legend = [], []
    for idx, n in enumerate(ns):
        se = sigma / sqrt(n)
        pts = " ".join(f"{sx(x):.2f},{sy(normal_pdf(x, mu, se)):.2f}" for x in xs)
        color = colors[idx % len(colors)]
        paths.append(f'<polyline points="{pts}" fill="none" stroke="{color}" stroke-width="3"/>')
        legend.append(f'<span><i style="background:{color}"></i>n={n}, SE={se:.3f} {unidad}</span>')

    x_mu = sx(mu)
    return f"""
    <div class="svg-wrap">
    <svg viewBox="0 0 {width} {height}" width="100%">
      <rect x="0" y="0" width="{width}" height="{height}" fill="#fff"/>
      <text x="60" y="22" font-size="16" font-weight="bold">Campanas comparativas: al aumentar n, disminuye SE</text>
      <line x1="60" y1="{height-45}" x2="{width-40}" y2="{height-45}" stroke="#444" stroke-width="1.5"/>
      <line x1="60" y1="25" x2="60" y2="{height-45}" stroke="#444" stroke-width="1.5"/>
      {''.join(paths)}
      <line x1="{x_mu:.2f}" y1="25" x2="{x_mu:.2f}" y2="{height-45}" stroke="#111" stroke-dasharray="7,6" stroke-width="2"/>
      <text x="{x_mu + 7:.2f}" y="42" font-size="14">μ={mu:g}</text>
      <text x="{width/2 - 120}" y="{height-12}" font-size="14">Media muestral X̄</text>
      <text x="16" y="30" font-size="14">Densidad</text>
    </svg>
    <div class="legend">{''.join(legend)}</div>
    </div>
    """


def grafica_error_estandar(sigma: float, n_actual: int, unidad: str = "") -> str:
    width, height = 900, 330
    n_max = max(200, n_actual * 3)
    ns = list(range(2, n_max + 1))
    ses = [sigma / sqrt(n) for n in ns]
    y_max = max(ses) * 1.08

    def sx(n): return 60 + (n - 2) / (n_max - 2) * (width - 100)
    def sy(se): return height - 45 - se / y_max * (height - 80)

    pts = " ".join(f"{sx(n):.2f},{sy(se):.2f}" for n, se in zip(ns, ses))
    se_actual = sigma / sqrt(n_actual)

    return f"""
    <div class="svg-wrap">
    <svg viewBox="0 0 {width} {height}" width="100%">
      <rect x="0" y="0" width="{width}" height="{height}" fill="#fff"/>
      <text x="60" y="22" font-size="16" font-weight="bold">Reducción del Error Estándar</text>
      <line x1="60" y1="{height-45}" x2="{width-40}" y2="{height-45}" stroke="#444" stroke-width="1.5"/>
      <line x1="60" y1="25" x2="60" y2="{height-45}" stroke="#444" stroke-width="1.5"/>
      <polyline points="{pts}" fill="none" stroke="#1f77b4" stroke-width="3"/>
      <circle cx="{sx(n_actual):.2f}" cy="{sy(se_actual):.2f}" r="7" fill="#d62728"/>
      <text x="{sx(n_actual)+8:.2f}" y="{sy(se_actual)-8:.2f}" font-size="14">n={n_actual}, SE={se_actual:.3f} {unidad}</text>
      <text x="{width/2 - 90}" y="{height-12}" font-size="14">Tamaño de muestra n</text>
      <text x="16" y="30" font-size="14">SE</text>
    </svg>
    </div>
    """


def grafica_intervalo(li: float, ls: float, estimador: float, unidad: str = "", es_proporcion: bool = False) -> str:
    width, height = 840, 135
    margin = (ls - li) * 0.35 if ls != li else 1
    x_min, x_max = li - margin, ls + margin

    def sx(x): return 55 + (x - x_min) / (x_max - x_min) * (width - 110)
    def etiqueta(x): return f"{x:.2%}" if es_proporcion else f"{x:.4f} {unidad}"

    y = 65
    return f"""
    <div class="svg-wrap">
    <svg viewBox="0 0 {width} {height}" width="100%">
      <rect width="{width}" height="{height}" fill="#fff"/>
      <text x="55" y="22" font-size="16" font-weight="bold">Visualización del intervalo de confianza</text>
      <line x1="{sx(li):.2f}" y1="{y}" x2="{sx(ls):.2f}" y2="{y}" stroke="#1f77b4" stroke-width="9" stroke-linecap="round"/>
      <circle cx="{sx(li):.2f}" cy="{y}" r="7" fill="#1f77b4"/>
      <circle cx="{sx(ls):.2f}" cy="{y}" r="7" fill="#1f77b4"/>
      <circle cx="{sx(estimador):.2f}" cy="{y}" r="9" fill="#d62728"/>
      <text x="{sx(li)-35:.2f}" y="108" font-size="13">LI {etiqueta(li)}</text>
      <text x="{sx(ls)-35:.2f}" y="108" font-size="13">LS {etiqueta(ls)}</text>
      <text x="{sx(estimador)-55:.2f}" y="48" font-size="13">Estimador {etiqueta(estimador)}</text>
    </svg>
    </div>
    """
