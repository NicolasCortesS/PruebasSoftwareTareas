from entities import UserData, ResponseLogin
from event import EVENT_MANAGER

class UserManager:
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
                self._admin_select(action)
            else:
                self._user_select(action)
        else:
            print("Opción no válida.")


USER_MANAGER = UserManager()
