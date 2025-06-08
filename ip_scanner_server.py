import socket
import threading
import ipaddress
import subprocess
import platform

HOST = '0.0.0.0'
PORT = 35640
BUFFER_SIZE = 1024
PING_TIMEOUT_SECONDS = 1 # Timeout para o subprocesso de ping

def ping_ip(ip_address_str):
    """
    Verifica a disponibilidade de um IP usando o comando ping.
    Retorna True se o IP responder, False caso contrário.
    """
    param = '-n' if platform.system().lower() == 'windows' else '-c'
    timeout_param_val = '200' if platform.system().lower() == 'windows' else '0.2' # Windows em ms, Linux/Mac em s
    timeout_flag = '-w' if platform.system().lower() == 'windows' else '-W'

    command = ['ping', param, '1', timeout_flag, timeout_param_val, ip_address_str]

    try:
        # O timeout em subprocess.run é uma garantia adicional
        result = subprocess.run(command,
                                stdout=subprocess.PIPE,
                                stderr=subprocess.PIPE,
                                timeout=PING_TIMEOUT_SECONDS, # Timeout para o processo de ping
                                check=False) # Nao lanca excecao para returncode!= 0
        return result.returncode == 0
    except subprocess.TimeoutExpired:
        print(f"Timeout ao tentar pingar {ip_address_str}")
        return False
    except Exception as e:
        print(f"Erro ao pingar {ip_address_str}: {e}")
        return False

def handle_client(conn, addr):
    """
    Manipula a conexão de um cliente individual.
    """
    print(f"[NOVA CONEXAO] {addr} conectado.")
    active_ips = []
    try:
        data = conn.recv(BUFFER_SIZE)
        if not data:
            print(f" Cliente {addr} desconectou sem enviar dados.")
            return

        cidr_request = data.decode('utf-8').strip()
        print(f"[{addr}] Recebido CIDR: {cidr_request}")

        try:
            network = ipaddress.ip_network(cidr_request, strict=False) # [1, 2]
            print(f"[{addr}] Processando {network.num_addresses} IPs na rede {cidr_request}...")

            # Para redes muito grandes, pode ser necessário otimizar ou limitar
            # Aqui, iteramos sobre os hosts utilizáveis
            for ip_obj in network.hosts(): # [1]
                ip_str = str(ip_obj)
                if ping_ip(ip_str):
                    print(f"[{addr}] IP Ativo: {ip_str}")
                    active_ips.append(ip_str)
                # else:
                #    print(f"[{addr}] IP Inativo: {ip_str}")


            if not active_ips:
                response_data = "Nenhum IP ativo encontrado na faixa especificada.\n"
            else:
                response_data = "\n".join(active_ips) + "\n"
            
            conn.sendall(response_data.encode('utf-8')) # [3, 4]
            print(f"[{addr}] Resposta enviada com {len(active_ips)} IPs ativos.")

        except ValueError: # [1, 5, 6]
            error_msg = f"Erro: CIDR '{cidr_request}' invalido.\n"
            print(f"[{addr}] {error_msg.strip()}")
            conn.sendall(error_msg.encode('utf-8'))
        except Exception as e:
            error_msg = f"Erro no servidor ao processar sua requisicao: {e}\n"
            print(f"[{addr}] Erro inesperado: {e}")
            conn.sendall(error_msg.encode('utf-8'))

    except socket.error as e:
        print(f" {addr}: {e}")
    except Exception as e:
        print(f" {addr}: {e}")
    finally:
        print(f" {addr}")
        conn.close() # [7, 8]

def start_server():
    """
    Inicia o servidor TCP multithread.
    """
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM) # [3, 7, 8]
    # Permite reutilizar o endereço imediatamente após o servidor ser fechado
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1) 
    
    try:
        server_socket.bind((HOST, PORT)) # [3, 7]
        server_socket.listen() # [3, 7]
        print(f"[INFO] Servidor esta escutando em {HOST}:{PORT}")

        while True:
            conn, addr = server_socket.accept() # [3, 7]
            client_thread = threading.Thread(target=handle_client, args=(conn, addr)) # [3, 9]
            client_thread.daemon = True # Permite que o programa principal saia mesmo se as threads estiverem rodando
            client_thread.start()
            print(f" {threading.active_count() - 1}") # -1 para a thread principal [3]

    except socket.error as e:
        print(f" Nao foi possivel iniciar o servidor: {e}")
    except KeyboardInterrupt:
        print("\n[INFO] Servidor interrompido pelo usuario.")
    finally:
        print("[INFO] Servidor encerrando.")
        server_socket.close()

if __name__ == "__main__":
    start_server()