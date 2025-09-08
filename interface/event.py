from validations import validate_non_empty, validate_price, validate_int, parse_local_datetime_to_utc, confirm_yes
from datetime import datetime, timezone
from entities import UserData
import os, sys
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from domain import create_event as d_create_event, list_events as d_list_events, update_event as d_update_event, delete_event as d_delete_event, get_event as d_get_event
from domain import sell as d_sell

# ---------- UI ----------
class EventManager:
    event_user_options = {
        1: {"name": "Listar eventos", "action": "list"},
        2: {"name": "Ver detalles de evento", "action": "details"},
        3: {"name": "Comprar entradas", "action": "buy"},
        0: {"name": "Volver", "action": "back"}
    }

    event_admin_options = {
        1: {"name": "Crear evento", "action": "create"},
        2: {"name": "Listar eventos", "action": "list"},
        3: {"name": "Ver detalles de evento", "action": "details"},
        4: {"name": "Actualizar evento", "action": "update"},
        5: {"name": "Eliminar evento", "action": "delete"},
        0: {"name": "Volver", "action": "back"}
    }

    def __init__(self):
        self._events = []
        self._id_counter = 1
        self._current_user: UserData | None = None

    def _event_select(self, action: str):
        match action:
            case "create":
                return self._create_event()
            case "list":
                return self._list_events()
            case "update":
                return self._update_event()
            case "delete":
                return self._delete_event()
            case "details":
                return self._show_details()
            case "buy":
                return self._buy_tickets()
            case "back":
                return None
            case _:
                print("Acción no reconocida.")

    def event_menu(self, user: UserData):
        while True:
            if not user:
                print("Debe iniciar sesión para gestionar eventos.")
                return
            self._current_user = user
            print("\n--- Menú de Eventos ---")
            event_options = self.event_admin_options if user.role == "admin" else self.event_user_options
            for key, value in event_options.items():
                print(f"{key}. {value['name']}")
            choice = input("Seleccione una opción: ")
            if not (choice.isdigit() and int(choice) in event_options):
                print("Opción no válida.")
                continue
            action = event_options[int(choice)]["action"]
            result = self._event_select(action)
            if action == "back":
                break

    def _create_event(self):
        print("Crear evento")
        name = validate_non_empty(input("Nombre: ") or "")
        if not name:
            print("Nombre obligatorio.")
            return
        description = input("Descripción: ") or ""
        start_utc = parse_local_datetime_to_utc(
            input("Fecha y hora (DD-MM-YYYY o DD-MM-YYYY HH:MM): ") or "")
        if not start_utc:
            print("Fecha inválida. Use DD-MM-YYYY o DD-MM-YYYY HH:MM")
            return
        category = (input("Categoría (Charla/Taller/Show/Otro): ") or "").strip()
        # Normalizar categoría con capitalización como en BD
        valid_cats = {"charla": "Charla", "taller": "Taller", "show": "Show", "otro": "Otro"}
        cat_key = category.lower()
        if cat_key not in valid_cats:
            print("Categoría inválida. Use: Charla/Taller/Show/Otro")
            return
        category = valid_cats[cat_key]
        price = validate_price(input("Precio (entero): ") or "")
        if price is None:
            print("Precio inválido.")
            return
        try:
            price_int = int(price)
        except Exception:
            print("Precio debe ser entero.")
            return
        total_capacity = validate_int(input("Cupos totales: ") or "")
        if total_capacity is None:
            print("Cupos inválidos.")
            return
        try:
            new_id = d_create_event(name, description, start_utc, category, price_int, total_capacity)
            print(f"Evento creado con ID: {new_id}")
        except Exception as e:
            print(f"Error creando evento: {e}")

    def _apply_filters(self, events, keyword: str, category: str, date_from, date_to, state: str):
        now = datetime.now(timezone.utc)
        filtered_events = []
        for event in events:
            start = datetime.fromisoformat(
                event["start_utc"]).astimezone(timezone.utc)
            if keyword and keyword not in event["name"].lower() and keyword not in event["description"].lower():
                continue
            if category and category != event["category"].lower():
                continue
            if date_from and start < date_from:
                continue
            if date_to and start > date_to:
                continue
            if state:
                if state == "proximos" and start <= now:
                    continue
                if state == "pasados" and start > now:
                    continue
                if state == "agotados" and event.get("available", 0) > 0:
                    continue
            filtered_events.append(event)
        return filtered_events

    def _list_events(self):
        print("Listar eventos")
        keyword = (input("Filtro palabra clave (enter para omitir): ") or "")
        category = (input("Filtro categoría (Charla/Taller/Show/Otro, enter para omitir): ") or "").strip()
        if category:
            valid_cats = {"charla": "Charla", "taller": "Taller", "show": "Show", "otro": "Otro"}
            category = valid_cats.get(category.lower(), "")
            if not category:
                print("Categoría inválida. Ignorando filtro.")
        date_from = input("Fecha desde (DD-MM-YYYY, enter para omitir): ") or ""
        date_to = input("Fecha hasta (DD-MM-YYYY, enter para omitir): ") or ""
        date_from = parse_local_datetime_to_utc(date_from) if date_from else None
        date_to = parse_local_datetime_to_utc(date_to) if date_to else None
        state = (input("Estado (proximos/pasados/agotados, enter para omitir): ") or "").lower()
        status = {"proximos": "upcoming", "pasados": "past", "agotados": "soldout"}.get(state, "")
        try:
            rows = d_list_events(q=keyword, category=category, status=status, dt_from=date_from, dt_to=date_to)
        except Exception as e:
            print(f"Error listando eventos: {e}")
            return
        if not rows:
            print("No se encontraron eventos.")
            return
        for r in rows:
            eid, name, starts_at, cat, price, seats_total, seats_sold = r
            available = seats_total - seats_sold
            start_local = starts_at.astimezone()
            print(f"ID: {eid} | {name} | {start_local.strftime('%d-%m-%Y %H:%M %Z')} | Cat: {cat} | Precio: {price} | Disponibles: {available}/{seats_total}")

    def _show_details(self):
        try:
            eid = int(input("ID del evento: ").strip())
            row = d_get_event(eid)
            if not row:
                print("Evento no encontrado.")
                return
            eid, name, description, starts_at, cat, price, seats_total, seats_sold = row
            available = seats_total - seats_sold
            start_local = starts_at.astimezone()
            print("\n--- Detalle de evento ---")
            print(f"ID: {eid}")
            print(f"Nombre: {name}")
            print(f"Descripción: {description or '-'}")
            print(f"Fecha: {start_local.strftime('%d-%m-%Y %H:%M %Z')}")
            print(f"Categoría: {cat}")
            print(f"Precio: {price}")
            print(f"Disponibles: {available}/{seats_total}")
        except Exception as e:
            print(f"Error obteniendo detalles: {e}")

    def _buy_tickets(self):
        try:
            eid = int(input("ID del evento: ").strip())
            qty = int(input("Cantidad a comprar: ").strip())
            if not self._current_user:
                print("No hay usuario en sesión.")
                return
            d_sell(eid, qty, self._current_user.id)
            print("Compra registrada.")
        except Exception as e:
            print(f"Error comprando entradas: {e}")


    def _update_event(self):
        print("Actualizar evento")
        try:
            event_id = int(input("ID del evento a actualizar: ").strip())
            fields = {}
            name = input("Nombre (enter para mantener): ").strip()
            if name:
                fields["name"] = name
            description = input("Descripción (enter para mantener): ").strip()
            if description:
                fields["description"] = description
            date_str = input("Fecha y hora (DD-MM-YYYY o DD-MM-YYYY HH:MM) (enter para mantener): ").strip()
            if date_str:
                start_utc = parse_local_datetime_to_utc(date_str)
                if start_utc:
                    fields["starts_at"] = start_utc
                else:
                    print("Fecha inválida; ignorando cambio de fecha.")
            category = input("Categoría (Charla/Taller/Show/Otro) (enter para mantener): ").strip()
            if category:
                valid_cats = {"charla": "Charla", "taller": "Taller", "show": "Show", "otro": "Otro"}
                cat = valid_cats.get(category.lower())
                if not cat:
                    print("Categoría inválida; ignorando cambio.")
                else:
                    fields["category"] = cat
            price = input("Precio entero (enter para mantener): ").strip()
            if price:
                p = validate_price(price)
                if p is None:
                    print("Precio inválido; ignorando cambio.")
                else:
                    try:
                        fields["price"] = int(p)
                    except Exception:
                        print("Precio debe ser entero; ignorando cambio.")
            cap = input("Cupos totales (enter para mantener): ").strip()
            if cap:
                cap_v = validate_int(cap)
                if cap_v is None:
                    print("Cupos inválidos; ignorando cambio.")
                else:
                    fields["seats_total"] = cap_v
            if not fields:
                print("Sin cambios.")
                return
            d_update_event(event_id, **fields)
            print("Evento actualizado.")
        except Exception as e:
            print(f"Error actualizando evento: {e}")


    def _delete_event(self):
        print("Eliminar evento")
        try:
            event_id = int(input("ID del evento a eliminar: ").strip())
            if confirm_yes(input("¿Confirma eliminación? (s/N): ")):
                d_delete_event(event_id)
                print("Evento eliminado.")
            else:
                print("Eliminación cancelada.")
        except Exception as e:
            print(f"Error eliminando evento: {e}")

EVENT_MANAGER = EventManager()