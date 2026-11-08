import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SRC_DIR = ROOT / 'src'
sys.path.append(str(SRC_DIR))

from storage import DB_PATH, load_database, get_conn

while True:
    print('''
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

    choice = input("Enter your choice: ").strip()
    if choice == '0':
        print("Exiting...")
        break
    elif choice == '1':
        print("Generating data...")
    elif choice == '2':
        print("Loading database...")
    elif choice == '3':
        print("Writing reports...")
    elif choice == '4':
        print("Due next...")
    elif choice == '5':
        print("Due within...")
    elif choice == '6':
        print("Overdue...")
    elif choice == '7':
        print("Overdue by Location...")
    elif choice == '8':
        print("Overdue by Asset Type...")
    else:
        print("Invalid choice. Please try again.")
