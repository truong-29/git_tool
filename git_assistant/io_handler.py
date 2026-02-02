import sys
from abc import ABC, abstractmethod

# Fix encoding cho Windows console
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')
    sys.stderr.reconfigure(encoding='utf-8')

class IOHandler(ABC):
    @abstractmethod
    def log(self, message, color=None):
        pass

    @abstractmethod
    def error(self, message):
        pass

    @abstractmethod
    def success(self, message):
        pass
    
    @abstractmethod
    def warning(self, message):
        pass

    @abstractmethod
    def input(self, prompt):
        pass

    @abstractmethod
    def confirm(self, prompt):
        pass

    @abstractmethod
    def select(self, prompt, options):
        pass

class ConsoleIO(IOHandler):
    def log(self, message, color=None):
        print(message)

    def error(self, message):
        print(f"\033[91m✘ {message}\033[0m")

    def success(self, message):
        print(f"\033[92m✔ {message}\033[0m")

    def warning(self, message):
        print(f"\033[93m⚠ {message}\033[0m")

    def input(self, prompt):
        return input(f"{prompt}: ").strip()

    def confirm(self, prompt):
        return input(f"{prompt} (y/n): ").lower().strip() == 'y'
