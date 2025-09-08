from interface.entities import UserData, ResponseLogin
from interface.event import EVENT_MANAGER


class UserManager:
    viewer_options = {
        1: {"name": "Gestionar eventos", "action": "manage_events"},
        2: {"name": "Generar reportes", "action": "generate_reports"},
        3: {"name": "Cerrar sesión", "action": "logout"},
        4: {"name": "Salir", "action": "exit"}
    }

    admin_options = {
        1: {"name": "Gestionar eventos", "action": "manage_events"},
        2: {"name": "Gestionar ventas y devoluciones", "action": "manage_sales"},
        3: {"name": "Generar reportes", "action": "generate_reports"},
        4: {"name": "Cerrar sesión", "action": "logout"},
        5: {"name": "Salir", "action": "exit"}
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
                print("Gestionando ventas y devoluciones...")
            case 'generate_reports':
                print("Generando reportes...")
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
                print("Gestionando ventas y devoluciones...")
            case 'generate_reports':
                print("Generando reportes...")
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
            if not user:
                print("No hay usuario autenticado.")
                return
            options = self.admin_options if user.role == 'admin' else self.viewer_options
            for key, value in options.items():
                print(f"{key}. {value['name']}")
            choice = input("Porfavor seleccione una opción: ")
            isValidChoice = choice.isdigit() and int(choice) in options
            if not isValidChoice:
                print("Opción no válida.")
                continue
            action = options[int(choice)]['action']
            result = self._admin_select(
                action) if user.role == 'admin' else self._user_select(action)
            if isinstance(result, dict) and result.get('logged_out'):
                self._userData = None
                print("Sesión cerrada.")
                return
            if action == 'exit':
                exit(0)


USER_MANAGER = UserManager()
