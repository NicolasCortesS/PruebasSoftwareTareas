# ---------- Imports ----------
import os, sys
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from entities import UserData, ResponseLogin
from domain import auth_user, create_user

# ---------- Auth ----------
class Auth():
    """
    Clase para manejar la autenticación de usuarios.
    Proporciona métodos para login y registro.
    """
    def login(self):
        """
        Procesa el login de un usuario.
        
        Returns:
            ResponseLogin: Respuesta con el resultado del login.
        """
        print("\n--- Iniciar sesión ---")
        username = input("Usuario: ")
        password = input("Contraseña: ")
        auth = auth_user(username, password)
        if not auth:
            print("Credenciales incorrectas.")
            return ResponseLogin(success=False)
        uid, role = auth
        print(f"Bienvenido, {username}!")
        # mapear roles de dominio (admin/viewer) a interfaz (admin/user)
        ui_role = "admin" if role == "admin" else "user"
        user = UserData(id=uid, username=username, role=ui_role)
        return ResponseLogin(success=True, userData=user)

    def register(self):
        """
        Procesa el registro de un nuevo usuario.
        
        Returns:
            ResponseLogin: Respuesta con el resultado del registro.
        """
        print("\n--- Registrarse ---")
        username = input("Elija un nombre de usuario: ")
        password = input("Elija una contraseña: ")
        try:
            uid = create_user(username, password, role="viewer")
            user = UserData(id=uid, username=username, role="user")
            print(f"Usuario {username} registrado exitosamente.")
            return ResponseLogin(success=True, userData=user)
        except Exception as e:
            print(f"Error registrando usuario: {e}")
            return ResponseLogin(success=False)

AUTH = Auth()