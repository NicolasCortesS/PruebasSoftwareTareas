from entities import UserData, ResponseLogin

_USERS = {
	"admin": {"password": "admin", "role": "admin"},
	"user": {"password": "user", "role": "user"}
}

class Auth():
    def login(self):
        print("\n--- Iniciar sesión ---")
        username = input("Usuario: ")
        password = input("Contraseña: ")
        if username in _USERS: 
            user = _USERS.get(username) 
        else:
            user = None

        if user and user["password"] == password:
            print(f"Bienvenido, {username}!")
            user = UserData(username=username, role=user["role"])
            return ResponseLogin(success=True, userData=user)
        else:
            print("Credenciales incorrectas.")
            return ResponseLogin(success=False)

    def register(self):
        print("\n--- Registrarse ---")
        username = input("Elija un nombre de usuario: ")
        password = input("Elija una contraseña: ")
        #Falta llamar realmente a la bd
        print(f"Usuario {username} registrado exitosamente.")
        user = UserData(username=username, role="user")
        return ResponseLogin(success=True, userData=user)

AUTH = Auth()