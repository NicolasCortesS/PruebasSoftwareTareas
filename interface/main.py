import os, sys
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from start import start
from user import USER_MANAGER


# ---------- Entry point ----------
def main():
    print("Bienvenido a la aplicación")
    while True:
        response = start()
        while not response.success:
            response = start()
        USER_MANAGER.set_user(response.userData)
        USER_MANAGER.user_menu()
        USER_MANAGER.set_user(None)

if __name__ == "__main__":
    main()
