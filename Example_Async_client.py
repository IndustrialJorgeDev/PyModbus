"""
Este código configura un cliente asíncrono para conectarse a un servidor Modbus usando diferentes protocolos de comunicación (TCP, UDP, serial, TLS). 
Realiza una lectura de coils y maneja posibles excepciones de Modbus, cerrando la conexión adecuadamente después de la operación.

"""

import asyncio  # Importa la biblioteca asyncio para la programación asíncrona

import pymodbus.client as ModbusClient  # Importa la clase ModbusClient del módulo pymodbus

from pymodbus import (  # Importa varias excepciones y configuraciones del módulo pymodbus
    ExceptionResponse,
    Framer,
    ModbusException,
    pymodbus_apply_logging_config,
)

async def run_async_simple_client(comm, host, port, framer=Framer.SOCKET):
    """Ejecuta un cliente asíncrono."""
    # Activa la depuración
    pymodbus_apply_logging_config("DEBUG")

    print("Obtener cliente")
    # Selecciona el tipo de cliente Modbus según el protocolo de comunicación (comm)
    if comm == "tcp":
        client = ModbusClient.AsyncModbusTcpClient(
            host,
            port=port,
            framer=framer,
            # timeout=10,
            # retries=3,
            # retry_on_empty=False,
            # source_address=("localhost", 0),
        )
    elif comm == "udp":
        client = ModbusClient.AsyncModbusUdpClient(
            host,
            port=port,
            framer=framer,
            # timeout=10,
            # retries=3,
            # retry_on_empty=False,
            # source_address=None,
        )
    elif comm == "serial":
        client = ModbusClient.AsyncModbusSerialClient(
            port,
            framer=framer,
            # timeout=10,
            # retries=3,
            # retry_on_empty=False,
            # strict=True,
            baudrate=9600,
            bytesize=8,
            parity="N",
            stopbits=1,
            # handle_local_echo=False,
        )
    elif comm == "tls":
        client = ModbusClient.AsyncModbusTlsClient(
            host,
            port=port,
            framer=Framer.TLS,
            # timeout=10,
            # retries=3,
            # retry_on_empty=False,
            # sslctx=sslctx,
            certfile="../examples/certificates/pymodbus.crt",
            keyfile="../examples/certificates/pymodbus.key",
            # password="none",
            server_hostname="localhost",
        )
    else:
        print(f"Cliente desconocido {comm} seleccionado")
        return

    print("Conectar al servidor")
    await client.connect()  # Conecta al servidor de forma asíncrona
    # Verifica si el cliente está conectado
    assert client.connected

    print("Obtener y verificar datos")
    try:
        # Realiza una lectura de los coils (bobinas) Modbus
        rr = await client.read_holding_registers(1, 1, slave=1)
    except ModbusException as exc:
        print(f"Recibió ModbusException({exc}) de la biblioteca")
        client.close()
        return
    # Verifica si hubo un error en la respuesta
    if rr.isError():
        print(f"Recibió un error de la biblioteca Modbus({rr})")
        client.close()
        return
    # Verifica si la respuesta es una excepción de Modbus
    if isinstance(rr, ExceptionResponse):
        print(f"Recibió una excepción de la biblioteca Modbus ({rr})")
        # ESTO NO ES UNA EXCEPCIÓN DE PYTHON, sino un mensaje válido de Modbus
        client.close()

    print("Cerrar conexión")
    client.close()  # Cierra la conexión

# Punto de entrada principal del script
if __name__ == "__main__":
    asyncio.run(
        run_async_simple_client("tcp", "192.168.2.4", 502), debug=True
    )
