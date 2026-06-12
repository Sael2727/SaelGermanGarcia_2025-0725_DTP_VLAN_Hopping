# 🔀 DTP VLAN Hopping Attack — Seguridad de Redes

<div align="center">

![Python](https://img.shields.io/badge/Python-3.x-blue?style=for-the-badge&logo=python)
![Scapy](https://img.shields.io/badge/Scapy-Latest-green?style=for-the-badge)
![Platform](https://img.shields.io/badge/Platform-Linux-orange?style=for-the-badge&logo=linux)
![License](https://img.shields.io/badge/Uso-Educativo-red?style=for-the-badge)

**Sael Germán García** | Matrícula: `2025-0725`  
Asignatura: Seguridad de Redes | Profesor: Jonathan Rondón  
Instituto Tecnológico de las Américas — ITLA | 2026

</div>

---

## 📋 Descripción del Ataque

El **DTP VLAN Hopping Attack** explota la negociación dinámica del protocolo **DTP (Dynamic Trunking Protocol)**. Mediante la construcción de paquetes DTP desde cero con Scapy, el atacante simula un dispositivo que desea negociar trunk enviando TLVs hacia la dirección multicast Cisco `01:00:0c:cc:cc:cc` con PID `0x2004`. Cuando el puerto del switch está en modo **dynamic auto** con negociación habilitada, el switch acepta la negociación y convierte el puerto de `static access` a `trunk`, otorgando al atacante acceso a todas las VLANs permitidas en el enlace.

> 💡 **Condición de vulnerabilidad:** El puerto del atacante (e0/3) debe estar configurado como `switchport mode dynamic auto` sin `switchport nonegotiate`, lo que permite que acepte negociaciones DTP entrantes.

---

## 🗺️ Topología de Red

### 📊 Parámetros del Ataque

| Parámetro | Valor | Descripción |
|:---------:|:-----:|-------------|
| Interfaz atacante | `ens3` | Interfaz Linux conectada a SW1-CORE e0/3 |
| Puerto atacado | `SW1-CORE e0/3` | Puerto vulnerable en `dynamic auto` |
| Dominio DTP/VTP | `LAB` | Dominio configurado en la práctica |
| MAC destino | `01:00:0c:cc:cc:cc` | Multicast Cisco para DTP/VTP/CDP |
| PID DTP | `0x2004` | Identificador SNAP para DTP |
| VLAN nativa / access | `10 - VENTAS` | VLAN inicial del puerto vulnerable |
| VLAN objetivo | `20 - RRHH` | VLAN alcanzable tras obtener trunk |
| VLAN adicional | `999 - HACKEADO` | VLAN permitida en trunks del lab |
| Trunks permitidos | `10, 20, 999` | VLANs habilitadas en el enlace troncal |
| Tiempo de ataque | `120 segundos` | Duración del envío de paquetes DTP |

### 📊 Matriz de Direccionamiento

| Equipo | Interfaz | Dirección IP | Descripción |
|:------:|:--------:|:------------:|-------------|
| SW1-CORE | Vlan1 | 10.25.7.1/24 | Administración switch principal |
| SW2 | Vlan1 | 10.25.7.2/24 | Administración switch secundario |
| Atacante | ens3 | 10.25.10.99/24 | Dirección en VLAN 10 |
| Atacante | ens3.20 | 10.25.20.99/24 | Subinterfaz 802.1Q hacia VLAN 20 |
| VPC1 | eth0 | 10.25.10.10/24 | Host en VLAN 10 |
| VPC2 | eth0 | 10.25.20.20/24 | Host en VLAN 20 |

### 📊 VLANs Utilizadas

| VLAN ID | Nombre | Rol | Descripción |
|:-------:|:------:|:---:|-------------|
| 10 | VENTAS | Access / Native | VLAN de usuario y native VLAN del puerto vulnerable |
| 20 | RRHH | Objetivo | VLAN a la que el atacante accede tras obtener trunk |
| 999 | HACKEADO | Permitida en trunk | VLAN adicional del laboratorio |

### 📊 Topología de Conexiones

| Equipo | Interfaz | Conexión / Rol | VLAN / Detalle |
|:------:|:--------:|:--------------:|:--------------:|
| SW1-CORE | e0/1 | Access hacia VPC2 | VLAN 20 |
| SW1-CORE | e0/2 | Trunk hacia SW2 | VLANs 10, 20, 999 |
| SW1-CORE | e0/3 | **Puerto vulnerable hacia atacante** | dynamic auto / native VLAN 10 |
| SW2 | e0/0 | Trunk hacia SW1-CORE | VLANs 10, 20, 999 |
| SW2 | e0/1 | Access hacia VPC1 | VLAN 10 |
| Atacante Linux | ens3 | Interfaz de ataque DTP | Capa 2 / DTP |

---

## ⚙️ Requisitos

```bash
# Sistema Operativo
Ubuntu Linux (recomendado)

# Dependencias
sudo apt update && sudo apt install -y python3 python3-pip tcpdump
sudo pip3 install scapy

# Privilegios requeridos
sudo / root
```

---

## 🔧 Configuración Base de los Switches

### SW1-CORE (Puerto Vulnerable)
```cisco
enable
configure terminal
vlan 10
 name VENTAS
vlan 20
 name RRHH
interface ethernet 0/3
 description PUERTO_VULNERABLE_DTP_HACIA_ATACANTE
 no switchport nonegotiate
 switchport trunk encapsulation dot1q
 switchport mode dynamic auto
 switchport access vlan 10
 switchport trunk native vlan 10
 switchport trunk allowed vlan 10,20,999
 no shutdown
end
write memory
```

### SW2
```cisco
enable
configure terminal
vlan 10
 name VENTAS
vlan 20
 name RRHH
interface ethernet 0/0
 switchport trunk encapsulation dot1q
 switchport mode trunk
 switchport trunk allowed vlan 10,20,999
 no shutdown
interface ethernet 0/1
 switchport mode access
 switchport access vlan 10
 no shutdown
end
write memory
```

---

## 🚀 Uso

```bash
# Ejecutar el ataque (interfaz ens3, dominio LAB, 120 segundos)
sudo python3 dtp_vlan_hopping.py -i ens3 -d LAB -s 120

# Parámetros disponibles
# -i / --iface    Interfaz atacante (default: ens3)
# -d / --domain   Dominio DTP/VTP  (default: LAB)
# -s / --seconds  Tiempo de envío  (default: 90)
# -t / --interval Intervalo entre paquetes en segundos (default: 1.0)

# Verificar conversión a trunk en SW1-CORE
SW1# show interfaces e0/3 switchport
SW1# show interfaces trunk

# Resultado esperado
# Operational Mode: trunk
# Et0/3 aparece en show interfaces trunk con VLANs 10,20,999
```

### Acceso a VLAN objetivo tras obtener trunk
```bash
# Crear subinterfaz 802.1Q hacia VLAN 20
sudo modprobe 8021q
sudo ip link add link ens3 name ens3.20 type vlan id 20
sudo ip addr add 10.25.20.99/24 dev ens3.20
sudo ip link set ens3.20 up

# Probar acceso a host en VLAN 20
ping 10.25.20.20
```

---

## 🔬 ¿Cómo funciona?

| Fase | Descripción |
|:----:|-------------|
| 1️⃣ **Construcción L2** | Usa `Dot3 + LLC + SNAP` para crear tramas compatibles con protocolos propietarios Cisco |
| 2️⃣ **PID DTP** | Configura SNAP con OUI `0x00000c` y PID `0x2004` — identificador exclusivo de DTP |
| 3️⃣ **TLV Domain** | Incluye el dominio `LAB` para coincidir con la configuración del switch |
| 4️⃣ **TLV Status** | Valor `0x03` simula modo **desirable** — induce al puerto `dynamic auto` a aceptar trunk |
| 5️⃣ **TLV Type** | Valor `0xa5` indica negociación de trunk **802.1Q** |
| 6️⃣ **TLV Neighbor** | Incluye la MAC de `ens3` como vecino DTP |
| 7️⃣ **Envío recurrente** | Envía paquetes cada segundo durante el tiempo definido para mantener la negociación activa |
| 8️⃣ **Resultado** | El puerto e0/3 pasa de `Operational Mode: static access` → `Operational Mode: trunk` |

### Estructura del Paquete DTP Malicioso

| Capa | Campo | Valor |
|:----:|:-----:|-------|
| L2 Ethernet 802.3 | `dst` | `01:00:0c:cc:cc:cc` (Multicast Cisco) |
| LLC | `dsap/ssap/ctrl` | `0xAA / 0xAA / 0x03` |
| SNAP | `OUI / PID` | `00:00:0C` / `0x2004` (DTP) |
| DTP | Version | `0x01` |
| TLV 0x0001 | Domain | `LAB` |
| TLV 0x0002 | Status | `0x03` (desirable) |
| TLV 0x0003 | Type | `0xa5` (trunk 802.1Q) |
| TLV 0x0004 | Neighbor | MAC del atacante |

---

## 🛡️ Contramedidas

### Deshabilitar DTP y forzar puerto como access
```cisco
configure terminal
interface ethernet 0/3
 description PUERTO_MITIGADO_HACIA_ATACANTE
 switchport mode access
 switchport access vlan 10
 switchport nonegotiate
 spanning-tree portfast
 spanning-tree bpduguard enable
end
write memory
```

### Resumen de mitigaciones

| Medida | Efecto |
|:------:|--------|
| `switchport mode access` | Elimina la negociación dinámica — el puerto no puede convertirse en trunk |
| `switchport nonegotiate` | Deshabilita DTP completamente en el puerto |
| `spanning-tree portfast` | Habilita PortFast para puertos de usuario final |
| `spanning-tree bpduguard enable` | Apaga el puerto (`err-disable`) si recibe algún BPDU |
| No usar `dynamic auto` / `dynamic desirable` | Nunca dejar puertos de usuario con negociación activa |
| Limitar VLANs en trunks reales | Reduce la superficie de ataque VLAN Hopping |
| Apagar puertos no utilizados | Elimina vectores de ataque inactivos |

---

## 📊 Resultados del Laboratorio

| Prueba | Resultado |
|:------:|:---------:|
| Estado inicial e0/3: dynamic auto / static access | ✅ Confirmado |
| Script envía paquetes DTP desde ens3 | ✅ Exitoso |
| e0/3 cambia a Operational Mode: trunk | ✅ Exitoso |
| Et0/3 aparece en `show interfaces trunk` | ✅ Exitoso |
| Acceso a VLAN 20 vía subinterfaz ens3.20 | ✅ Exitoso |
| Mitigación: access + nonegotiate aplicados | ✅ Aplicada |

---

## 📁 Archivos del Repositorio

| Archivo | Descripción |
|:-------:|-------------|
| [`dtp_vlan_hopping.py`](dtp_vlan_hopping.py) | Script principal del ataque |
| [`SaelGermanGarcia_2025-0725_DTPVLANHopping_P1.pdf`](SaelGermanGarcia_2025-0725_DTPVLANHopping_P1.pdf) | Documentación técnica completa |

---

## 🖼️ Capturas de Pantalla

- 📸 [Topología PNETLab del laboratorio DTP VLAN Hopping](Capturas%20de%20Pantalla%20DTP%20VLAN%20HOPPING/Topologia%20PNETLab%20del%20laboratorio%20DTP%20VLAN%20Hopping.png)
- 📸 [Estado inicial de e0/3: Administrative Mode dynamic auto y Operational Mode static access](Capturas%20de%20Pantalla%20DTP%20VLAN%20HOPPING/Estado%20inicial%20de%20e03%20Administrative%20Mode%20dynamic%20auto%20y%20Operational%20Mode%20static%20access.png)
- 📸 [Estado inicial de trunks: solo Et0/2 aparece como trunk antes del ataque](Capturas%20de%20Pantalla%20DTP%20VLAN%20HOPPING/Estado%20inicial%20de%20trunks%20solo%20Et02%20aparece%20como%20trunk%20antes%20del%20ataque.png)
- 📸 [Ejecución del script DTP desde la máquina atacante Linux](Capturas%20de%20Pantalla%20DTP%20VLAN%20HOPPING/Ejecucion%20del%20script%20DTP%20desde%20la%20maquina%20atacante%20Linux.png)
- 📸 [Verificación posterior: e0/3 cambia a Operational Mode trunk](Capturas%20de%20Pantalla%20DTP%20VLAN%20HOPPING/Verificacion%20posterior%20e03%20cambia%20a%20Operational%20Mode%20trunk.png)
- 📸 [Verificación posterior: Et0/3 aparece en show interfaces trunk como enlace trunking](Capturas%20de%20Pantalla%20DTP%20VLAN%20HOPPING/Verificacion%20posterior%20Et03%20aparece%20en%20show%20interfaces%20trunk%20como%20enlace%20trunking.png)
- 📸 [Aplicación de contramedida: e0/3 forzado como access y DTP deshabilitado](Capturas%20de%20Pantalla%20DTP%20VLAN%20HOPPING/Aplicacion%20de%20contramedida%20e03%20forzado%20como%20access%20y%20DTP%20deshabilitado.png)

---

## 📎 Recursos

📄 **Documentación Técnica:** [Ver Informe PDF](SaelGermanGarcia_2025-0725_DTPVLANHopping_P1.pdf)  
▶️ **Video Demostración:** [Ver en YouTube](https://www.youtube.com/playlist?list=PLV_dKVnYXf6f67jGkXDf8d4dPSeYV39qM)

---

## 📚 Referencias

1. Cisco Systems. *Dynamic Trunking Protocol and Trunk/Access Port Configuration Guide*. Documentación oficial de Cisco IOS.
2. Scapy Project. *Scapy: Packet crafting and network manipulation framework*. [https://scapy.net/](https://scapy.net/)
3. PNETLab. *Plataforma de emulación de redes*. Entorno utilizado para el laboratorio.
4. Reconocimiento especial: Troubleshooting, base del script y documentación apoyado en Inteligencia Artificial.

---

<div align="center">

⚠️ **AVISO LEGAL** ⚠️  
*Este script fue desarrollado exclusivamente con fines académicos y educativos.*  
*Su uso en redes sin autorización explícita es ilegal y éticamente inaceptable.*

</div>
