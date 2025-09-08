import bcrypt
from datetime import datetime
from typing import Optional, List, Tuple
from db import get_conn
from logger import log_user_operation, log_event_operation, log_sale_operation

# ---------- Usuarios ----------
def create_user(username: str, password: str, role: str = "admin") -> int:
    """
    Crea un nuevo usuario en el sistema.
    
    Args:
        username (str): Nombre de usuario único.
        password (str): Contraseña en texto plano.
        role (str, optional): Rol del usuario (admin o viewer). Defaults to "admin".
        
    Returns:
        int: ID del usuario creado.
        
    Raises:
        ValueError: Si el rol es inválido o el usuario ya existe.
    """
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
        user_id = cur.fetchone()[0]
        log_user_operation(user_id, username, "CREATE", f"role={role}")
        return user_id

def auth_user(username: str, password: str) -> Optional[Tuple[int,str]]:
    """
    Autentica un usuario con sus credenciales.
    
    Args:
        username (str): Nombre de usuario.
        password (str): Contraseña en texto plano.
        
    Returns:
        Optional[Tuple[int,str]]: Tupla con (user_id, role) si la autenticación es exitosa, None en caso contrario.
    """
    with get_conn() as c, c.cursor() as cur:
        cur.execute("SELECT id, password_hash, role FROM users WHERE username=%s", (username,))
        row = cur.fetchone()
        if not row: 
            log_user_operation(0, username, "AUTH_FAILED", "user_not_found")
            return None
        uid, ph, role = row
        if bcrypt.checkpw(password.encode(), ph.encode()):
            log_user_operation(uid, username, "AUTH_SUCCESS", f"role={role}")
            return uid, role
        log_user_operation(uid, username, "AUTH_FAILED", "invalid_password")
        return None

# ---------- Eventos ----------
def create_event(name: str, description: str, starts_at: datetime, category: str, price: int, seats_total: int) -> int:
    """
    Crea un nuevo evento en el sistema.
    
    Args:
        name (str): Nombre del evento.
        description (str): Descripción del evento.
        starts_at (datetime): Fecha y hora de inicio en UTC.
        category (str): Categoría del evento (Charla, Taller, Show, Otro).
        price (int): Precio de la entrada en CLP.
        seats_total (int): Total de cupos disponibles.
        
    Returns:
        int: ID del evento creado.
        
    Raises:
        ValueError: Si los valores son negativos.
    """
    if price < 0 or seats_total < 0:
        raise ValueError("Valores no válidos")
    with get_conn() as c, c.cursor() as cur:
        cur.execute(
            """INSERT INTO events(name,description,starts_at,category,price,seats_total,seats_sold)
               VALUES(%s,%s,%s,%s,%s,%s,0) RETURNING id""",
            (name.strip(), description.strip(), starts_at, category, price, seats_total),
        )
        event_id = cur.fetchone()[0]
        log_event_operation(event_id, "CREATE", f"name={name}, category={category}, price={price}, seats_total={seats_total}")
        return event_id

def update_event(event_id: int, **fields) -> None:
    """
    Actualiza los campos de un evento existente.
    
    Args:
        event_id (int): ID del evento a actualizar.
        **fields: Campos a actualizar (name, description, starts_at, category, price, seats_total).
        
    Raises:
        ValueError: Si el evento no existe o si seats_total es menor que seats_sold.
    """
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
        log_event_operation(event_id, "UPDATE", f"fields={list(fields.keys())}")

def delete_event(event_id: int) -> None:
    """
    Elimina un evento del sistema.
    
    Args:
        event_id (int): ID del evento a eliminar.
        
    Raises:
        ValueError: Si el evento no existe.
    """
    with get_conn() as c, c.cursor() as cur:
        cur.execute("DELETE FROM events WHERE id=%s", (event_id,))
        if cur.rowcount == 0: raise ValueError("Evento no existe")
        log_event_operation(event_id, "DELETE", "")

# ---------- Ventas/Devoluciones ----------
def sell(event_id: int, qty: int, user_id: int) -> None:
    """
    Vende entradas para un evento.
    
    Args:
        event_id (int): ID del evento.
        qty (int): Cantidad de entradas a vender.
        user_id (int): ID del usuario que realiza la venta.
        
    Raises:
        ValueError: Si la cantidad es inválida, el evento no existe o no hay cupos suficientes.
    """
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
        log_sale_operation(event_id, user_id, qty, "SALE")

def refund(event_id: int, qty: int, user_id: int) -> None:
    """
    Devuelve entradas de un evento.
    
    Args:
        event_id (int): ID del evento.
        qty (int): Cantidad de entradas a devolver.
        user_id (int): ID del usuario que realiza la devolución.
        
    Raises:
        ValueError: Si la cantidad es inválida, el evento no existe o se intenta devolver más de lo vendido.
    """
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
        log_sale_operation(event_id, user_id, qty, "REFUND")

# ---------- Consulta y reporte ----------
def list_events(q: str = "", category: str = "", status: str = "", dt_from: datetime = None, dt_to: datetime = None) -> List[tuple]:
    """
    Lista eventos con filtros opcionales.
    
    Args:
        q (str, optional): Palabra clave para buscar en nombre y descripción.
        category (str, optional): Filtrar por categoría.
        status (str, optional): Filtrar por estado (upcoming, past, soldout).
        dt_from (datetime, optional): Fecha de inicio del rango.
        dt_to (datetime, optional): Fecha de fin del rango.
        
    Returns:
        List[tuple]: Lista de tuplas con información de eventos.
    """
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

def get_event(event_id: int):
    """
    Obtiene la información completa de un evento.
    
    Args:
        event_id (int): ID del evento.
        
    Returns:
        tuple: Tupla con toda la información del evento o None si no existe.
    """
    with get_conn() as c, c.cursor() as cur:
        cur.execute(
            """
            SELECT id, name, description, starts_at, category, price, seats_total, seats_sold
            FROM events WHERE id=%s
            """,
            (event_id,)
        )
        row = cur.fetchone()
    return row

def report_summary() -> dict:
    """
    Genera un resumen estadístico del sistema.
    
    Returns:
        dict: Diccionario con estadísticas (total_events, sum_available, sold_out).
    """
    with get_conn() as c, c.cursor() as cur:
        cur.execute("SELECT COUNT(*), COALESCE(SUM(seats_total - seats_sold),0) FROM events")
        total, sum_available = cur.fetchone()
        cur.execute("SELECT id,name FROM events WHERE (seats_total - seats_sold)=0")
        sold_out = cur.fetchall()
    return {"total_events": total, "sum_available": sum_available, "sold_out": sold_out}
