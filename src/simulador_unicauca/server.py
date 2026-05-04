"""Servidor web local del simulador."""

from __future__ import annotations

import json
from http.server import BaseHTTPRequestHandler, HTTPServer
from math import sqrt
from urllib.parse import urlparse

from .cases import casos_ic_media_documento, casos_ic_proporcion_documento, casos_tcl_documento
from .charts import grafica_campana, grafica_campanas_comparativas, grafica_error_estandar, grafica_intervalo
from .core import SimuladorUnicauca
from .models import CasoICMedia, CasoICProporcion, CasoTCL

sim = SimuladorUnicauca()


def _json(handler: BaseHTTPRequestHandler, status: int, data: dict) -> None:
    payload = json.dumps(data, ensure_ascii=False).encode("utf-8")
    handler.send_response(status)
    handler.send_header("Content-Type", "application/json; charset=utf-8")
    handler.send_header("Content-Length", str(len(payload)))
    handler.end_headers()
    handler.wfile.write(payload)


def _html(handler: BaseHTTPRequestHandler, content: str) -> None:
    payload = content.encode("utf-8")
    handler.send_response(200)
    handler.send_header("Content-Type", "text/html; charset=utf-8")
    handler.send_header("Content-Length", str(len(payload)))
    handler.end_headers()
    handler.wfile.write(payload)


def _read_json(handler: BaseHTTPRequestHandler) -> dict:
    length = int(handler.headers.get("Content-Length", "0"))
    body = handler.rfile.read(length).decode("utf-8")
    return json.loads(body or "{}")


def _float(data: dict, key: str, default=None) -> float:
    value = data.get(key, default)
    if value in (None, ""):
        raise ValueError(f"El campo '{key}' es obligatorio.")
    return float(value)


def _int(data: dict, key: str, default=None) -> int:
    value = data.get(key, default)
    if value in (None, ""):
        raise ValueError(f"El campo '{key}' es obligatorio.")
    return int(value)


def api_tcl(data: dict) -> dict:
    tipo = data.get("tipo", "mayor")
    unidad = data.get("unidad", "")
    mu = _float(data, "mu")
    sigma = _float(data, "sigma")
    n = _int(data, "n")
    observada = float(data.get("media_observada") or mu)
    ns = [int(x) for x in data.get("ns", [5, 10, 30, n, 100]) if int(x) > 0]

    caso = CasoTCL(
        ref="PERSONALIZADO",
        escenario=data.get("nombre", "Caso personalizado"),
        mu=mu,
        sigma=sigma,
        n=n,
        tipo=tipo,
        limite=float(data["limite"]) if data.get("limite") not in (None, "") else None,
        limite_inferior=float(data["limite_inferior"]) if data.get("limite_inferior") not in (None, "") else None,
        limite_superior=float(data["limite_superior"]) if data.get("limite_superior") not in (None, "") else None,
        unidad=unidad,
        contexto=data.get("contexto", ""),
    )
    r = sim.resolver_tcl(caso)
    error_muestra = sim.error_muestra(observada, mu)

    if tipo == "suma_mayor":
        media_suma = n * mu
        sd_suma = sigma * sqrt(n)
        area = grafica_campana(media_suma, sd_suma, "mayor", limite=caso.limite, titulo="Área de probabilidad para la suma", unidad=unidad)
    elif tipo == "entre":
        area = grafica_campana(mu, r.se, "entre", li=caso.limite_inferior, ls=caso.limite_superior, titulo="Área de probabilidad para la media muestral", unidad=unidad)
    else:
        area = grafica_campana(mu, r.se, tipo, limite=caso.limite, titulo="Área de probabilidad para la media muestral", unidad=unidad)

    return {
        "ok": True,
        "resultado": {
            "escenario": r.escenario,
            "pregunta": r.pregunta,
            "se": r.se,
            "z": r.z,
            "probabilidad": r.probabilidad,
            "probabilidad_pct": f"{r.probabilidad:.4%}",
            "procedimiento": r.procedimiento,
            "interpretacion": r.interpretacion,
            "error_muestra": error_muestra,
            "formula_error": f"Error de muestra = x̄ - μ = {observada} - {mu} = {error_muestra:.6f}",
            "formula_se": f"SE = σ/√n = {sigma}/√{n} = {r.se:.6f}",
        },
        "graficas": {
            "area": area,
            "campanas": grafica_campanas_comparativas(mu, sigma, ns, unidad),
            "se": grafica_error_estandar(sigma, n, unidad),
        },
    }


