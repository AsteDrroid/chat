from flask import Flask, render_template_string, request
from flask_socketio import SocketIO, send
import socket
import threading

# Connexion au serveur TCP (server.py)
tcp_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
tcp_socket.connect(("127.0.0.1", 9001))

# Création serveur Flask
app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*")

# HTML en string (comme un fichier index.html)
html = """
<!DOCTYPE html>
<html lang="fr">
<head>
  <meta charset="UTF-8">
  <title>Chat Web</title>
  <style>
    body { font-family: Arial; margin: 20px; }
    #chat { border: 1px solid #ccc; padding: 10px; height: 300px; overflow-y: scroll; }
    #message { width: 80%; }
  </style>
</head>
<body>
  <h2>Chat en ligne</h2>
  <label>Nom : <input type="text" id="nom" /></label>
  <div id="chat"></div>
  <input type="text" id="message" placeholder="Votre message..." />
  <button onclick="sendMessage()">Envoyer</button>

  <script src="https://cdn.socket.io/4.3.2/socket.io.min.js"
    integrity="sha384-LfQ3fE5omTYq5sGKmzChpMp2IjTFqn+LkePS1I7u66UzYYu0pEK0rD94Y2FqAT0B"
    crossorigin="anonymous"></script>
  <script>
    const socket = io();
    const nomInput = document.getElementById('nom');
    const messageInput = document.getElementById('message');
    const chatDiv = document.getElementById('chat');

    socket.on('message', (data) => {
      const msg = document.createElement('div');
      msg.textContent = data;
      chatDiv.appendChild(msg);
      chatDiv.scrollTop = chatDiv.scrollHeight;
    });

    function sendMessage() {
      const nom = nomInput.value;
      const msg = messageInput.value;
      if (nom && msg) {
        socket.send(`${nom} > ${msg}`);
        messageInput.value = '';
      }
    }
  </script>
</body>
</html>
"""

# Route principale : page web
@app.route("/")
def index():
    return render_template_string(html)

# Message reçu du navigateur → on l'envoie au serveur TCP
@socketio.on("message")
def handle_message(msg):
    tcp_socket.send(msg.encode("utf-8"))

# Écoute en parallèle des messages du serveur TCP → envoie au navigateur
def receive_from_tcp():
    while True:
        try:
            data = tcp_socket.recv(128)
            if data:
                socketio.emit("message", data.decode("utf-8"))
        except:
            break

# 🔁 Thread pour écouter le serveur TCP
threading.Thread(target=receive_from_tcp, daemon=True).start()

# ✅ MAIN — fichier principal à exécuter
if __name__ == "__main__":
    print("Serveur Web disponible sur http://localhost:5000")
    socketio.run(app, host="0.0.0.0", port=5000)
