import os
import sys

class Colors:
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

def print_header(msg):
    print(f"{Colors.HEADER}{Colors.BOLD}=== {msg} ==={Colors.ENDC}")

def print_success(msg):
    print(f"{Colors.GREEN}✔ {msg}{Colors.ENDC}")

def print_info(msg):
    print(f"{Colors.CYAN}ℹ {msg}{Colors.ENDC}")

def print_warning(msg):
    print(f"{Colors.WARNING}⚠ {msg}{Colors.ENDC}")

def print_error(msg):
    print(f"{Colors.FAIL}✘ {msg}{Colors.ENDC}")

def get_input(prompt):
    return input(f"{Colors.BLUE}{prompt}: {Colors.ENDC}").strip()

def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')
