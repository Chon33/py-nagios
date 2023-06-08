# Info stuff
import platform
import socket
import re
import uuid
import psutil
import logging
import cpuinfo

# Server stuff
import asyncio

# Funciones para obtener la infor del PC   ( MUY obtimizables y lentas ^^" )
# Se obtiene la información en bytes, la divido entre 1024^3 para pasarlo a Gb

def getRAMInfo() -> dict | None:
    try:
        ram = {}
        vram = psutil.virtual_memory()
        ram['installed'] = round(vram.total / (1024.0 ** 3))
        ram['available'] = round(vram.available / (1024 ** 3), 2)
        ram['percent'] = vram.percent
        ram['used'] = round(vram.used / (1024 ** 3), 2)

        return ram

    except Exception as e:
        logging.exception(e)

def getCPUInfo() -> dict | None:
    try:
        mycpuinfo = cpuinfo.get_cpu_info()
        cpu = {}
        cpu['processor'] = mycpuinfo['brand_raw']
        cpu['cores'] = mycpuinfo['count']
        cpu['arch'] = mycpuinfo['arch']
        cpu['currentload'] = psutil.cpu_percent()
        cpu['coreloads'] = psutil.cpu_percent(interval=1, percpu=True)
        return cpu

    except Exception as e:
        logging.exception(e)

def getSystemInfo() -> dict | None:
    try:
        info = {}
        info['hostname'] = socket.gethostname()
        info['system'] = f"{platform.system()} {platform.version()}"
        info['architecture'] = platform.machine()
        info['ip-address'] = socket.gethostbyname(socket.gethostname())
        # "re" se usa para expresiones, en este caso ".." significa, cada dos dígitos
        # '%012x' sirve para formatear en hex y cada dos números y añadir los :
        info['mac-address'] = ':'.join(re.findall('..',
                                       '%012x' % uuid.getnode()))
        
        disks = psutil.disk_partitions()

        info['disks'] = {}

        for disk in disks:
            if disk.fstype:
                disk_size_info = psutil.disk_usage(disk.mountpoint)
                info['disks'][disk.mountpoint] = {
                    "mountpoint": disk.mountpoint,
                    "fs": disk.fstype,
                    "size": round(disk_size_info.total / (1024 ** 3), 2),
                    "used": round(disk_size_info.used / (1024 ** 3), 2),
                    "free": round(disk_size_info.free / (1024 ** 3), 2),
                    "percent": disk_size_info.percent
                }

        return info
    except Exception as e:
        logging.exception(e)

def getAllInfo() -> dict | str:
    dic = {}
    system_info = {}
    cpu_info = {}
    ram_info = {}

    system_info = getSystemInfo()

    if system_info is not None:
        #dic['nickname'] = nickname
        dic['system'] = system_info
        cpu_info = getCPUInfo()
        ram_info = getRAMInfo()

        if cpu_info is not None:
            dic['cpu'] = cpu_info  # si tenemos la info del cpu, la ponemos

        if ram_info is not None:
            dic['ram'] = ram_info  # si tenemos la info del ram, la ponemos

        return dic  # si todo va bien, y no hay errores te lo devuelve todo

    else:
        return "Te comes un moco xula"  # si hay problemas, pues te comes un moquillo


# Parte de servidor
#HOST = socket.gethostbyname(socket.gethostname()) # IP del servidor
HOST = input("IP del servidor: ") # esto se podría mejorar y hacer que el cliente busque solo al servidor, algo asi como el ARP
PORT = 3434

nickname = input("Ponle un nombre bonito a este PC: ")


# Ejecuta una nueva conexión, y es prácticamente donde todo ocurre
async def run_client() -> None:
    reader, writer = await asyncio.open_connection(HOST, PORT) # Nos conectamos

    writer.write(f"K pasa su xula?".encode()) # Llenamos el buffer con un mensaje bonito, es como el handshake de http, pero de xulas
    await writer.drain() # Enviamos este bello mensaje

    b_quit = False

    # Los prints los he usado para no volverme loca haciendolo :) es muy chusquero, pero me ha ayudado mucho ( tengo q buscarme un tutorial del debugger )
    # Mientras no le des a Ctrl + C
    while not b_quit:
        try:
            print("waiting for reply") 
            data = await reader.read(1024)  # Leemos los datos recibidos
            msg = data.decode() # bytes a string
            print(msg) 

            msg = getAllInfo() # Preparamos un nuevo mensaje

            # Si la variable msg no es una str ( si no ha explotado nada )
            if isinstance(msg, str):
                break

            msg['nickname'] = nickname
            
            writer.write(bytes(str(msg), 'utf-8')) # Rellenamos el buffer con la info del PC
            await writer.drain() # Y lo mandamos
            print("sent")

        
        # Si das CTRL + C, parar todo
        except KeyboardInterrupt:
            writer.write(b'bye xula') # Decirle al servidor que nos desconectamos
            await writer.drain()
            b_quit = True


# Main Function
if __name__ == "__main__":
    loop = asyncio.new_event_loop() # Creamos un event handler
    loop.run_until_complete(run_client()) # Le decimos que use nuestro cliente
