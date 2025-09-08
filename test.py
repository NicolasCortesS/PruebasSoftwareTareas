from datetime import datetime, timedelta, UTC
from domain import (
    auth_user, create_event, update_event, delete_event,
    sell, refund, list_events, report_summary
)

def ok(msg): print(msg)
def fail(msg): print(msg)

def expect_error(fn, *args, **kwargs):
    try:
        fn(*args, **kwargs)
        fail(f"Se esperaba error en {fn.__name__}")
    except Exception as e:
        ok(f"Error esperado en {fn.__name__}: {e}")

def main():
    auth = auth_user("admin", "admin123")
    if not auth:
        fail("Login admin falló (¿creaste el usuario con seed_admin?)")
        return
    uid, role = auth
    ok(f"Login admin OK (uid={uid}, role={role})")

    e1 = create_event("Charla AI", "Intro", datetime.now(UTC)+timedelta(days=1), "Charla", 5000, 10)
    e2 = create_event("Show Ayer", "Show", datetime.now(UTC)-timedelta(days=1), "Show", 0, 5)
    ok(f"Eventos creados E1={e1}, E2={e2}")

    all_events = list_events()
    ok(f"Listar eventos: {len(all_events)} encontrados")
    upcoming = list_events(status="upcoming")
    past = list_events(status="past")
    ok(f"Próximos={len(upcoming)} | Pasados={len(past)}")

    sell(e1, 3, uid)     # vendemos 3
    refund(e1, 1, uid)   # devolvemos 1
    ok("Venta 3 y devolución 1 en E1 OK")

    expect_error(sell, e1, 100, uid)     # no hay tantos cupos
    expect_error(refund, e1, 10, uid)    # no puedes devolver más de lo vendido
    expect_error(update_event, e1, seats_total=1)

    e3 = create_event("Taller Completo", "Capacidad 1", datetime.now(UTC)+timedelta(days=2), "Taller", 1000, 1)
    sell(e3, 1, uid)
    soldout = list_events(status="soldout")
    assert any(r[0] == e3 for r in soldout), "E3 no aparece como agotado"
    ok("Filtro 'soldout' OK")

    rep = report_summary()
    ok(f"Reporte: total={rep['total_events']}, suma_disp={rep['sum_available']}, agotados={len(rep['sold_out'])}")

    delete_event(e2)
    ok("Eliminar evento pasado (E2) OK")
    expect_error(delete_event, e2)

    ok("SMOKE TESTS COMPLETOS")

if __name__ == "__main__":
    main()
