from interface.validations import validate_non_empty, validate_price, validate_int, parse_local_datetime_to_utc, confirm_yes
from datetime import datetime, timezone
from interface.entities import UserData
import domain

class EventManager:
    event_viewer_options = {
        1: {"name": "Listar eventos", "action": "list"},
        0: {"name": "Volver", "action": "back"}
    }

    event_admin_options = {
        1: {"name": "Crear evento", "action": "create"},
        2: {"name": "Listar eventos", "action": "list"},
        3: {"name": "Actualizar evento", "action": "update"},
        4: {"name": "Eliminar evento", "action": "delete"},
        0: {"name": "Volver", "action": "back"}
    }

    def __init__(self):
        self._events = []
        self._id_counter = 1

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
            case "back":
                return None
            case _:
                print("Acción no reconocida en events.")

    def event_menu(self, user: UserData):
        while True:
            if not user:
                print("Debe iniciar sesión para gestionar eventos.")
                return
            print("\n--- Menú de Eventos ---")
            event_options = self.event_admin_options if user.role == "admin" else self.event_viewer_options
            for key, value in event_options.items():
                print(f"{key}. {value['name']}")
            choice = input("Seleccione una opción: ")
            if not (choice.isdigit() and int(choice) in event_options):
                print("Opción no válida.")
                continue
            action = event_options[int(choice)]["action"]
            self._event_select(action)
            if action == "back":
                return

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
        category = input("Categoría: ") or ""
        price = validate_price(input("Precio: ") or "")
        if price is None:
            print("Precio inválido.")
            return
        total_capacity = validate_int(input("Cupos totales: ") or "")
        if total_capacity is None:
            print("Cupos inválidos.")
            return
        try:
            eid = domain.create_event(name=name, description=description, starts_at=start_utc, category=category, price=int(price), seats_total=total_capacity)
            print(f"Evento creado con ID: {eid}")
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

        keyword = (input("Filtro palabra clave (enter para omitir): ") or "").lower()
        category = (input("Filtro categoría (enter para omitir): ") or "").lower()
        date_from = input("Fecha desde (DD-MM-YYYY, enter para omitir): ") or ""
        date_to = input("Fecha hasta (DD-MM-YYYY, enter para omitir): ") or ""
        date_from = parse_local_datetime_to_utc(date_from) if date_from else None
        date_to = parse_local_datetime_to_utc(date_to) if date_to else None
        state = (
            input("Estado (proximos/pasados/agotados, enter para omitir): ") or "").lower()
        status = ""
        if state == "proximos":
            status = "upcoming"
        elif state == "pasados":
            status = "past"
        elif state == "agotados":
            status = "soldout"

        try:
            rows = domain.list_events(q=keyword or "", category=category or "", status=status, dt_from=date_from, dt_to=date_to)
        except Exception as e:
            print(f"Error consultando eventos: {e}")
            return

        if not rows:
            print("No se encontraron eventos.")
            return

        for row in rows:
            eid, name, description, starts_at, category, price, seats_total, seats_sold = row
            available = seats_total - seats_sold
            start_local = starts_at.astimezone()
            print(f"ID: {eid} | {name} | {start_local.strftime('%d-%m-%Y %H:%M %Z')} | Cat: {category} | Precio: {price} | Disponibles: {available}/{seats_total}")
            if description:
                print(f"  Descripción: {description}")


    def _update_event(self):
        print("Actualizar evento")
        try:
            event_id = int(input("ID del evento a actualizar: ").strip())
            try:
                row = domain.get_event_by_id(event_id)
            except Exception as e:
                print(f"Error consultando eventos: {e}")
                return
            if not row:
                print("Evento no encontrado.")
                return

            _, cur_name, cur_description, cur_starts_at, cur_category, cur_price, cur_seats_total, cur_seats_sold = row
            cur_available = cur_seats_total - cur_seats_sold

            summary = (
                f"ID:{event_id} | Nombre:{cur_name} | Descripción:{cur_description} | "
                f"Fecha:{cur_starts_at.astimezone().strftime('%d-%m-%Y %H:%M %Z')} | Cat:{cur_category} | "
                f"Precio:{cur_price} | Total:{cur_seats_total} | Vendidos:{cur_seats_sold} | Disponibles:{cur_available}"
            )
            print("\nEvento actual: " + summary + "\n")

            name = input(f"Nombre (enter para mantener) [{cur_name}]: ").strip()
            description = input(f"Descripción (enter para mantener) [{cur_description}]: ").strip()
            date_str = input(f"Fecha y hora (DD-MM-YYYY o DD-MM-YYYY HH:MM) (enter para mantener) [{cur_starts_at.astimezone().strftime('%d-%m-%Y %H:%M')}]: ").strip()
            category = input(f"Categoría (enter para mantener) [{cur_category}]: ").strip()
            price = input(f"Precio (enter para mantener) [{cur_price}]: ").strip()
            cap = input(f"Cupos totales (enter para mantener) [{cur_seats_total}]: ").strip()

            fields = {}
            if name:
                fields['name'] = name
            if description:
                fields['description'] = description
            if date_str:
                start_utc = parse_local_datetime_to_utc(date_str)
                if not start_utc:
                    print("Fecha inválida.")
                    return
                fields['starts_at'] = start_utc
            if category:
                fields['category'] = category
            if price:
                pv = validate_price(price)
                if pv is None:
                    print("Precio inválido.")
                    return
                fields['price'] = int(pv)
            if cap:
                cv = validate_int(cap)
                if cv is None:
                    print("Cupos inválidos.")
                    return
                fields['seats_total'] = cv

            if not fields:
                print("No hay cambios.")
                return

            try:
                domain.update_event(event_id, **fields)
                print("Evento actualizado.")
            except Exception as e:
                print(f"Error actualizando evento: {e}")
        except Exception as e:
            print(f"Error actualizando evento: {e}")


    def _delete_event(self):
        print("Eliminar evento")
        try:
            event_id = int(input("ID del evento a eliminar: ").strip())
            try:
                row = domain.get_event_by_id(event_id)
            except Exception as e:
                print(f"Error consultando eventos: {e}")
                return
            if not row:
                print("Evento no encontrado.")
                return
            eid, name, description, starts_at, category, price, seats_total, seats_sold = row
            available = seats_total - seats_sold
            start_local = starts_at.astimezone()
            print(f"Evento: {eid} - {name} | {start_local.strftime('%d-%m-%Y %H:%M %Z')} | Disponibles: {available}/{seats_total}")
            if description:
                print(f"  Descripción: {description}")
            if confirm_yes(input("¿Confirma eliminación? (s/N): ")):
                try:
                    domain.delete_event(event_id)
                    print("Evento eliminado.")
                except Exception as e:
                    print(f"Error eliminando evento: {e}")
            else:
                print("Eliminación cancelada.")
        except Exception as e:
            print(f"Error eliminando evento: {e}")

EVENT_MANAGER = EventManager()