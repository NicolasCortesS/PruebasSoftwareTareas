from interface.start import start
from interface.user import USER_MANAGER
from seeder import seed_admin


def main():
    print("Bienvenido a la aplicación")
    seed_admin()

    while True:
        response = start()
        while not response.success:
            response = start()
        USER_MANAGER.set_user(response.userData)
        USER_MANAGER.user_menu()

if __name__ == "__main__":
    main()