def api_ic(data: dict) -> dict:
    tipo = data.get("tipo", "media")
    confianza = float(data.get("confianza", 0.95))
    unidad = data.get("unidad", "")
    meta_raw = data.get("meta", None)
    meta = float(meta_raw) if meta_raw not in (None, "") else None

    if tipo == "media":
        caso = CasoICMedia(
            nombre=data.get("nombre", "Caso personalizado"),
            n=_int(data, "n"),
            media_muestral=_float(data, "media_muestral"),
            sigma=float(data["sigma"]) if data.get("sigma") not in (None, "") else None,
            s=float(data["s"]) if data.get("s") not in (None, "") else None,
            confianza=confianza,
            unidad=unidad,
            contexto=data.get("contexto", ""),
        )
        r = sim.intervalo_media(caso, meta)
    else:
        caso = CasoICProporcion(
            nombre=data.get("nombre", "Caso personalizado"),
            n=_int(data, "n"),
            x=_int(data, "x"),
            confianza=confianza,
            contexto=data.get("contexto", ""),
        )
        r = sim.intervalo_proporcion(caso, meta)

    return {
        "ok": True,
        "resultado": {
            "caso": r.caso,
            "modelo": r.modelo,
            "razon": r.razon,
            "estimador": r.estimador,
            "se": r.se,
            "valor_critico": r.valor_critico,
            "margen_error": r.margen_error,
            "limite_inferior": r.limite_inferior,
            "limite_superior": r.limite_superior,
            "formula": r.formula,
            "recomendacion": r.recomendacion,
            "es_proporcion": r.es_proporcion,
        },
        "graficas": {
            "intervalo": grafica_intervalo(r.limite_inferior, r.limite_superior, r.estimador, unidad, r.es_proporcion)
        },
    }


def api_casos() -> dict:
    tcl = []
    for c in casos_tcl_documento():
        r = sim.resolver_tcl(c)
        tcl.append({"ref": c.ref, "escenario": c.escenario, "n": c.n, "se": r.se, "z": r.z, "probabilidad_pct": f"{r.probabilidad:.4%}"})

    ic = []
    for c in casos_ic_media_documento():
        r = sim.intervalo_media(c)
        ic.append({"caso": c.nombre, "modelo": r.modelo, "estimador": r.estimador, "se": r.se, "li": r.limite_inferior, "ls": r.limite_superior, "unidad": c.unidad, "es_proporcion": False})

    for c in casos_ic_proporcion_documento():
        r = sim.intervalo_proporcion(c)
        ic.append({"caso": c.nombre, "modelo": r.modelo, "estimador": r.estimador, "se": r.se, "li": r.limite_inferior, "ls": r.limite_superior, "unidad": "%", "es_proporcion": True})

    return {"ok": True, "tcl": tcl, "ic": ic}


