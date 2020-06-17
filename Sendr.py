import asyncio
import socket
import os

COM_PORT = 8888

async def transfer_data(reader, writer, data):
     writer.write(data.encode())
     await writer.drain()
     writer.write_eof()

async def client(message):
    reader, writer = await asyncio.open_connection('127.0.0.1', 8888)

    await transfer_data(reader, writer, message)
    data = await reader.read()

    if data.decode() == "ack":
        print("command recieved")

    writer.close()
 
asyncio.run(client('store'))

listener_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
listener_sock.bind(('127.0.0.1', 8889))
listener_sock.listen()
conn, addr = listener_sock.accept()

# code can be run after this
# currently working on getting an asynchronous transport client side(or just sucessfully sending data

