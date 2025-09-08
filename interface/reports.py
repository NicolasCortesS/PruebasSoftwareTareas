import domain
from interface.entities import UserData

class ReportsManager:
    reports_options = {
        1: {"name": "Mostrar resumen de eventos", "action": "show_summary"},
        0: {"name": "Volver", "action": "back"}
    }

    def reports_menu(self, user: UserData):
        if not user:
            print("Debe iniciar sesión para ver reportes.")
            return
        while True:
            print("\n--- Reportes ---")
            for option_number, option_data in self.reports_options.items():
                print(f"{option_number}. {option_data['name']}")
            choice = input("Seleccione una opción: ")
            if not (choice.isdigit() and int(choice) in self.reports_options):
                print("Opción no válida.")
                continue
            action = self.reports_options[int(choice)]["action"]
            if action == "show_summary":
                self.show_events_summary()
            elif action == "back":
                return

    def show_events_summary(self):
        try:
            summary = domain.report_summary()
        except Exception as e:
            print(f"Error generando reporte: {e}")
            return
        print("\n--- Resumen de eventos ---")
        print(f"Total de eventos: {summary.get('total_events')}")
        print(f"Suma de cupos disponibles: {summary.get('sum_available')}")
        sold_out = summary.get('sold_out') or []
        if sold_out:
            print("Eventos agotados:")
            for sid, name in sold_out:
                print(f"  - {sid}: {name}")
        else:
            print("No hay eventos agotados.")

REPORTS_MANAGER = ReportsManager()
