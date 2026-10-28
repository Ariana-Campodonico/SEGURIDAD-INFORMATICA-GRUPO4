import ipaddress
import socket
from datetime import datetime


def escanear_puertos(host="127.0.0.1", puertos=(80, 443, 3306, 5000, 8080)):
    try:
        direccion = ipaddress.ip_address(host)
    except ValueError as error:
        raise ValueError("El destino debe ser una dirección IP de loopback.") from error
    if not direccion.is_loopback:
        raise ValueError("Por seguridad, este escáner solo admite loopback.")

    puertos = tuple(puertos)
    if any(type(puerto) is not int or not 1 <= puerto <= 65535 for puerto in puertos):
        raise ValueError("Cada puerto debe ser un entero entre 1 y 65535.")

    print("="*60)
    print(f" ESCANER DE PUERTOS Y SERVICIOS - GRUPO 4 UNEMI")
    print(f" Host objetivo: {host} | Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*60)

    for puerto in puertos:
        try:
            with socket.create_connection((str(direccion), puerto), timeout=1.0):
                abierto = True
        except OSError:
            abierto = False
        if abierto:
            print(f"[+] Puerto {puerto:5d} : ABIERTO")
        else:
            print(f"[-] Puerto {puerto:5d} : CERRADO / FILTRADO")
    print("="*60)

if __name__ == '__main__':
    escanear_puertos()