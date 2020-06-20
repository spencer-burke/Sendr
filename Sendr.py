import asyncio
import socket
import click
import os

COM_PORT = 8888
DATA_PORT = 8889

async def transfer_data_encoded(reader, writer, data):
     writer.write(data.encode())
     await writer.drain()
     writer.write_eof()

async def transfer_data_raw(reader, writer, data):
     writer.write(data)
     await writer.drain()
     writer.write_eof()

# this function might be used to configure the socket
def listen_raw_connection():
    pass

async def send_command(command):
    reader, writer = await asyncio.open_connection('127.0.0.1', 8888)

    await transfer_data_encoded(reader, writer, command)
    data = await reader.read()

    if data.decode() == "ack":
        print("command recieved")

    writer.close()

async def send_file_name():
    listener_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    listener_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    listener_sock.bind(('127.0.0.1', 8889))
    listener_sock.listen()
    conn, addr = listener_sock.accept()

    n_reader, n_writer = await asyncio.open_connection(sock=conn)

    await transfer_data_encoded(n_reader, n_writer, "example_text_file.txt")

    listener_sock.close()

async def send_file_data():
    listener_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    listener_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    listener_sock.bind(('127.0.0.1', 8889))
    listener_sock.listen()
    conn, addr = listener_sock.accept()

    n_reader, n_writer = await asyncio.open_connection(sock=conn)

    with open("example_text_file.txt", 'rb') as file_reader:
        data = file_reader.read()
        n_writer.write(data)
        await n_writer.drain()
        n_writer.write_eof()

    listener_sock.close()

async def send_file():
    await send_command('store')
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as writer_sock:
        writer_sock.bind(('127.0.0.1', DATA_PORT))
        # listen for the server connecting for the file data 
        writer_sock.listen()
        # accept server connection
        conn, addr = writer_sock.accept()
        
        # open asynchronous acception
        n_reader, n_writer = await asyncio.open_connection(sock=conn)
        
        # send the name of the file
        await transfer_data_encoded(n_reader, n_writer, "example_text_file.txt") 
        # get an acknowledgement
        response = await n_reader.read() 
        #n_writer.close()
        #await n_writer.wait_closed()
        
        d_reader, d_writer = await asyncio.open_connection(sock=conn)
    
        file_writer = open("example_text_file.txt", 'rb')
        data = file_writer.read()
        print(data)
        d_writer.write(data)
        await d_writer.drain()
        d_writer.close()
        print("sucessfully sent file")

asyncio.run(send_command('store'))
asyncio.run(send_file_name())
asyncio.run(send_file_data())
#asyncio.run(send_file())
# currently working on a better way to recieve data being the socket keeps getting used repeatedly

@click.group()
def cli():
    pass

@click.command()
def store():
    pass

@click.command()
def recv():
    pass

@click.command()
def show():
    pass

cli.add_command(store)
cli.add_command(recv)
cli.add_command(show)

if __name__ == '__main__':
    cli()
