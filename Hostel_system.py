# DATA SETUP
import json 
import os 
hostel_blocks = {
    "Block A": {
        "num_rooms": 10,
        "capacity_per_room": 4,
        "rooms": {f"A{i}": [] for i in range(1, 11)}
    },
    "Block B": {
        "num_rooms": 10,
        "capacity_per_room": 3,
        "rooms": {f"B{i}": [] for i in range(1, 11)}
    },
    "Block C": {
        "num_rooms": 10,
        "capacity_per_room": 2,
        "rooms": {f"C{i}": [] for i in range(1, 11)}
    },        
}

students = {} 

def print_occupancy_overview():
    print("\n=== HOSTEL OCCUPANCY OVERVIEW ===")
    for block_name, block in hostel_blocks.items():
        total_capacity = block["num_rooms"] * block["capacity_per_room"]
        occupied = sum(len(students) for students in block["rooms"].values())
        print(f"{block_name}: {occupied}/{total_capacity} beds occupied "f"({block['num_rooms']} rooms, {block['capacity_per_room']} beds/room)")
    print("=========================\n")

# STUDENT REGISTRATION & ROOM ALLOCATION 

def allocate_student(reg_number, name, block_name, room_name):
    """
    Try to allocate a student to aspecific room in a specific block.
    Returns True if it suceeded, False if rejected.
    """
    if block_name not in hostel_blocks:
        print(f"REJECTED: '{block_name}' is not a vaild hostel block.")
        return False

    block = hostel_blocks[block_name]

    if room_name not in block["rooms"]:
        print(f"REJECTED: Room '{room_name}' does not exist in {block_name}.")
        return False

    current_occupants = block["rooms"] [room_name]
    capacity = block["capacity_per_room"]

    if len(current_occupants) >= capacity:
        print(f"REJECTED: Room {room_name} is full "f"({len(current_occupants)}/{capacity}). Choose another room.")
        return False

    if reg_number in students:
        print(f"REJECTED: Student {reg_number} is already registered.")
        return False

    current_occupants.append(reg_number)
    students[reg_number] = {
        "name": name,
        "block": block_name,
        "room": room_name,
        "total_fees": 1500000,
        "balance": 1500000,
    }
    print(f"SUCCESS: {name} ({reg_number}) allocated to {room_name}, {block_name}.")
    return True      

# FEE PAYMENT RECORDING

def record_payment(reg_number, amount):
    """
    Record a full or partial fee payment for a student.
    Reduces their outstanding balance. Returns True if recorded, False if rejected.
    """
    if reg_number not in students:
        print("REJECTED: No student found with reg number {reg_number}.")
        return False

    if amount <= 0:
        print("REJECTED: Payment amount must be greater than zero.")
        return False

    student = students[reg_number]

    if "payments" not in student:
        student["payments"] = []

    student["payments"].append(amount)
    student["balance"] -= amount 

    if student["balance"] < 0:
        student["balance"] = 0

    print(f"SUCCESS: UGX {amount:,} recorded for {student['name']} ({reg_number})."f"New balance: UGX {student['balance']:,}")
    return True 

# SEARCH AND REPORTING

def search_student(query):
    """
    Search for a student by exact reg number, or by name (partial match, case-insensitive).
    Prints matching student(s). Returns the list of matchingreg numbers.
    """
    query_lower = query. strip().lower()
    matches = []

    if query in students:
        matches.append(query)
    else:

        for reg_number, info in students.items():
            if query_lower in info["name"].lower():
                matches.append(reg_number)

    if not matches:
        print(f"No student found matching '{query}'.")
        return []

    print(f"\n--- Search results for '{query}'---")
    for reg_number in matches:
        info =  students[reg_number]
        print(f"{reg_number}: {info['name']} | {info['block']} {info['room']} | "f"Balance: UGX {info['balance']:,}")
    print("----------------------------\n")
    return matches 

def block_occupancy_report(block_name):
    """Print a detailed room-by-room report for one hostel block."""
    if block_name not in hostel_blocks:
        print(f"'{block_name}' is not a valid hostel block.")
        return

    block = hostel_blocks[block_name] 
    print(f"\n===OCCUPANCY REPORT: {block_name} ===")
    for room_name, occupants in block["rooms"].items():
        capacity = block["capacity_per_room"]
        if occupants:
            names = ", ".join(students[reg]["name"] for reg in occupants)
        else:
            names = "empty" 
        print(f" {room_name}: {len(occupants)}/{capacity} - {names}") 
    print("============================\n")

