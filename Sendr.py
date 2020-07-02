import asyncio
import socket
import click
import os

COM_PORT = 8888
DATA_PORT = 8889

def conf_ip(path):
    '''
    path(string): path to conf file
    return(int): the ip used for the server 
    '''
    with open(path, 'r') as reader:
        data  = reader.readlines()
        client_ip = data[0][4:-1]
        server_ip = data[1][11:-1]
        return (client_ip, server_ip)

ADDRESSES = conf_ip("./conf/conf.txt")

async def transfer_data_encoded(writer, data):
     writer.write(data.encode())
     await writer.drain()
     writer.write_eof()

async def transfer_data_raw(writer, data):
     writer.write(data)
     await writer.drain()
     writer.write_eof()

async def send_command(command, server_ip):
    '''
    command(string): the command being sent to the server 
    server_ip(string): the ip address of the server being connected to
    ''' 
    reader, writer = await asyncio.open_connection(server_ip, 8888)

    await transfer_data_encoded(writer, command)
    data = await reader.read()
    
    writer.close()

async def send_file_name(file_name, addr):
    '''
    file_name(string): name of the file to send
    addr(tuple): contains the ip and port the socket should listen on
    the socket must listen on port 8889 as that is the data port being used to send data
    previous bind('127.0.0.1', 8889)                                                        
    '''
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock: 
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sock.bind(addr)
        sock.listen()

        conn, addr = sock.accept()

        reader, writer = await asyncio.open_connection(sock=conn)

        await transfer_data_encoded(writer, file_name)

async def send_file_data(file_name, addr):
    '''
    addr(tuple): contains the ip and port the socket should listen on
    file_name(string): the name of the file being sent
    PORT MUST BE 8889 PREVIOUS BIND CALL -> ('127.0.0.1', 8889)
    '''
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sock.bind(addr)
        sock.listen()
        conn, addr = sock.accept()

        reader, writer = await asyncio.open_connection(sock=conn)

        with open(file_name, 'rb') as file_reader:
                data = file_reader.read()
                writer.write(data)
                await writer.drain()
                writer.write_eof()


async def recv_file_presence(addr):
    '''
    recv whether the file exists on the server or not
    addr(tuple): contains the ip and port the socket should listen on
    return(boolean): true if the file exists, false if it doesn't
    PORT MUST BE 8889 PREVIOUS BIND CALL -> ('127.0.0.1', 8889)
    '''
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock: 
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sock.bind(addr) 
        sock.listen()
        conn, addr = sock.accept()

        reader, writer = await asyncio.open_connection(sock=conn) 

        presence = await reader.read()

        return presence.decode() == "prs"

async def recv_file(file_name, addr):
    '''
    file_name(string): name of the file being recv'd
    addr(tuple): contains the ip and port the socket should listen on
    PORT MUST BE 8889 PREVIOUS BIND CALL -> ('127.0.0.1', 8889)
    '''
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sock.bind(addr)                            
        sock.listen()                                                 
        conn, addr = sock.accept()                                    
                                                                               
        reader, writer = await asyncio.open_connection(sock=conn)          
        data = await reader.read()

        with open(file_name, 'wb') as writer:
            writer.write(data)

async def recv_dir_string(addr):
    '''
    connect to the server and recieve a list of files there
    addr(tuple): contains the ip and port the socket should listen on
    '''
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sock.bind(addr)                            
        sock.listen()                                                 
        conn, addr = sock.accept()                                    
                                                                               
        reader, writer = await asyncio.open_connection(sock=conn)          
        data = await reader.read()
        
        return data.decode()

async def recv_command(file_name):
    '''
    when called it will query the server for the file specified and will retrieve it if present
    file_name(string): name of the file to recieve
    '''
    await send_command('recv', ADDRESSES[1])
    await send_file_name(file_name, (ADDRESSES[0], DATA_PORT) )
    present = await recv_file_presence( (ADDRESSES[0], DATA_PORT) ) 
    if present:
        await recv_file( file_name, (ADDRESSES[0], DATA_PORT) )
    else:
        print("ERROR: [FILENAME] not available in server")

async def show_command():
    '''
    when called it will connect to the server and recieve a list of files available to be served
    '''
    await send_command('show', ADDRESSES[1])
    print( await recv_dir_string( (ADDRESSES[0], DATA_PORT) ) )

async def store_command(file_name):
    '''
    when called it will send a file to the server to be stored
    '''
    await send_command('store', ADDRESSES[1])
    await send_file_name(file_name, (ADDRESSES[0], DATA_PORT))
    await send_file_data(file_name, (ADDRESSES[0], DATA_PORT))

@click.group()
def cli():
    pass

@click.command()
@click.option('--file', help='File being stored in server')
def store(file):
   asyncio.run(store_command(file)) 

@click.command()
@click.option('--file', help='File being recieved from  server')
def recv(file):
     asyncio.run(recv_command(file)) 

@click.command()
def show():
    asyncio.run(show_command()) 

cli.add_command(store)
cli.add_command(recv)
cli.add_command(show)

if __name__ == '__main__':
    cli()

