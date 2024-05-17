import asyncio

import pymodbus.client as ModbusClient

from pymodbus import (
    ExceptionResponse,
    Framer,
    ModbusException,
    pymodbus_apply_logging_config,
)


async def run_async_simple_client(comm, host, port, framer=Framer.SOCKET):
    """Run async client."""
    # activate debugging
    pymodbus_apply_logging_config("DEBUG")

    print("get client")
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
        print(f"Unknown client {comm} selected")
        return

    print("connect to server")
    await client.connect()
    # test client is connected
    assert client.connected

    print("get and verify data")
    try:
        # See all calls in client_calls.py
        rr = await client.read_coils(1, 1, slave=1)
    except ModbusException as exc:
        print(f"Received ModbusException({exc}) from library")
        client.close()
        return
    if rr.isError():
        print(f"Received Modbus library error({rr})")
        client.close()
        return
    if isinstance(rr, ExceptionResponse):
        print(f"Received Modbus library exception ({rr})")
        # THIS IS NOT A PYTHON EXCEPTION, but a valid modbus message
        client.close()

    print("close connection")
    client.close()


if __name__ == "__main__":
    asyncio.run(
        run_async_simple_client("tcp", "127.0.0.1", 5020), debug=True
    )