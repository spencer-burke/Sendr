import asyncio
import socket
import os

import asyncio

async def client(message):
    reader, writer = await asyncio.open_connection(
        '127.0.0.1', 8888)

    writer.write(message.encode())

    data = await reader.read()
    print(f'Received: {data.decode()!r}')

    print('Close the connection')
    writer.close()

asyncio.run(client('store'))

