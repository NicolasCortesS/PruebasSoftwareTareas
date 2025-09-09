from datetime import datetime, timedelta, UTC, timezone
from domain import (
    auth_user, create_event, update_event, delete_event,
    sell, refund, list_events, report_summary, create_user
)
from domain import get_event
from db import get_conn
import bcrypt
import threading
import builtins
from contextlib import contextmanager
from io import StringIO
import sys

def ok(msg): 
    """Imprime un mensaje de éxito."""
    print(msg)

def fail(msg): 
    """Imprime un mensaje de fallo."""
    print(msg)

def expect_error(fn, *args, **kwargs):
    """
    Verifica que una función lance una excepción.
    
    Args:
        fn: Función a ejecutar.
        *args: Argumentos posicionales para la función.
        **kwargs: Argumentos con nombre para la función.
    """
    try:
        fn(*args, **kwargs)
        fail(f"Se esperaba error en {fn.__name__}")
    except Exception as e:
        ok(f"Error esperado en {fn.__name__}: {e}")

def main():
    """
    Función principal que ejecuta todos los tests del sistema.
    Incluye tests de backend, frontend y cleanup.
    """
    # Contadores de tests
    tests_passed = 0
    tests_failed = 0
    
    print("=" * 60)
    print("TEST BACKENDS")
    print("=" * 60)
    
    # Backend tests
    # -------------------- Helpers --------------------
    def print_case(idt, esperado, obtenido, exito):
        nonlocal tests_passed, tests_failed
        status = "Éxito" if exito else "Fallo"
        print(f"\nId_Test: {idt}")
        print(f"Resultado Esperado: {esperado}")
        print(f"Resultado Obtenido: {obtenido}")
        print(f"Fallo o éxito: {status}")
        
        # Incrementar contadores
        if exito:
            tests_passed += 1
        else:
            tests_failed += 1

    # -------------------- B1-01 --------------------
    try:
        auth = auth_user("admin", "admin123")
        if not auth:
            print_case("B1-01", "Login admin exitoso", "Login falló", False)
            return
        uid, role = auth
        exito = (uid is not None and role == "admin")
        print_case("B1-01", "Login admin exitoso", f"uid={uid}, role={role}", exito)
    except Exception as e:
        print_case("B1-01", "Login admin exitoso", f"Error: {e}", False)

    # -------------------- B2-01 --------------------
    try:
        e1 = create_event("Charla AI", "Intro", datetime.now(UTC)+timedelta(days=1), "Charla", 5000, 10)
        e2 = create_event("Show Ayer", "Show", datetime.now(UTC)-timedelta(days=1), "Show", 0, 5)
        exito = (e1 is not None and e2 is not None)
        print_case("B2-01", "Creación de eventos", f"E1={e1}, E2={e2}", exito)
    except Exception as e:
        print_case("B2-01", "Creación de eventos", f"Error: {e}", False)

    # -------------------- B3-01 --------------------
    try:
        all_events = list_events()
        upcoming = list_events(status="upcoming")
        past = list_events(status="past")
        exito = (len(all_events) >= 2 and len(upcoming) >= 1 and len(past) >= 1)
        print_case("B3-01", "Listado de eventos con filtros", f"Total={len(all_events)}, Próximos={len(upcoming)}, Pasados={len(past)}", exito)
    except Exception as e:
        print_case("B3-01", "Listado de eventos con filtros", f"Error: {e}", False)

    # -------------------- B4-01 --------------------
    try:
        sell(e1, 3, uid)
        refund(e1, 1, uid)
        row = get_event(e1)
        exito = (row[7] == 2)
        print_case("B4-01", "Venta y devolución de entradas", f"seats_sold={row[7]}", exito)
    except Exception as e:
        print_case("B4-01", "Venta y devolución de entradas", f"Error: {e}", False)

    # -------------------- B5-01 --------------------
    try:
        error1 = error2 = error3 = False
        try:
            sell(e1, 100, uid)
        except Exception:
            error1 = True
        try:
            refund(e1, 10, uid)
        except Exception:
            error2 = True
        try:
            update_event(e1, seats_total=1)
        except Exception:
            error3 = True
        exito = (error1 and error2 and error3)
        print_case("B5-01", "Validaciones de negocio", f"sobreventa={error1}, sobredevolución={error2}, cupos_insuficientes={error3}", exito)
    except Exception as e:
        print_case("B5-01", "Validaciones de negocio", f"Error: {e}", False)

    # -------------------- B6-01 --------------------
    try:
        e3 = create_event("Taller Completo", "Capacidad 1", datetime.now(UTC)+timedelta(days=2), "Taller", 1000, 1)
        sell(e3, 1, uid)
        soldout = list_events(status="soldout")
        exito = any(r[0] == e3 for r in soldout)
        print_case("B6-01", "Filtro de eventos agotados", f"E3 en soldout={exito}", exito)
    except Exception as e:
        print_case("B6-01", "Filtro de eventos agotados", f"Error: {e}", False)

    # -------------------- B7-01 --------------------
    try:
        rep = report_summary()
        exito = isinstance(rep, dict) and "total_events" in rep and "sum_available" in rep and "sold_out" in rep
        print_case("B7-01", "Generación de reporte", f"rep={rep}", exito)
    except Exception as e:
        print_case("B7-01", "Generación de reporte", f"Error: {e}", False)

    # -------------------- B8-01 --------------------
    try:
        delete_event(e2)
        exists = any(r[0] == e2 for r in list_events())
        error_on_delete = False
        try:
            delete_event(e2)
        except Exception:
            error_on_delete = True
        exito = (not exists and error_on_delete)
        print_case("B8-01", "Eliminación de eventos", f"existe={exists}, error_eliminar_inexistente={error_on_delete}", exito)
    except Exception as e:
        print_case("B8-01", "Eliminación de eventos", f"Error: {e}", False)

    # -------------------- BACKEND CLEANUP --------------------
    print("\n" + "=" * 60)
    print("BACKEND CLEANUP - Eliminando datos de prueba")
    print("=" * 60)
    
    try:
        with get_conn() as c, c.cursor() as cur:
            cur.execute("DELETE FROM events WHERE name IN ('Charla AI', 'Show Ayer', 'Taller Completo')")
            deleted_events = cur.rowcount
            print(f"Eventos de backend eliminados: {deleted_events}")
    except Exception as e:
        print(f"Error en backend cleanup: {e}")

    print("\n" + "=" * 60)
    print("TEST FRONTEND")
    print("=" * 60)
    
    # Frontend tests
    # -------------------- Helpers --------------------
    @contextmanager
    def mock_io(inputs):
        old_input = builtins.input
        old_stdout = sys.stdout
        sio = StringIO()
        it = iter(inputs)
        builtins.input = lambda prompt='': next(it)
        sys.stdout = sio
        try:
            yield sio
        finally:
            builtins.input = old_input
            sys.stdout = old_stdout

    # -------------------- R1-01 --------------------
    try:
        from interface.event import EventManager
        em = EventManager()
        fecha = "01-01-2026"
        with mock_io([
            "Evento A", "Desc...", fecha, "Charla", "10", "100"
        ]):
            em._create_event()
        rows = list_events(q="Evento A")
        created = [r for r in rows if r[1] == "Evento A"]
        assert created, "No se encontró Evento A"
        eid = created[-1][0]
        row = get_event(eid)
        starts_at = row[3]
        obtenido = f"Creado ID={eid}, starts_at tzinfo={starts_at.tzinfo}"
        exito = (starts_at.tzinfo is not None) and (starts_at.astimezone(timezone.utc).tzinfo is not None)
        print_case("R1-01", "Evento creado y fecha en UTC", obtenido, exito)
    except Exception as e:
        print_case("R1-01", "Evento creado y fecha en UTC", f"Error: {e}", False)

    # -------------------- R2-01 --------------------
    try:
        e_ok = create_event("ai meetup", "x", datetime(2026,1,10,12,0, tzinfo=UTC), "Charla", 0, 5)
        create_event("no match", "x", datetime(2026,2,10,12,0, tzinfo=UTC), "Show", 0, 5)
        res = list_events(q="ai", category="Charla",
                          status="upcoming",
                          dt_from=datetime(2026,1,1,0,0, tzinfo=UTC),
                          dt_to=datetime(2026,1,31,23,59, tzinfo=UTC))
        ids = [r[0] for r in res]
        exito = e_ok in ids and all(r[3]=="Charla" for r in res)
        print_case("R2-01", "Solo eventos que cumplen todos los filtros", f"Retornados={ids}", exito)
    except Exception as e:
        print_case("R2-01", "Solo eventos que cumplen todos los filtros", f"Error: {e}", False)

    # -------------------- R3-01 --------------------
    try:
        e = create_event("Update me", "x", datetime.now(UTC)+timedelta(days=2), "Show", 100, 10)
        update_event(e, name="Nuevo", price=20)
        row = get_event(e)
        exito = (row[1]=="Nuevo" and row[5]==20)
        print_case("R3-01", "Campos actualizados reflejados", f"name={row[1]}, price={row[5]}", exito)
    except Exception as e:
        print_case("R3-01", "Campos actualizados reflejados", f"Error: {e}", False)

    # -------------------- R4-01 --------------------
    try:
        from interface.event import EventManager
        em_local = EventManager()
        e = create_event("Borrar", "x", datetime.now(UTC)+timedelta(days=3), "Otro", 0, 1)
        with mock_io([str(e), "s"]):
            em_local._delete_event()
        ids = [r[0] for r in list_events()]
        exito = e not in ids
        print_case("R4-01", "Eliminado tras confirmación", f"Existe={e in ids}", exito)
    except Exception as e:
        print_case("R4-01", "Eliminado tras confirmación", f"Error: {e}", False)

    # -------------------- R5-01 --------------------
    try:
        import time
        uid = create_user(f"r5user_{int(time.time())}","pw","admin")
        e = create_event("Ventas", "x", datetime.now(UTC)+timedelta(days=1), "Taller", 100, 10)
        sell(e, 3, uid)
        row = get_event(e)
        with get_conn() as c, c.cursor() as cur:
            cur.execute("SELECT type,qty,user_id FROM movements WHERE event_id=%s ORDER BY id DESC", (e,))
            mv = cur.fetchone()
        exito = (row[6]==10 and row[7]==3 and mv[0]=="SALE" and mv[1]==3 and mv[2]==uid)
        print_case("R5-01", "seats_sold+=3 y movimiento SALE", f"sold={row[7]}, mv={mv}", exito)
    except Exception as e:
        print_case("R5-01", "seats_sold+=3 y movimiento SALE", f"Error: {e}", False)

    # -------------------- R5.1-01 --------------------
    try:
        sell(e, 1, uid)
        with get_conn() as c, c.cursor() as cur:
            cur.execute("SELECT user_id FROM movements WHERE event_id=%s ORDER BY id DESC", (e,))
            mv_uid = cur.fetchone()[0]
        try:
            sell(e, 1, 0)
            unauth_failed = False
        except Exception:
            unauth_failed = True
        exito = (mv_uid == uid and unauth_failed)
        print_case("R5.1-01", "Venta registra user_id y sin auth falla", f"last_user_id={mv_uid}, unauth_failed={unauth_failed}", exito)
    except Exception as ex:
        print_case("R5.1-01", "Venta registra user_id y sin auth falla", f"Error: {ex}", False)

    # -------------------- R6-01 --------------------
    try:
        prev = get_event(e)[7]
        refund(e, 1, uid)
        now_sold = get_event(e)[7]
        with get_conn() as c, c.cursor() as cur:
            cur.execute("SELECT type,qty FROM movements WHERE event_id=%s ORDER BY id DESC", (e,))
            mv = cur.fetchone()
        exito = (now_sold == prev-1 and mv[0]=="REFUND" and mv[1]==1)
        print_case("R6-01", "seats_sold-=1 y movimiento REFUND", f"sold={now_sold}, mv={mv}", exito)
    except Exception as ex:
        print_case("R6-01", "seats_sold-=1 y movimiento REFUND", f"Error: {ex}", False)

    # -------------------- R7-01 --------------------
    try:
        rep = report_summary()
        exito = isinstance(rep, dict) and {"total_events","sum_available","sold_out"} <= set(rep.keys())
        print_case("R7-01", "Resumen contiene métricas y agotados", f"rep={rep}", exito)
    except Exception as e:
        print_case("R7-01", "Resumen contiene métricas y agotados", f"Error: {e}", False)

    # -------------------- R8-01 --------------------
    try:
        e = create_event("OversellTest", "x", datetime.now(UTC)+timedelta(days=1), "Show", 0, 1)
        uid2 = create_user(f"r8user_{int(time.time())}","pw","admin")
        before = get_event(e)[7]
        ok1 = ok2 = False
        try:
            sell(e, 2, uid2)
        except Exception:
            ok1 = True
        try:
            refund(e, 1, uid2)
        except Exception:
            ok2 = True
        after = get_event(e)[7]
        exito = ok1 and ok2 and before == after
        print_case("R8-01", "Excepciones en sobreventa y sobre-devolución", f"sold_before={before}, sold_after={after}", exito)
    except Exception as e:
        print_case("R8-01", "Excepciones en sobreventa y sobre-devolución", f"Error: {e}", False)

    # -------------------- R9-01 --------------------
    try:
        from interface.event import EventManager
        em_local = EventManager()
        e = create_event("ConfirmDel", "x", datetime.now(UTC)+timedelta(days=1), "Otro", 0, 1)
        with mock_io([str(e), "n"]):
            em_local._delete_event()
        exists1 = any(r[0]==e for r in list_events())
        with mock_io([str(e), "s"]):
            em_local._delete_event()
        exists2 = any(r[0]==e for r in list_events())
        exito = (exists1 and not exists2)
        print_case("R9-01", "Cancelar luego confirmar eliminación", f"existe_tras_n={exists1}, existe_tras_s={exists2}", exito)
    except Exception as e:
        print_case("R9-01", "Cancelar luego confirmar eliminación", f"Error: {e}", False)

    # -------------------- R10-01 --------------------
    try:
        u = f"r10user_{int(time.time())}"
        uid = create_user(u, "pw", "viewer")
        good = auth_user(u, "pw")
        bad = auth_user(u, "bad")
        exito = (good and good[0]==uid and good[1]=="viewer" and bad is None)
        print_case("R10-01", "Auth ok/None según credenciales", f"good={good}, bad={bad}", exito)
    except Exception as e:
        print_case("R10-01", "Auth ok/None según credenciales", f"Error: {e}", False)

    # -------------------- R11-01 --------------------
    try:
        u = f"r11user_{int(time.time())}"
        create_user(u, "pw", "viewer")
        with get_conn() as c, c.cursor() as cur:
            cur.execute("SELECT password_hash FROM users WHERE username=%s", (u,))
            ph = cur.fetchone()[0]
        exito = bcrypt.checkpw(b"pw", ph.encode())
        print_case("R11-01", "Contraseña almacenada como hash válido", f"checkpw={exito}", exito)
    except Exception as e:
        print_case("R11-01", "Contraseña almacenada como hash válido", f"Error: {e}", False)

    # -------------------- R12-01 --------------------
    try:
        from interface.user import UserManager
        um = UserManager()
        admin_opts = set(v["action"] for v in um.admin_options.values())
        user_opts = set(v["action"] for v in um.user_options.values())
        exito = ("manage_sales" in admin_opts and "manage_sales" not in user_opts)
        print_case("R12-01", "Permisos UI por rol (ventas solo admin)", f"admin={admin_opts}, user={user_opts}", exito)
    except Exception as e:
        print_case("R12-01", "Permisos UI por rol (ventas solo admin)", f"Error: {e}", False)

    # -------------------- R13-01 --------------------
    try:
        import os
        log_file = "logs/operations.log"
        exito = os.path.exists(log_file) and os.path.getsize(log_file) > 0
        if exito:
            with open(log_file, 'r', encoding='utf-8') as f:
                content = f.read()
                has_operations = any(op in content for op in ["USER_CREATE", "EVENT_CREATE", "SALE_SALE", "SALE_REFUND"])
                exito = exito and has_operations
        print_case("R13-01", "Archivo de log con operaciones", f"file_exists={os.path.exists(log_file)}, has_operations={exito}", exito)
    except Exception as e:
        print_case("R13-01", "Archivo de log con operaciones", f"Error: {e}", False)

    # -------------------- R14-01 --------------------
    try:
        from interface.event import EventManager
        em_local = EventManager()
        with mock_io(["Test Event", "Desc", "01-01-2026", "Charla", "-10", "100"]) as sio:
            em_local._create_event()
            out = sio.getvalue()
        precio_error = ("Precio inválido" in out or "Precio debe ser entero" in out)
        no_traceback = "Traceback" not in out
        exito = (precio_error and no_traceback)
        print_case("R14-01", "Mensajes legibles sin stacktrace", f"precio_error={precio_error}, no_traceback={no_traceback}, out={out[:200]}...", exito)
    except Exception as e:
        print_case("R14-01", "Mensajes legibles sin stacktrace", f"Error: {e}", False)

    # -------------------- R15-01 --------------------
    try:
        e = create_event("Race", "x", datetime.now(UTC)+timedelta(days=1), "Show", 0, 1)
        uid = create_user(f"r15_{int(time.time())}","pw","admin")
        results = []
        def t():
            try:
                sell(e, 1, uid)
                results.append("ok")
            except Exception:
                results.append("err")
        th1 = threading.Thread(target=t)
        th2 = threading.Thread(target=t)
        th1.start(); th2.start(); th1.join(); th2.join()
        sold = get_event(e)[7]
        exito = (results.count("ok")==1 and results.count("err")==1 and sold==1)
        print_case("R15-01", "Sin sobreventa con concurrencia", f"threads={results}, sold={sold}", exito)
    except Exception as e:
        print_case("R15-01", "Sin sobreventa con concurrencia", f"Error: {e}", False)

    # -------------------- R16-01 --------------------
    try:
        e = create_event("UTCtest", "x", datetime.now(UTC)+timedelta(days=1), "Charla", 0, 1)
        row = get_event(e)
        dt = row[3]
        exito = (dt.tzinfo is not None)
        print_case("R16-01", "BD almacena TIMESTAMPTZ (UTC); UI muestra local", f"tzinfo={dt.tzinfo}", exito)
    except Exception as e:
        print_case("R16-01", "BD almacena TIMESTAMPTZ (UTC); UI muestra local", f"Error: {e}", False)

    # -------------------- CLEANUP --------------------
    print("\n" + "=" * 60)
    print("CLEANUP - Eliminando datos de prueba")
    print("=" * 60)
    
    try:
        with get_conn() as c, c.cursor() as cur:
            cur.execute("""
                DELETE FROM movements 
                WHERE user_id IN (
                    SELECT id FROM users 
                    WHERE username LIKE 'r%user_%' OR username LIKE 'r%_%'
                )
            """)
            deleted_movements = cur.rowcount
            print(f"Movimientos de prueba eliminados: {deleted_movements}")
            
            cur.execute("DELETE FROM users WHERE username LIKE 'r%user_%' OR username LIKE 'r%_%'")
            deleted_users = cur.rowcount
            print(f"Usuarios de prueba eliminados: {deleted_users}")
    except Exception as e:
        print(f"Error en cleanup: {e}")

    # -------------------- RESUMEN FINAL --------------------
    print("\n" + "=" * 60)
    print("RESUMEN FINAL DE TESTS")
    print("=" * 60)
    total_tests = tests_passed + tests_failed
    success_rate = (tests_passed / total_tests * 100) if total_tests > 0 else 0
    
    print(f"Total de tests ejecutados: {total_tests}")
    print(f"Tests que pasaron: {tests_passed}")
    print(f"Tests que fallaron: {tests_failed}")
    print(f"Tasa de éxito: {success_rate:.1f}%")
    
    if tests_failed == 0:
        print("\nTodos los tests pasaron")
    else:
        print(f"\n{tests_failed} test(s) fallaron.")

if __name__ == "__main__":
    main()
