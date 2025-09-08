from entities import UserData, ResponseLogin
from event import EVENT_MANAGER
import os, sys
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from domain import sell as d_sell, refund as d_refund, report_summary as d_report

class UserManager:
    # ---------- Menús ----------
    user_options = {
        1: {"name": "Gestionar eventos", "action": "manage_events"},
        2: {"name": "Generar reportes", "action": "generate_reports"},
        3: {"name": "Cerrar sesión", "action": "logout"},
        4: {"name": "Salir", "action": "exit"}
    }

    admin_options = {
        1: {"name": "Gestionar eventos", "action": "manage_events"},
        2: {"name": "Gestionar ventas y devoluciones", "action": "manage_sales"},
        3: {"name": "Generar reportes", "action": "generate_reports"},
    }

    _userData: UserData = None
    
    def __init__(self):
        pass

    def get_user(self):
        return self._userData

    def set_user(self, user: UserData):
        self._userData = user

    def _user_select(self, option: str):
        match option:
            case 'manage_events':
                EVENT_MANAGER.event_menu(self.get_user())
            case 'manage_sales':
                self._sales_menu()
            case 'generate_reports':
                self._print_report()
            case 'manage_users':
                print("Gestionando usuarios...")
            case 'logout':
                print("Cerrando sesión...")
                return {"logged_out": True}
            case 'exit':
                print("Saliendo de la aplicación...")
                exit(0)
            case _:
                print("Opción no válida")

    def _admin_select(self, option: str):
        match option:
            case 'manage_events':
                EVENT_MANAGER.event_menu(self.get_user())
            case 'manage_sales':
                self._sales_menu()
            case 'generate_reports':
                self._print_report()
            case 'manage_users':
                print("Gestionando usuarios...")
            case 'logout':
                print("Cerrando sesión...")
                return {"logged_out": True}
            case 'exit':
                print("Saliendo de la aplicación...")
                exit(0)
            case _:
                print("Opción no válida")

    def user_menu(self):
        while True:
            print("\n--- Menú de usuario ---")
            user = self.get_user()
            options = self.admin_options if user.role == 'admin' else self.user_options
            for key, value in options.items():
                print(f"{key}. {value['name']}")
            choice = input("Porfavor seleccione una opción: ")
            isValidChoice = choice.isdigit() and int(choice) in options
            if isValidChoice:
                action = options[int(choice)]['action']
                if user.role == 'admin':
                    res = self._admin_select(action)
                else:
                    res = self._user_select(action)
                if isinstance(res, dict) and res.get("logged_out"):
                    return
            else:
                print("Opción no válida.")

    def _sales_menu(self):
        print("\n--- Ventas y devoluciones ---")
        print("1. Vender")
        print("2. Devolver")
        print("0. Volver")
        choice = input("Seleccione una opción: ").strip()
        if choice == '1':
            self._sell_flow()
        elif choice == '2':
            self._refund_flow()
        elif choice == '0':
            return
        else:
            print("Opción no válida.")

    def _sell_flow(self):
        try:
            eid = int(input("ID evento: ").strip())
            qty = int(input("Cantidad: ").strip())
            user = self.get_user()
            d_sell(eid, qty, user.id)
            print("Venta registrada.")
        except Exception as e:
            print(f"Error en venta: {e}")

    def _refund_flow(self):
        try:
            eid = int(input("ID evento: ").strip())
            qty = int(input("Cantidad a devolver: ").strip())
            user = self.get_user()
            d_refund(eid, qty, user.id)
            print("Devolución registrada.")
        except Exception as e:
            print(f"Error en devolución: {e}")

    def _print_report(self):
        try:
            rep = d_report()
            print(f"Total eventos: {rep['total_events']}")
            print(f"Suma cupos disponibles: {rep['sum_available']}")
            agotados = rep.get('sold_out', [])
            if agotados:
                print("Agotados:")
                for eid, name in agotados:
                    print(f" - {eid}: {name}")
        except Exception as e:
            print(f"Error generando reporte: {e}")


USER_MANAGER = UserManager()
