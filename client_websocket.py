# client_websocket.py
import asyncio
import websockets
import socket

TCP_SERVER_HOST = "127.0.0.1"
TCP_SERVER_PORT = 9001

connected_clients = set()

async def handle_websocket(websocket, path):
    # Connexion au serveur TCP
    tcp_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    tcp_socket.connect((TCP_SERVER_HOST, TCP_SERVER_PORT))

    connected_clients.add(websocket)
    try:
        async def receive_from_web():
            async for message in websocket:
                tcp_socket.send(message.encode('utf-8'))

        async def receive_from_tcp():
            while True:
                data = tcp_socket.recv(128)
                if not data:
                    break
                await websocket.send(data.decode('utf-8'))

        await asyncio.gather(receive_from_web(), receive_from_tcp())

    except websockets.exceptions.ConnectionClosed:
        pass
    finally:
        connected_clients.remove(websocket)
        tcp_socket.close()

# Lancer un serveur WebSocket sur le port 6789
start_server = websockets.serve(handle_websocket, "localhost", 6789)

asyncio.get_event_loop().run_until_complete(start_server)
print("WebSocket server started on ws://localhost:6789")
asyncio.get_event_loop().run_forever()
