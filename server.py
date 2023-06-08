# Server stuff
import asyncio
import socket
from ast import literal_eval

# UI stuff
from rich.text import Text
from rich.panel import Panel
from rich.live import Live
from rich.console import Console
from rich.layout import Layout


# Funciones para formatear dictionarios (json) a strings

def sys_dict_to_str(pc: dict) -> str:

    disk_size_infos = "* Disks\n"

    for d in pc['system']['disks']:
        disk_size_infos += f"       - {pc['system']['disks'][d]['mountpoint']!r}\n"
        disk_size_infos += f"         · FileSystem: {pc['system']['disks'][d]['fs']}\n"
        disk_size_infos += f"         · Partition Size: {pc['system']['disks'][d]['size']} Gb\n"
        disk_size_infos += f"         · Used Space: {pc['system']['disks'][d]['used']} Gb\n"
        disk_size_infos += f"         · Free Space: {pc['system']['disks'][d]['free']} Gb\n"
        disk_size_infos += f"         · Percent: {pc['system']['disks'][d]['percent']}%\n"

    return f"""
    * Name: {pc['nickname']}
    * Hostname: {pc['system']['hostname']}
    * System: {pc['system']['system']}
    * Arch: {pc['system']['architecture']}
    * IP: {pc['system']['ip-address']}
    * MAC: {pc['system']['mac-address']}
    {disk_size_infos}
    """

def cpu_dict_to_str(pc: dict) -> str:
    coreloads = "* Core Loads\n"

    for i,l in enumerate(pc['cpu']['coreloads']):
        coreloads += f"       - Core {i+1}: {l}%\n"

    return f"""
    * CPU: {pc['cpu']['processor']}
    * CPU Load: {pc['cpu']['currentload']}
    * Cores: {pc['cpu']['cores']}
    {coreloads}
    """

def ram_dict_to_str(pc: dict) -> str:
    return f"""
    * Installed RAM: {pc['ram']['installed']} Gb
    * Available RAM: {pc['ram']['available']} Gb
    * Used RAM: {pc['ram']['used']} Gb
    * Percent: {pc['ram']['percent']}%
    """


# Elegimos una IP y un puerto para el servidor
HOST = socket.gethostbyname(socket.gethostname())  # Devuelve nuestra IP actual
print(HOST)
PORT = 3434

layout = Layout()
console = Console()

# Cada vez que recibamos algo, se ejecuta esta función
async def handle_echo(reader: asyncio.StreamReader, writer: asyncio.StreamWriter) -> None:
    data = None  # Variable para guardar los bytes que recibamos

    print("una xula se ha conectado!")

    writer.write(b"esa xunga!!") # devolvemos un mensaje bonito al cliente ("rellenamos" / preparamos el buffer del writer)
    await writer.drain() # "vaciamos" el writer (realmente, lo enviamos aquí)

    # Info de placeholder para crear la interfaz
    pc_info = {
        'nickname': '',
        'system': {'hostname': '', 'system': '', 'architecture': '', 'ip-address': '', 'mac-address': '',
                'disks': {
                    'None': {'mountpoint': '', 'fs': '', 'size': 0, 'used': 0, 'free': 0, 'percent': 0}
                        }
                },
        'cpu': {'processor': '', 'cores': 0, 'arch': '0', 'currentload': 0, 'coreloads': []},
        'ram': {'installed': 0, 'available': 0, 'percent': 0, 'used': 0}
    }

    # Montamos la interfaz
    layout = Layout()
    header = Text.assemble(
        ("Nagios peste de la Dani ", ""),
        ("<3", "bold red"),
        justify='center', style="cyan"
    )

    layout.split_column(
        Layout(header, size=1, name="header"),
        Layout(name="main"),
    )
    layout['main'].split_row(
        Layout(Panel(Text(sys_dict_to_str(pc_info))), name="system"),
        Layout(name="right")
    )

    layout['main']['right'].split_column(
        Layout(Panel(Text(cpu_dict_to_str(pc_info))), name="cpu"),
        Layout(Panel(Text(ram_dict_to_str(pc_info))), name="ram", size=8)
    )

    data = await reader.read(1024)  # leemos los datos
    msg = data.decode() # bytes a string

    writer.write(b"grasias corason") # devolvemos un mensaje bonito al cliente ("rellenamos" / preparamos el buffer del writer)
    await writer.drain() # "vaciamos" el buffer del writer (realmente, lo enviamos aquí)

    # Montamos la pantalla rexulona
    with Live(layout, screen=True, redirect_stderr=False, refresh_per_second=1) as live:
            while data != b'bye xula':
                data = await reader.read(1024)  # leemos los datos
                msg = data.decode() # bytes a string
                pc_info = literal_eval(msg) # string a diccionario

                writer.write(b"dime cosas") # devolvemos un mensaje bonito al cliente ("rellenamos" / preparamos el buffer del writer)
                await writer.drain() # "vaciamos" el writer (realmente, lo enviamos aquí)

                # Actualizamos la interfaz
                layout['main'].split_row(
                    Layout(Panel(Text(sys_dict_to_str(pc_info))), name="system"),
                    Layout(name="right")
                )

                layout['main']['right'].split_column(
                    Layout(Panel(Text(cpu_dict_to_str(pc_info))), name="cpu"),
                    Layout(Panel(Text(ram_dict_to_str(pc_info))), name="ram", size=8)
                )

                layout.update(layout)
                print("update")


    #with console.screen() as screen:
        # Si los datos que recibimos es "bye xula", salimos del bucle y cerramos el servidor


    # Cerrar el servidor
    writer.close()
    await writer.wait_closed()


# Le decimos al servidor que empiece a escuchar peticiones de nuevas conexiones
async def run_server() -> None:
    # creamos el server
    server = await asyncio.start_server(handle_echo, HOST, PORT)

    async with server:
        await server.serve_forever()  # le decimos que nunca pare


# Main funciton
if __name__ == "__main__":
    try:
        loop = asyncio.new_event_loop() # Crear el event handler
        loop.run_until_complete(run_server()) # Decirle que use mi server

    except KeyboardInterrupt:  # Si damos Ctrl + C ...
        pass  # ... No es del todo correcto pararlo así, se queja un poco, pero... para, que es lo importante :)