def home_html() -> str:
    return """<!doctype html>
<html lang="es">
<head>
<meta charset="utf-8">
<title>Simulador Unicauca Python Pro</title>
<meta name="viewport" content="width=device-width, initial-scale=1">
<style>
:root{--blue:#003366;--blue2:#0b6b8f;--cyan:#e0f2fe;--green:#ecfdf5;--orange:#fff7ed;--gray:#f4f6f8;--text:#1f2937;--card:#fff}
*{box-sizing:border-box}
body{margin:0;font-family:Arial,Helvetica,sans-serif;background:var(--gray);color:var(--text);line-height:1.55}
header{background:linear-gradient(135deg,var(--blue),var(--blue2));color:white;padding:34px 6%}
header h1{margin:0 0 8px;font-size:34px}
header p{margin:0;opacity:.95;font-size:17px}
nav{position:sticky;top:0;z-index:5;background:white;border-bottom:1px solid #e5e7eb;padding:10px 6%;display:flex;gap:10px;flex-wrap:wrap;box-shadow:0 4px 16px rgba(0,0,0,.06)}
nav a{color:var(--blue);text-decoration:none;font-weight:bold;padding:7px 12px;border-radius:999px;background:#f8fafc}
main{padding:24px 6% 70px}
.card{background:var(--card);border-radius:18px;padding:22px;box-shadow:0 8px 24px rgba(0,0,0,.08);margin:18px 0}
.grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(280px,1fr));gap:16px}
h2{color:var(--blue);margin-top:32px;font-size:28px}
h3{color:#0f3e5a;margin:8px 0}
label{display:block;font-size:14px;color:#374151;margin:10px 0 5px;font-weight:bold}
input,select{width:100%;padding:10px 12px;border:1px solid #cbd5e1;border-radius:10px;font-size:15px;background:white}
button{border:0;padding:11px 16px;border-radius:12px;font-weight:bold;cursor:pointer;background:var(--blue2);color:white;margin:10px 8px 0 0;box-shadow:0 4px 12px rgba(0,0,0,.12)}
button.secondary{background:#475569}
button.warn{background:#b45309}
.eq{background:#f8fafc;border-left:5px solid var(--blue2);padding:12px 14px;margin:12px 0;border-radius:10px;font-size:17px}
.result{background:var(--green);border:1px solid #86efac;padding:12px 14px;border-radius:12px;margin:12px 0}
.warning{background:var(--orange);border:1px solid #fed7aa;padding:12px 14px;border-radius:12px;margin:12px 0}
.error{background:#fee2e2;border:1px solid #fca5a5;padding:12px 14px;border-radius:12px;margin:12px 0}
.tag{display:inline-block;background:var(--cyan);color:#075985;padding:4px 10px;border-radius:999px;font-weight:bold;font-size:13px}
.svg-wrap{background:white;border:1px solid #e5e7eb;border-radius:18px;padding:12px;margin:14px 0;overflow-x:auto}
.legend{display:flex;flex-wrap:wrap;gap:12px 18px;font-size:14px;margin:8px 0 0 4px}
.legend i{display:inline-block;width:14px;height:14px;border-radius:3px;margin-right:7px;vertical-align:-2px}
table{width:100%;border-collapse:collapse;background:white;border-radius:14px;overflow:hidden;box-shadow:0 8px 24px rgba(0,0,0,.06);margin:14px 0}
th,td{padding:11px;border-bottom:1px solid #e5e7eb;text-align:left;vertical-align:top}
th{background:#0f3e5a;color:white}
.kpi{display:grid;grid-template-columns:repeat(auto-fit,minmax(180px,1fr));gap:10px}
.kpi div{background:#f8fafc;border:1px solid #e5e7eb;border-radius:14px;padding:14px}
.kpi b{display:block;color:var(--blue);font-size:20px}
@media print{nav,button{display:none!important}body{background:white}.card{box-shadow:none;border:1px solid #e5e7eb;break-inside:avoid}}
</style>
</head>
<body>
<header>
<h1>Simulador Unicauca Python Pro</h1>
<p>Aplicación local en Python para TCL, errores e Intervalos de Confianza con gráficas SVG.</p>
</header>
<nav>
<a href="#tcl">Calculadora TCL</a>
<a href="#ic">Calculadora IC</a>
<a href="#validacion">Casos del PDF</a>
<a href="#guia">Sustentación</a>
</nav>
<main>
<section class="card">
<h2>Idea central</h2>
<p>La interfaz envía los datos al motor estadístico Python y recibe resultados, ecuaciones y gráficas.</p>
<div class="eq">Error de muestra = x̄ − μ</div>
<div class="eq">Error Estándar de la Media = SE = σ / √n</div>
</section>

<section id="tcl" class="card">
<h2>1. Calculadora TCL</h2>
<div class="grid">
<div><label>Escenario</label><input id="tclName" value="Mi escenario económico del Cauca"></div>
<div><label>Unidad</label><input id="tclUnit" value="unidades"></div>
<div><label>Media poblacional μ</label><input id="tclMu" type="number" step="any" value="180"></div>
<div><label>Desviación estándar σ</label><input id="tclSigma" type="number" step="any" value="45"></div>
<div><label>Tamaño de muestra n</label><input id="tclN" type="number" step="1" value="40"></div>
<div><label>Tipo de pregunta</label><select id="tclType" onchange="syncTclInputs()"><option value="mayor">P(X̄ > valor)</option><option value="menor">P(X̄ < valor)</option><option value="entre">P(a < X̄ < b)</option><option value="suma_mayor">P(Suma > valor)</option></select></div>
<div id="singleLimitBox"><label>Límite</label><input id="tclLimit" type="number" step="any" value="195"></div>
<div id="lowerBox" style="display:none"><label>Límite inferior</label><input id="tclLower" type="number" step="any" value="2.3"></div>
<div id="upperBox" style="display:none"><label>Límite superior</label><input id="tclUpper" type="number" step="any" value="2.7"></div>
<div><label>Media observada x̄ para error de muestra</label><input id="tclObserved" type="number" step="any" value="195"></div>
<div><label>n para comparar campanas</label><input id="tclNs" value="5,10,30,40,100"></div>
</div>
<button onclick="calculateTCL()">Calcular TCL</button>
<button class="secondary" onclick="clearBox('tclOutput')">Limpiar</button>
<div id="tclOutput"></div>
</section>

<section id="ic" class="card">
<h2>2. Calculadora de Intervalos de Confianza</h2>
<div class="grid">
<div><label>Nombre del caso</label><input id="icName" value="Mi intervalo de confianza"></div>
<div><label>Tipo de parámetro</label><select id="icType" onchange="syncICInputs()"><option value="media">Media</option><option value="proporcion">Proporción</option></select></div>
<div><label>Confianza</label><select id="icConf"><option value="0.90">90%</option><option value="0.95" selected>95%</option><option value="0.99">99%</option></select></div>
<div><label>Tamaño n</label><input id="icN" type="number" step="1" value="40"></div>
<div id="xbarBox"><label>Media muestral x̄</label><input id="icXbar" type="number" step="any" value="50"></div>
<div id="sigmaKnownBox"><label>¿σ conocida?</label><select id="icSigmaKnown" onchange="syncICInputs()"><option value="yes">Sí</option><option value="no">No, usar s</option></select></div>
<div id="sigmaBox"><label>σ poblacional</label><input id="icSigma" type="number" step="any" value="4"></div>
<div id="sBox" style="display:none"><label>s muestral</label><input id="icS" type="number" step="any" value="4"></div>
<div id="xBox" style="display:none"><label>x éxitos</label><input id="icX" type="number" step="1" value="450"></div>
<div><label>Unidad</label><input id="icUnit" value="unidades"></div>
<div><label>Meta opcional</label><input id="icMeta" type="number" step="any" placeholder="Ej: 50 o 0.5"></div>
</div>
<button onclick="calculateIC()">Calcular IC</button>
<button class="secondary" onclick="clearBox('icOutput')">Limpiar</button>
<div id="icOutput"></div>
</section>

<section id="validacion" class="card">
<h2>3. Casos del PDF</h2>
<button class="warn" onclick="loadPDFCases()">Resolver todos los casos del documento</button>
<div id="pdfOutput"></div>
</section>

<section id="guia" class="card">
<h2>4. Guía de sustentación</h2>
<div class="grid">
<div class="card"><h3>¿Por qué Z?</h3><p>Porque σ poblacional es conocida o porque la muestra es grande.</p></div>
<div class="card"><h3>¿Por qué t?</h3><p>Porque σ es desconocida, se estima con s y la muestra es pequeña.</p></div>
<div class="card"><h3>¿Por qué proporciones?</h3><p>Porque el parámetro es p y se estima con p̂ = x/n.</p></div>
<div class="card"><h3>¿Qué es SE?</h3><p>Es la desviación estándar de la distribución de medias muestrales.</p></div>
</div>
</section>
</main>

<script>
function $(id){return document.getElementById(id)}
function num(id){const v=parseFloat($(id).value); if(Number.isNaN(v)) throw new Error("Campo numérico inválido: "+id); return v}
function intNum(id){const v=parseInt($(id).value,10); if(Number.isNaN(v)) throw new Error("Campo entero inválido: "+id); return v}
function fmt(x,d=4){return Number(x).toFixed(d)}
function pct(x,d=4){return (100*x).toFixed(d)+"%"}
function clearBox(id){$(id).innerHTML=""}
function syncTclInputs(){const t=$("tclType").value;$("singleLimitBox").style.display=t==="entre"?"none":"block";$("lowerBox").style.display=t==="entre"?"block":"none";$("upperBox").style.display=t==="entre"?"block":"none"}
function syncICInputs(){const type=$("icType").value;const known=$("icSigmaKnown").value;const prop=type==="proporcion";$("xbarBox").style.display=prop?"none":"block";$("sigmaKnownBox").style.display=prop?"none":"block";$("sigmaBox").style.display=(!prop&&known==="yes")?"block":"none";$("sBox").style.display=(!prop&&known==="no")?"block":"none";$("xBox").style.display=prop?"block":"none"}
async function postJSON(url,data){const res=await fetch(url,{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify(data)});return await res.json()}
function renderError(id,msg){$(id).innerHTML=`<div class="error"><b>Error:</b> ${msg}</div>`}

async function calculateTCL(){
try{
const tipo=$("tclType").value
const ns=$("tclNs").value.split(",").map(s=>parseInt(s.trim(),10)).filter(n=>Number.isFinite(n)&&n>0)
const data={nombre:$("tclName").value,unidad:$("tclUnit").value,mu:num("tclMu"),sigma:num("tclSigma"),n:intNum("tclN"),tipo:tipo,media_observada:num("tclObserved"),ns:ns}
if(tipo==="entre"){data.limite_inferior=num("tclLower");data.limite_superior=num("tclUpper")}else{data.limite=num("tclLimit")}
const json=await postJSON("/api/tcl",data)
if(!json.ok) throw new Error(json.error)
const r=json.resultado
$("tclOutput").innerHTML=`<div class="card"><span class="tag">Resultado TCL</span><h3>${r.escenario}</h3><div class="kpi"><div><span>SE</span><b>${fmt(r.se,6)}</b></div><div><span>Error de muestra</span><b>${fmt(r.error_muestra,6)}</b></div><div><span>Z</span><b>${r.z}</b></div><div><span>Probabilidad</span><b>${r.probabilidad_pct}</b></div></div><div class="eq">${r.formula_error}</div><div class="eq">${r.formula_se}</div><div class="eq">${r.procedimiento}</div><p class="result"><b>${r.pregunta}</b> = ${r.probabilidad_pct}</p><p class="warning">${r.interpretacion}</p>${json.graficas.area}${json.graficas.campanas}${json.graficas.se}</div>`
}catch(e){renderError("tclOutput",e.message)}
}

async function calculateIC(){
try{
const type=$("icType").value
const data={nombre:$("icName").value,tipo:type,confianza:parseFloat($("icConf").value),n:intNum("icN"),unidad:$("icUnit").value,meta:$("icMeta").value}
if(type==="media"){data.media_muestral=num("icXbar"); if($("icSigmaKnown").value==="yes") data.sigma=num("icSigma"); else data.s=num("icS")}else{data.x=intNum("icX")}
const json=await postJSON("/api/ic",data)
if(!json.ok) throw new Error(json.error)
const r=json.resultado
const interval=r.es_proporcion?`[${pct(r.limite_inferior,2)}, ${pct(r.limite_superior,2)}]`:`[${fmt(r.limite_inferior,6)}, ${fmt(r.limite_superior,6)}] ${$("icUnit").value}`
const estim=r.es_proporcion?pct(r.estimador,4):`${fmt(r.estimador,6)} ${$("icUnit").value}`
$("icOutput").innerHTML=`<div class="card"><span class="tag">Resultado IC</span><h3>${r.caso}</h3><p><b>Modelo elegido:</b> ${r.modelo}</p><p><b>Justificación:</b> ${r.razon}</p><div class="kpi"><div><span>Estimador</span><b>${estim}</b></div><div><span>SE</span><b>${fmt(r.se,6)}</b></div><div><span>Crítico</span><b>${fmt(r.valor_critico,6)}</b></div><div><span>Margen</span><b>${fmt(r.margen_error,6)}</b></div></div><div class="eq">${r.formula}</div><p class="result"><b>IC:</b> ${interval}</p>${json.graficas.intervalo}<p class="warning"><b>Recomendación gerencial:</b> ${r.recomendacion}</p></div>`
}catch(e){renderError("icOutput",e.message)}
}

async function loadPDFCases(){
try{
const res=await fetch("/api/casos")
const json=await res.json()
if(!json.ok) throw new Error(json.error)
const tclRows=json.tcl.map(r=>`<tr><td>${r.ref}</td><td>${r.escenario}</td><td>${r.n}</td><td>${fmt(r.se,4)}</td><td>${r.z}</td><td>${r.probabilidad_pct}</td></tr>`).join("")
const icRows=json.ic.map(r=>{const est=r.es_proporcion?pct(r.estimador,2):`${fmt(r.estimador,4)} ${r.unidad}`;const li=r.es_proporcion?pct(r.li,2):`${fmt(r.li,4)} ${r.unidad}`;const ls=r.es_proporcion?pct(r.ls,2):`${fmt(r.ls,4)} ${r.unidad}`;return `<tr><td>${r.caso}</td><td>${r.modelo}</td><td>${est}</td><td>${fmt(r.se,4)}</td><td>${li}</td><td>${ls}</td></tr>`}).join("")
$("pdfOutput").innerHTML=`<div class="card"><h3>Bloque 1 - TCL</h3><table><thead><tr><th>Ref</th><th>Escenario</th><th>n</th><th>SE</th><th>Z</th><th>Probabilidad</th></tr></thead><tbody>${tclRows}</tbody></table><h3>Bloque 2 - Intervalos de Confianza</h3><table><thead><tr><th>Caso</th><th>Modelo</th><th>Estimador</th><th>SE</th><th>LI</th><th>LS</th></tr></thead><tbody>${icRows}</tbody></table></div>`
}catch(e){renderError("pdfOutput",e.message)}
}
syncTclInputs();syncICInputs();calculateTCL();calculateIC();
</script>
</body>
</html>"""


class Handler(BaseHTTPRequestHandler):
    def log_message(self, format: str, *args) -> None:
        return

    def do_GET(self) -> None:
        path = urlparse(self.path).path
        if path == "/":
            _html(self, home_html())
            return
        if path == "/api/casos":
            try:
                _json(self, 200, api_casos())
            except Exception as exc:
                _json(self, 400, {"ok": False, "error": str(exc)})
            return
        _json(self, 404, {"ok": False, "error": "Ruta no encontrada."})

    def do_POST(self) -> None:
        path = urlparse(self.path).path
        try:
            data = _read_json(self)
            if path == "/api/tcl":
                _json(self, 200, api_tcl(data))
                return
            if path == "/api/ic":
                _json(self, 200, api_ic(data))
                return
            _json(self, 404, {"ok": False, "error": "Ruta no encontrada."})
        except Exception as exc:
            _json(self, 400, {"ok": False, "error": str(exc)})


def run_server(host: str = "127.0.0.1", port: int = 8000) -> None:
    server = HTTPServer((host, port), Handler)
    server.serve_forever()
