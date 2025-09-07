import bcrypt
from datetime import datetime
from typing import Optional, List, Tuple
from db import get_conn

# ---------- Usuarios ----------
def create_user(username: str, password: str, role: str = "admin") -> int:
    if role not in ("admin", "viewer"):
        raise ValueError("Rol inválido")
    pwd = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()
    with get_conn() as c, c.cursor() as cur:
        cur.execute("SELECT 1 FROM users WHERE username=%s", (username,))
        if cur.fetchone():
            raise ValueError("Usuario ya existe")
        cur.execute(
            "INSERT INTO users(username,password_hash,role) VALUES(%s,%s,%s) RETURNING id",
            (username, pwd, role),
        )
        return cur.fetchone()[0]

def auth_user(username: str, password: str) -> Optional[Tuple[int,str]]:
    with get_conn() as c, c.cursor() as cur:
        cur.execute("SELECT id, password_hash, role FROM users WHERE username=%s", (username,))
        row = cur.fetchone()
        if not row: return None
        uid, ph, role = row
        if bcrypt.checkpw(password.encode(), ph.encode()):
            return uid, role
        return None

# ---------- Eventos ----------
def create_event(name: str, description: str, starts_at: datetime, category: str, price: int, seats_total: int) -> int:
    if price < 0 or seats_total < 0:
        raise ValueError("Valores no válidos")
    with get_conn() as c, c.cursor() as cur:
        cur.execute(
            """INSERT INTO events(name,description,starts_at,category,price,seats_total,seats_sold)
               VALUES(%s,%s,%s,%s,%s,%s,0) RETURNING id""",
            (name.strip(), description.strip(), starts_at, category, price, seats_total),
        )
        return cur.fetchone()[0]

def update_event(event_id: int, **fields) -> None:
    if "seats_total" in fields:
        new_total = int(fields["seats_total"])
        with get_conn() as c, c.cursor() as cur:
            cur.execute("SELECT seats_sold FROM events WHERE id=%s", (event_id,))
            row = cur.fetchone()
            if not row: raise ValueError("Evento no existe")
            if new_total < row[0]: raise ValueError("Cupos totales no pueden ser < vendidos")
    sets = ", ".join(f"{k}=%s" for k in fields.keys())
    vals = list(fields.values()) + [event_id]
    with get_conn() as c, c.cursor() as cur:
        cur.execute(f"UPDATE events SET {sets}, updated_at=now() WHERE id=%s", vals)

def delete_event(event_id: int) -> None:
    with get_conn() as c, c.cursor() as cur:
        cur.execute("DELETE FROM events WHERE id=%s", (event_id,))
        if cur.rowcount == 0: raise ValueError("Evento no existe")

# ---------- Ventas/Devoluciones ----------
def sell(event_id: int, qty: int, user_id: int) -> None:
    if qty <= 0: raise ValueError("Cantidad debe ser > 0")
    with get_conn() as c, c.cursor() as cur:
        cur.execute("SELECT seats_total, seats_sold FROM events WHERE id=%s FOR UPDATE", (event_id,))
        row = cur.fetchone()
        if not row: raise ValueError("Evento no existe")
        total, sold = row
        available = total - sold
        if available < qty: raise ValueError("No hay cupos suficientes")
        cur.execute("UPDATE events SET seats_sold = seats_sold + %s, updated_at=now() WHERE id=%s", (qty, event_id))
        cur.execute("INSERT INTO movements(event_id,type,qty,user_id) VALUES(%s,'SALE',%s,%s)",
                    (event_id, qty, user_id))

def refund(event_id: int, qty: int, user_id: int) -> None:
    if qty <= 0: raise ValueError("Cantidad debe ser > 0")
    with get_conn() as c, c.cursor() as cur:
        cur.execute("SELECT seats_sold FROM events WHERE id=%s FOR UPDATE", (event_id,))
        row = cur.fetchone()
        if not row: raise ValueError("Evento no existe")
        sold = row[0]
        if sold - qty < 0: raise ValueError("No se puede devolver más de lo vendido")
        cur.execute("UPDATE events SET seats_sold = seats_sold - %s, updated_at=now() WHERE id=%s", (qty, event_id))
        cur.execute("INSERT INTO movements(event_id,type,qty,user_id) VALUES(%s,'REFUND',%s,%s)",
                    (event_id, qty, user_id))

# ---------- Consulta y reporte ----------
def list_events(q: str = "", category: str = "", status: str = "", dt_from: datetime = None, dt_to: datetime = None) -> List[tuple]:
    clauses = []; params = []
    if q:         clauses += ["(name ILIKE %s OR description ILIKE %s)"]; params += [f"%{q}%", f"%{q}%"]
    if category:  clauses += ["category=%s"]; params += [category]
    if dt_from:   clauses += ["starts_at >= %s"]; params += [dt_from]
    if dt_to:     clauses += ["starts_at <= %s"]; params += [dt_to]
    if status == "soldout":
        clauses += ["(seats_total - seats_sold) = 0"]
    elif status == "upcoming":
        clauses += ["starts_at >= NOW()"]
    elif status == "past":
        clauses += ["starts_at < NOW()"]

    where = (" WHERE " + " AND ".join(clauses)) if clauses else ""
    sql = f"SELECT id,name,starts_at,category,price,seats_total,seats_sold FROM events{where} ORDER BY starts_at"
    with get_conn() as c, c.cursor() as cur:
        cur.execute(sql, params)
        rows = cur.fetchall()
    return rows

def report_summary() -> dict:
    with get_conn() as c, c.cursor() as cur:
        cur.execute("SELECT COUNT(*), COALESCE(SUM(seats_total - seats_sold),0) FROM events")
        total, sum_available = cur.fetchone()
        cur.execute("SELECT id,name FROM events WHERE (seats_total - seats_sold)=0")
        sold_out = cur.fetchall()
    return {"total_events": total, "sum_available": sum_available, "sold_out": sold_out}
