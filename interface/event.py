from validations import validate_non_empty, validate_price, validate_int, parse_local_datetime_to_utc, confirm_yes
from datetime import datetime, timezone
from entities import UserData

class EventManager:
    event_user_options = {
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
        category = input("Categoría: ") or ""
        price = validate_price(input("Precio: ") or "")
        if price is None:
            print("Precio inválido.")
            return
        total_capacity = validate_int(input("Cupos totales: ") or "")
        if total_capacity is None:
            print("Cupos inválidos.")
            return

        # Aca iría la logica de pasar datos al backend
        event = {
            "id": self._id_counter,
            "name": name,
            "description": description,
            "start_utc": start_utc.isoformat(),
            "category": category,
            "price": price,
            "total_capacity": total_capacity,
            "available": total_capacity,
        }
        self._events.append(event)
        self._id_counter += 1
        print(f"Evento creado con ID: {event['id']}")

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
        # Acá se debería verificar si es que hay eventos

        keyword = (input("Filtro palabra clave (enter para omitir): ") or "").lower()
        category = (input("Filtro categoría (enter para omitir): ") or "").lower()
        date_from = input("Fecha desde (DD-MM-YYYY, enter para omitir): ") or ""
        date_to = input("Fecha hasta (DD-MM-YYYY, enter para omitir): ") or ""
        date_from = parse_local_datetime_to_utc(date_from) if date_from else None
        date_to = parse_local_datetime_to_utc(date_to) if date_to else None
        state = (
            input("Estado (proximos/pasados/agotados, enter para omitir): ") or "").lower()
        results = self.apply_filters(self._events, keyword,
                        category, date_from, date_to, state)
        if not results:
            print("No se encontraron eventos.")
            return
        for event in results:
            start_local = datetime.fromisoformat(event["start_utc"]).astimezone()
            print(f"ID: {event['id']} | {event['name']} | {start_local.strftime('%d-%m-%Y %H:%M %Z')} | Cat: {event['category']} | Precio: {event['price']} | Disponibles: {event['available']}/{event['total_capacity']}")


    def _update_event(self):
        print("Actualizar evento")
        # Acá se debería verificar si es que hay eventos
        try:
            event_id = int(input("ID del evento a actualizar: ").strip())
            # logica de buscar evento y de verificar iria aca
            event = next((e for e in self._events if e['id'] == event_id), None)
            if not event:
                print("Evento no encontrado.")
                return

            name = input(f"Nombre [{event['name']}]: ") or event['name']
            description = input(
                f"Descripción [{event['description']}]: ") or event['description']
            date_str = input(
                "Fecha y hora (DD-MM-YYYY o DD-MM-YYYY HH:MM) (enter para mantener): ") or ""
            if date_str:
                start_utc = parse_local_datetime_to_utc(date_str)
                if start_utc:
                    event['start_utc'] = start_utc.isoformat()
            category = input(f"Categoría [{event['category']}]: ") or event['category']
            price = input(f"Precio [{event['price']}]: ") or str(event['price'])
            price_v = validate_price(price)
            if price_v is not None:
                event['price'] = price_v
            cap = input(f"Cupos totales [{event['total_capacity']}]: ") or str(
                event['total_capacity'])
            cap_v = validate_int(cap)
            if cap_v is not None:
                delta = cap_v - event['total_capacity']
                event['total_capacity'] = cap_v
                event['available'] = max(0, event['available'] + delta)
            print("Evento actualizado.")
        except Exception as e:
            print(f"Error actualizando evento: {e}")


    def _delete_event(self):
        print("Eliminar evento")
        ##logica de eliminar evento
        try:
            event_id = int(input("ID del evento a eliminar: ").strip())
            ### logic ade eliminar y verificar iria aca
            event = next((e for e in self._events if e['id'] == event_id), None)
            if not event:
                print("Evento no encontrado.")
                return
            print(
                f"Evento: {event['id']} - {event['name']} (Disponibles: {event['available']}/{event['total_capacity']})")
            if confirm_yes(input("¿Confirma eliminación? (s/N): ")):
                self._events.remove(event)
                print("Evento eliminado.")
            else:
                print("Eliminación cancelada.")
        except Exception as e:
            print(f"Error eliminando evento: {e}")

EVENT_MANAGER = EventManager()