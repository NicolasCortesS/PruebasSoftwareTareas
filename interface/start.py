from entities import ResponseLogin
from auth import AUTH

start_options = {
    1: {"name": "Iniciar sesión", "action": "login"},
    2: {"name": "Registrarse", "action": "register"},
    0: {"name": "Terminar aplicación", "action": "exit"}
}

def start_select(option: str) -> ResponseLogin:
    match option:
        case 'login':
            return AUTH.login()
        case 'register':
            return AUTH.register()
        case 'exit':
            print("Saliendo de la aplicación...")
            exit(0)
        case _:
            print("Opción no válida")
            return ResponseLogin(success=False)

def start() -> ResponseLogin:
    print("\n--- Menú de inicio ---")
    for key, value in start_options.items():
        print(f"{key}. {value['name']}")
    choice = input("Porfavor seleccione una opción: ")
    isValidChoice = choice.isdigit() and int(choice) in start_options
    if isValidChoice:
        action = start_options[int(choice)]['action']
        return start_select(action)
    else:
        print("Opción no válida.")
        return ResponseLogin(success=False)
