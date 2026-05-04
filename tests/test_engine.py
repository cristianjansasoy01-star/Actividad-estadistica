from simulador_unicauca.core import SimuladorUnicauca
from simulador_unicauca.models import CasoICMedia, CasoICProporcion, CasoTCL


def test_error_estandar():
    sim = SimuladorUnicauca()
    assert round(sim.error_estandar_media(45, 40), 4) == 7.1151


def test_tcl_ceo_energia():
    sim = SimuladorUnicauca()
    r = sim.resolver_tcl(CasoTCL("TCL-1", "CEO-Energía", 180, 45, 40, "mayor", limite=195))
    assert round(r.probabilidad, 4) == 0.0175


def test_ic_media_z():
    sim = SimuladorUnicauca()
    r = sim.intervalo_media(CasoICMedia("Fibras", 40, 50, sigma=4))
    assert round(r.limite_inferior, 4) == 48.7604
    assert round(r.limite_superior, 4) == 51.2396


def test_ic_proporcion():
    sim = SimuladorUnicauca()
    r = sim.intervalo_proporcion(CasoICProporcion("Aceptación", 1000, 450))
    assert round(r.estimador, 2) == 0.45
