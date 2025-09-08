from interface.validations import validate_int, confirm_yes
from interface.entities import UserData
import domain
from datetime import datetime

class SalesAndRefundManager:
    sales_menu_options = {
        1: {"name": "Registrar venta/inscripción", "action": "register_sale_or_registration"},
        2: {"name": "Registrar devolución", "action": "register_refund"},
        0: {"name": "Volver", "action": "back"}
    }

    def manage_sales_and_refunds_menu(self, user: UserData):
        if not user or user.role != "admin":
            print("Permisos insuficientes.")
            return
        while True:
            print("\n--- Gestión de ventas y devoluciones ---")
            for option_number, option_data in self.sales_menu_options.items():
                print(f"{option_number}. {option_data['name']}")
            choice = input("Seleccione una opción: ")
            if not (choice.isdigit() and int(choice) in self.sales_menu_options):
                print("Opción no válida.")
                continue
            action = self.sales_menu_options[int(choice)]["action"]
            if action == "register_sale_or_registration":
                self.register_sale_or_registration(user)
            elif action == "register_refund":
                self.register_refund(user)
            elif action == "back":
                return

    def register_sale_or_registration(self, user: UserData):
        try:
            event_id = int(input("ID del evento: ").strip())
        except Exception:
            print("ID inválido.")
            return
        try:
            row = domain.get_event_by_id(event_id)
        except Exception as e:
            print(f"Error consultando evento: {e}")
            return
        if not row:
            print("Evento no encontrado.")
            return
        _, name, description, starts_at, category, price, seats_total, seats_sold = row
        available = seats_total - seats_sold
        print(f"Evento: {event_id} - {name} | Fecha: {starts_at.astimezone().strftime('%d-%m-%Y %H:%M %Z')} | Disponibles: {available}/{seats_total}")
        if available <= 0:
            print("No hay cupos disponibles.")
            return
        quantity = validate_int(input("Cantidad a vender/inscribir: ").strip() or "")
        if quantity is None or quantity <= 0:
            print("Cantidad inválida.")
            return
        if quantity > available:
            print("No hay suficientes cupos disponibles.")
            return
        if not confirm_yes(input("Confirmar venta? (s/N): ")):
            print("Venta cancelada.")
            return
        try:
            domain.sell(event_id, quantity, user.id)
            print("Venta registrada.")
        except Exception as e:
            print(f"Error registrando venta: {e}")

    def register_refund(self, user: UserData):
        try:
            event_id = int(input("ID del evento: ").strip())
        except Exception:
            print("ID inválido.")
            return
        try:
            row = domain.get_event_by_id(event_id)
        except Exception as e:
            print(f"Error consultando evento: {e}")
            return
        if not row:
            print("Evento no encontrado.")
            return
        _, name, description, starts_at, category, price, seats_total, seats_sold = row
        if seats_sold <= 0:
            print("No hay ventas que devolver.")
            return
        print(f"Evento: {event_id} - {name} | Vendidos: {seats_sold} | Cupos totales: {seats_total}")
        quantity = validate_int(input("Cantidad a devolver: ").strip() or "")
        if quantity is None or quantity <= 0:
            print("Cantidad inválida.")
            return
        if quantity > seats_sold:
            print("No se puede devolver más de lo vendido.")
            return
        if not confirm_yes(input("Confirmar devolución? (s/N): ")):
            print("Devolución cancelada.")
            return
        try:
            domain.refund(event_id, quantity, user.id)
            print("Devolución registrada.")
        except Exception as e:
            print(f"Error registrando devolución: {e}")

SALES_AND_REFUNDS_MANAGER = SalesAndRefundManager()
