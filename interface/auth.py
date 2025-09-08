from interface.entities import UserData, ResponseLogin
import domain


class Auth:
    def login(self):
        print("\n--- Iniciar sesión ---")
        username = input("Usuario: ")
        password = input("Contraseña: ")
        try:
            res = domain.auth_user(username, password)
        except Exception as e:
            print(f"Error de autenticación: {e}")
            return ResponseLogin(success=False)
        if res:
            uid, role = res
            print(f"Bienvenido, {username}!")
            ud = UserData(username=username, role=role, id=uid)
            return ResponseLogin(success=True, userData=ud)
        else:
            print("Credenciales incorrectas.")
            return ResponseLogin(success=False)

    def register(self):
        print("\n--- Registrarse ---")
        username = input("Elija un nombre de usuario: ")
        password = input("Elija una contraseña: ")
        try:
            uid = domain.create_user(username=username, password=password, role='viewer')
            print(f"Usuario {username} registrado exitosamente (id={uid}).")
            ud = UserData(username=username, role='viewer', id=uid)
            return ResponseLogin(success=True, userData=ud)
        except Exception as e:
            print(f"Error registrando usuario: {e}")
            return ResponseLogin(success=False)


AUTH = Auth()