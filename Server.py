import eventlet
eventlet.monkey_patch()  # MUITO IMPORTANTE: antes de qualquer outra coisa

from flask import Flask, render_template
from flask_socketio import SocketIO, join_room, emit
import random, string


eventlet.monkey_patch()  # necessário para WebSocket funcionar via tunnel

app = Flask(__name__)
socketio = SocketIO(
    app, 
    cors_allowed_origins="*",
    async_mode='eventlet',
    ping_timeout=60,
    ping_interval=25,
    engineio_logger=True,
    logger=True
)

def gerar_codigo():
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/debug")
def debug():
    return render_template("debug.html")

@app.route("/criar")
def criar():
    codigo = gerar_codigo()
    return render_template("Criar.html", codigo=codigo)

@app.route("/entrar")
def entrar():
    return render_template("entrar.html")

@app.route("/sala/<codigo>")
def sala(codigo):
    return render_template("chat.html", codigo=codigo)

@socketio.on("join")
def join(data):
    username = data["username"]
    room = data["room"]
    join_room(room)
    print(f"✓ {username} entrou na sala {room}")
    emit("message", f"{username} entrou na sala!", to=room)

@socketio.on("message")
def message_handler(data):
    room = data.get("room")
    msg = data.get("msg")
    user = data.get("user")
    if room and msg and user:
        message_text = f"{user}: {msg}"
        print(f"[{room}] {message_text}")
        emit("message", message_text, to=room)
    else:
        print(f"✗ Erro: dados inválidos - {data}")

if __name__ == "__main__":
    print("A arrancar o servidor com Eventlet...")
    socketio.run(app, host="0.0.0.0", port=5000)
