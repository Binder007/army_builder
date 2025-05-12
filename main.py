# main.py
import subprocess
import platform

def clear_screen():
    """Clears the terminal screen."""
    if platform.system() == "Windows":
        subprocess.run("cls", check=True)
    else:
        subprocess.run("clear", shell=True, check=True)

def main_menu():
    """Displays the main menu and handles user selection."""
    while True:
        clear_screen()
        print("--- Main Menu ---")
        print("1. Unit Editor")
        print("2. Army Drafter")
        print("3. Exit")

        choice = input("Enter your choice: ")

        if choice == '1':
            print("\nLaunching Unit Editor...")
            try:
                subprocess.run(["python", "unit_editor/editor.py"], check=True)
            except FileNotFoundError:
                print("Error: 'unit_editor/editor.py' not found.")
            except subprocess.CalledProcessError as e:
                print(f"Error running Unit Editor: {e}")
        elif choice == '2':
            print("\nLaunching Army Drafter...")
            try:
                subprocess.run(["python", "army_drafting/drafter.py"], check=True)
            except FileNotFoundError:
                print("Error: 'army_drafting/drafter.py' not found.")
            except subprocess.CalledProcessError as e:
                print(f"Error running Army Drafter: {e}")
        elif choice == '3':
            print("Exiting.")
            break
        else:
            print("Invalid choice. Please try again.")

if __name__ == "__main__":
    main_menu()
