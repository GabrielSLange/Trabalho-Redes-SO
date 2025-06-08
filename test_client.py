import socket

SERVER_HOST = '127.0.0.1' # Ou o IP do servidor se estiver em outra maquina
SERVER_PORT = 35640
BUFFER_SIZE = 4096 # Buffer maior para receber listas potencialmente longas de IPs

def run_client():
    """
    Executa o cliente TCP para testar o servico de varredura de IP.
    """
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client_socket:
            print(f"Tentando conectar a {SERVER_HOST}:{SERVER_PORT}...")
            client_socket.connect((SERVER_HOST, SERVER_PORT))
            print("Conectado ao servidor.")

            cidr_request = input("Digite a faixa CIDR (ex: 192.168.1.0/24): ").strip()
            if not cidr_request:
                print("Nenhuma CIDR fornecida. Saindo.")
                return

            client_socket.sendall(cidr_request.encode('utf-8'))
            print(f"CIDR '{cidr_request}' enviada. Aguardando resposta...")

            # Loop para receber toda a resposta, pois pode ser maior que o buffer
            full_response_bytes = b''
            while True:
                chunk = client_socket.recv(BUFFER_SIZE)
                if not chunk: # Servidor fechou a conexao apos enviar todos os dados
                    break
                full_response_bytes += chunk
            
            response_str = full_response_bytes.decode('utf-8')
            
            if response_str.startswith("Erro:"):
                print(f"\nResposta do Servidor (Erro):\n{response_str.strip()}")
            elif "Nenhum IP ativo encontrado" in response_str:
                print(f"\nResposta do Servidor:\n{response_str.strip()}")
            else:
                print("\nIPs Ativos Recebidos:")
                print(response_str.strip())

    except ConnectionRefusedError:
        print(f"Erro: Nao foi possivel conectar ao servidor em {SERVER_HOST}:{SERVER_PORT}. Verifique se o servidor esta em execucao.")
    except socket.timeout:
        print("Erro: Timeout na conexao com o servidor.")
    except Exception as e:
        print(f"Ocorreu um erro inesperado no cliente: {e}")

if __name__ == "__main__":
    run_client()