import socket
import json
import threading
import random

HOST = '127.0.0.1' 
PORT = 12345  

game_state = {
    "players": {},
    "player_turn": None,
    "current_round": 1,
    "status": "waiting_players"
}

bullets = None

connected_players = 0

def create_bullets():
    quantity_bullets = random.randint(7, 8)
    bullets = []
    has_true = False
    has_false = False

    for _ in range(quantity_bullets):
        bool = random.choice([True, False])
        bullets.append(bool)
        if bool:
            has_true = True
        else:
            has_false = True

    if not has_true:
        index = random.randint(0, quantity_bullets - 1)
        bullets[index] = True
    if not has_false:
        index = random.randint(0, quantity_bullets - 1)
        bullets[index] = False

    random.shuffle(bullets)

    return bullets

def handle_client(client_socket, player_id):
    global connected_players
    try:
        while True:
            message = client_socket.recv(4096).decode()
            data = json.loads(message)

            if data["type"] == "START_GAME":
                handle_start_game(data, player_id)
    
            elif data["type"] == "PLAYER_ACTION":
                handle_player_action(data)

    except Exception as e:
        print("Erro ao lidar com a mensagem do cliente:", e)
        del game_state["players"][player_id]
        connected_players -= 1
        print('Jogador desconectado. Jogadores online:', connected_players)
        client_sockets.remove(client_socket)
        client_socket.close()
        if connected_players < 2:
            send_game_ended_to_all_clients(("Jogo encerrado. Não há jogadores suficientes para continuar.",))
        else:
            send_game_ended_to_all_clients(("Jogador desconectado. O jogo foi encerrado.",))

def handle_start_game(data, player_id):
    global connected_players
    player_name = data["player_name"]
    game_state["players"][player_id] = {"id": player_id, "name": player_name, "lives": 3, "items": []}
    connected_players += 1
    
    if connected_players == 2:
        global bullets 
        bullets = create_bullets()
        game_state["player_turn"] = 1

        send_initial_game_state_to_all_clients()

def send_initial_game_state_to_all_clients():
    try:
        if game_state["status"] == "waiting_players":
            game_state["status"] = "started"
            game_started_json = {
                "type": "GAME_STARTED",
                "initial_state": game_state
            }
            game_started_json_str = json.dumps(game_started_json)

            for client_socket in client_sockets:
                client_socket.send(game_started_json_str.encode())
    except Exception as e:
        print("Erro ao enviar o estado inicial do jogo para o cliente:", e)

def handle_player_action(data):
    global game_state
    if data["action"]["type"] == "shoot":
        target_player_id = data["action"]["target_player_id"]
        current_bullet = bullets.pop(0)
        if current_bullet is True:
            game_state["players"][target_player_id]["lives"] -= 1
            game_state["player_turn"] = (game_state["player_turn"] % len(game_state["players"])) + 1
            if game_state["players"][target_player_id]["lives"] == 0:
                game_state["status"] = "ended"
        else:
            if data["player_id"] != target_player_id:
              game_state["player_turn"] = (game_state["player_turn"] % len(game_state["players"])) + 1
    else:
        print(data["action"]["type"])
    send_game_state_to_all_clients()

def send_game_state_to_all_clients():
    try:
        game_state_json = {
            "type": "GAME_STATE",
            "game_state": game_state
        }
        game_state_json_str = json.dumps(game_state_json)

        for client_socket in client_sockets:
            client_socket.send(game_state_json_str.encode())
    except Exception as e:
        print("Erro ao enviar o estado do jogo para o cliente:", e)

def send_game_ended_to_all_clients(message):
    try:
        game_state["status"] = "ended"
        game_state_json = {
            "type": "GAME_ENDED",
            "game_state": game_state,
            "message": message
        }
        game_state_json_str = json.dumps(game_state_json)

        for client_socket in client_sockets:
            client_socket.send(game_state_json_str.encode())
            print("enviado para: ", client_socket)
    except Exception as e:
        print("Erro ao enviar o estado do jogo para o cliente:", e)
    

client_sockets = []

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server:
    server.bind((HOST, PORT))
    
    server.listen()
    
    print('Servidor escutando em {}:{}'.format(HOST, PORT))
    
    while True:
        connection, endereco_cliente = server.accept()
        print('Conectado por', endereco_cliente)
        
        client_sockets.append(connection)

        player_id = len(client_sockets)
        response = {"player_id": player_id}
        connection.send(json.dumps(response).encode())
        
        threading.Thread(target=handle_client, args=(connection, len(client_sockets))).start()
