import socket
import json
import time

HOST = '127.0.0.1'
PORT = 12345  

actual_game_state = None


def enviar_json_para_servidor(data, client):
    data_json = json.dumps(data)
    
    client.sendall(data_json.encode())

    resposta = client.recv(1024)
    return resposta.decode()

def handle_player_action():
    acao = input("Escolha sua ação (shoot para atirar, self para atirar em si mesmo): ")
    target = 0

    if acao == "shoot" or acao == "self":
        target
        dados_jogada = {
          "type": "PLAYER_ACTION",
          "player_id": player_id,
          "action": {
          "type": acao.lower(),
          "target_player_id": 1
          }}
                    
    return enviar_json_para_servidor(dados_jogada, client)

if __name__ == "__main__":
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client:
        client.connect((HOST, PORT))

        player_name = input("Digite o nome do jogador: ")
        
        dados_iniciais = {
            "type": "START_GAME",
            "player_name": player_name
        }
        
        response = enviar_json_para_servidor(dados_iniciais, client)
        player_id = json.loads(response).get("player_id") 

        while True:
            message = client.recv(4096).decode()
            data = json.loads(message)
            print(data)
            if data["type"] == "GAME_STARTED":
                actual_game_state = data["initial_state"]
                if actual_game_state["player_turn"] == player_id:
                  response = handle_player_action()
            elif data["type"] == "GAME_STATE":
                actual_game_state = data["game_state"]
                if actual_game_state["status"] == "ended":
                    print(actual_game_state)
                    break
                elif actual_game_state["player_turn"] == player_id:
                  response = handle_player_action()