from start import start
from user import USER_MANAGER


def main():
    print("Bienvenido a la aplicación")
    response = start()
    while not response.success:
        response = start()
    USER_MANAGER.set_user(response.userData)
    USER_MANAGER.user_menu()

if __name__ == "__main__":
    main()
