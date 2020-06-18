import asyncio
import socket
import os

COM_PORT = 8888
DATA_PORT = 8889

async def transfer_data(reader, writer, data):
     writer.write(data.encode())
     await writer.drain()
     writer.write_eof()

def listen_raw_connection():
    pass

async def client(message):
    reader, writer = await asyncio.open_connection('127.0.0.1', 8888)

    await transfer_data(reader, writer, message)
    data = await reader.read()

    if data.decode() == "ack":
        print("command recieved")

    writer.close()
     
asyncio.run(client('store'))

async def send_file_name():
    listener_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    listener_sock.bind(('127.0.0.1', 8889))
    listener_sock.listen()
    conn, addr = listener_sock.accept()

    n_reader, n_writer = await asyncio.open_connection(sock=conn)
    await transfer_data(n_reader, n_writer, "example_file_name.txt")
    listener_sock.close()

async def send_file_data():
    pass
asyncio.run(send_file_name())
# code can be run after this
# currently working on getting an asynchronous transport client side(or just sucessfully sending data

