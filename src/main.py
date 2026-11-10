import sys
from pathlib import Path
from datetime import datetime

ROOT = Path(__file__).resolve().parent.parent
SRC_DIR = ROOT / 'src'
sys.path.append(str(SRC_DIR))

from storage import DB_PATH, load_database, get_conn
from generator import generate_all, OUT_DIR
from reports import write_overdue_by_location, write_overdue_by_type, write_history_by_month, REPORT_DIR
from queries import due_next, due_within, overdue_procedures

def show_menu():
    print('''
    Menu:
    1. Generate data
    2. Load database
    3. Write reports
    4. Due next
    5. Due within
    6. Overdue
    7. Overdue by Location
    8. Overdue by Asset Type
    0. Quit
    ''')

def main():
    while True:
        show_menu()

        choice = input("Enter your choice: ").strip()
        if choice == '0':
            print("Exiting...")
            break
        elif choice == '1':
            print("Generating data...")
            generate_all()
            print(f"Data written to {OUT_DIR}. You can now load the database.")
        elif choice == '2':
            print("Loading database...")
            if not (OUT_DIR / 'assets.csv').exists(): print(f"No data found in {OUT_DIR}. Please generate data first (Option 1).")
            else: 
                load_database(DB_PATH, OUT_DIR)
                print(f"Database loaded from {OUT_DIR}. You can now write reports.")
        elif choice == '3':
            print("Writing reports...")
            if not DB_PATH.exists(): print(f"No database found at {DB_PATH}. Please load the database first (Option 2).")
            else:
                conn = get_conn()
                today = datetime.now().strftime('%Y-%m-%d')
                write_overdue_by_location(conn, today, REPORT_DIR / 'overdue_by_location.xlsx')
                write_overdue_by_type(conn, today, REPORT_DIR / 'overdue_by_type.xlsx')
                write_history_by_month(conn, REPORT_DIR / 'history_by_month.xlsx')
                conn.close()
                print(f"Reports written to {REPORT_DIR}.")
        elif choice == '4':
            print("Due next...")
            if not DB_PATH.exists(): print(f"No database found at {DB_PATH}. Please load the database first (Option 2).")
            else:
                raw = input('How many procedures? ').strip()
                try:
                    n = int(raw)
                except ValueError:
                    print("Invalid input. Please enter a valid number.")
                    continue
                if n <= 0:
                    print("Please enter a positive number.")
                    continue
                conn = get_conn()
                rows = due_next(conn, n)
                conn.close()
                if not rows:
                    print("No procedures due in that window.")
                for procedure_id, last_done, next_due in rows:
                    print(f"Procedure ID: {procedure_id}, Last Done: {last_done or 'never serviced'}, Next Due: {next_due}")
        elif choice == '5':
            print("Due within...")
            if not DB_PATH.exists(): print(f"No database found at {DB_PATH}. Please load the database first (Option 2).")
            else:
                rawstrt = input('Enter start date (YYYY-MM-DD), Press Enter key for today: ').strip()
                if rawstrt == '':
                    start_date = datetime.now().strftime('%Y-%m-%d')
                    print("No start date provided. Defaulting to today:", start_date)
                else:
                    try:
                        datetime.strptime(rawstrt, '%Y-%m-%d')
                    except ValueError:
                        print("Invalid date format. Please enter a valid date in YYYY-MM-DD format.")
                        continue
                    start_date = rawstrt
                rawwnd = input('How many days? ').strip()
                try:
                    days = int(rawwnd)
                except ValueError:
                    print("Invalid input. Please enter a valid number.")
                    continue
                if days <= 0:
                    print("Please enter a positive number.")
                    continue
                conn = get_conn()
                rows = due_within(conn, start_date, days)
                conn.close()
                if not rows:
                    print("No procedures due in that window.")
                else:
                    for procedure_id, last_done, next_due in rows:
                        print(f"Procedure ID: {procedure_id}, Last Done: {last_done or 'never serviced'}, Next Due: {next_due}")
        elif choice == '6':
            print("Overdue...")
            if not DB_PATH.exists(): print(f"No database found at {DB_PATH}. Please load the database first (Option 2).")
            else:
                conn = get_conn()
                today = datetime.now().strftime('%Y-%m-%d')
                rows = overdue_procedures(conn, today)
                conn.close()
                if not rows:
                    print("No overdue procedures.")
                else:
                    print(f"{len(rows)} overdue procedures found:")
                    for procedure_id, last_done, next_due in rows:
                        print(f"Procedure ID: {procedure_id}, Last Done: {last_done or 'never serviced'}, Next Due: {next_due}")
        elif choice == '7':
            print("Overdue by Location...")
        elif choice == '8':
            print("Overdue by Asset Type...")
        else:
            print("Invalid choice. Please try again.")

if __name__ == "__main__":
    main()