def fee_defaulters(threshold):
    """Print every student whose oustanding balance is above the given threshold."""
    print(f"\n=== FEE DEFAULTERS (balance above UGX {threshold:,}) ===")
    found = False
    for reg_number, info in students.items():
        if info["balance"] > threshold:
            print(f"  {reg_number}: {info['name']} - owes UGX {info['balance']:,}")
            found = True
    if not found:
        print(" No defaulters above this threshold.")
    print("===================================\n")

# FILE PERSISTENCE

DATA_FILE = "hostel_data.json"

def save_data():
    """Save the current hostel_blocks and students data to a JSON file."""
    data = {
        "hostel_blocks": hostel_blocks,
        "students": students
    }
    try:
        with open(DATA_FILE, "w") as f:
            json.dump(data, f, indent=2)
        print(f"Data saved to {DATA_FILE}.")
    except IOError as e:
        print(f"WARNING: Could not save data - {e}")

def load_data():
    """
    Load hostel_blocks and students from the JSON file if it exists and is valid.
    If the file is missing or damaged, keep the predefined defaults instead of crashing.
    """
    global hostel_blocks, students

    if not os.path.exists(DATA_FILE):
        print("No saved data found - starting with fresh default data.")
        return

    try:
        with open(DATA_FILE, "r") as f:
            data = json.load(f)
        hostel_blocks = data["hostel_blocks"]
        students = data["students"] 
        print(f"Data loaded from {DATA_FILE}.")
    except (json.JSONDecodeError, KeyError) as e:
        print(f"WARNING: {DATA_FILE} is damaged or invalid ({e}). "f"Starting with fresh default data instead.")       
                    

# MENU-DRVEN DRIVER PROGRAMME

def get_int_input(prompt):
    """Keep askng until the user types a valid whole number. Prevents crashes on bad input."""
    while True:
        value = input(prompt).strip()
        if value.isdigit():
            return int(value)
        print("Please enter a valid whole number.")

def menu_allocate_student():
    reg_number = input("Enter student registration number: ").strip()
    name = input("Enter student full name: ").strip() 

    print("Available blocks:", ", ".join(hostel_blocks.keys())) 
    block_name = input("Enter block name (e.g. Block A): ").strip()

    room_name = input("Enter room number (e.g. A1): ").strip()

    allocate_student(reg_number, name, block_name, room_name)

def menu_record_payment():
    reg_number = input("Enter student registration number: ").strip()
    amount = get_int_input("Enter payment amount (UGX): ")
    record_payment(reg_number, amount)

def menu_search_student():
    query = input("Enter registration number or name to search: ").strip()
    search_student(query)

def menu_block_report():
    print("Available blocks:", ", ".join(hostel_blocks.keys()))
    block_name = input("Enter block name for the report: ").strip() 
    block_occupancy_report(block_name) 

def menu_fee_defaulters():
    threshold = get_int_input("Enter balance threshold (UGX): ")
    fee_defaulters(threshold)

def show_menu():
    print("\n============HOSTEL MANAGEMENT SYSTEM===========")
    print("1. View occupancy overview")
    print("2. Register/allocate a student to a room")
    print("3. Record a fee payment")
    print("4. Search for a student")
    print("5. View block occupancy report")
    print("6. View fee defaulters")
    print("7. Save and exit")
    print("===================================")

def run_menu():
    load_data() 
    while True:
        show_menu() 
        choice = input("Select an option (1-7): ").strip() 

        if choice == "1":
            print_occupancy_overview()
        elif choice == "2":
            menu_allocate_student()
        elif choice == "3":
            menu_record_payment()
        elif choice == "4":
            menu_search_student() 
        elif choice == "5":
            menu_block_report() 
        elif choice == "6":
            menu_fee_defaulters() 
        elif choice == "7":
            save_data() 
            print("Goodbye!")
            break
        else:
            print("Invalid option. Please choose a number from 1 t0 7.")                

           
if __name__ == "__main__":
    run_menu() 
