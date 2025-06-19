# main.py
from irrigation_system.ui import MenuInterativo

if __name__ == "__main__":
    print("Iniciando Sistema de Gerenciamento Agrícola...")
    menu = MenuInterativo()
    menu.executar()