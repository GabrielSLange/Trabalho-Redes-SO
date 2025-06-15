import socket
import sys

SERVER_HOST = '127.0.0.1' 
SERVER_PORT = 35640
BUFFER_SIZE = 4096

def run_client():
    """
    Executa o cliente TCP para testar o servico de varredura de IP.
    """
    if len(sys.argv) < 2:
        print("Uso: python test_client.py <CIDR_REQUEST>")
        print("Exemplo 1: python test_client.py 192.168.1.0/24")
        print("Exemplo 2: python test_client.py 192.168.1.0/24 segredo")
        return

    cidr_request = sys.argv[1]
    community_string = sys.argv[2] if len(sys.argv) > 2 else ""

    request_message = cidr_request
    if community_string:
        request_message += f";{community_string}"

    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client_socket:
            print(f"Tentando conectar a {SERVER_HOST}:{SERVER_PORT}...")
            client_socket.connect((SERVER_HOST, SERVER_PORT))
            print("Conectado ao servidor.")

            client_socket.sendall(request_message.encode('utf-8'))
            print(f"Mensagem '{request_message}' enviada. Aguardando resposta...")

            # Loop para receber toda a resposta, pois pode ser grande
            full_response_bytes = b''
            while True:
                chunk = client_socket.recv(BUFFER_SIZE)
                if not chunk: # Servidor fechou a conexão após enviar todos os dados
                    break
                full_response_bytes += chunk
            
            response_str = full_response_bytes.decode('utf-8')
            
            if response_str.startswith("Erro:"):
                print(f"\nResposta do Servidor (Erro):\n{response_str.strip()}")
            elif not response_str.strip():
                 print("\nNenhuma resposta recebida do servidor (pode ter sido fechada).")
            else:
                print("\nResultados da Varredura:")
                print(response_str.strip())

    except ConnectionRefusedError:
        print(f"Erro: Nao foi possivel conectar ao servidor em {SERVER_HOST}:{SERVER_PORT}. Verifique se o servidor esta em execucao.")
    except socket.timeout:
        print("Erro: Timeout na conexao com o servidor.")
    except Exception as e:
        print(f"Ocorreu um erro inesperado no cliente: {e}")

if __name__ == "__main__":
    run_client()