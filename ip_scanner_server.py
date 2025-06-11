import socket
import threading
import ipaddress
import subprocess
import platform

# Importações corrigidas para puresnmp v2.0+
from puresnmp.api.pythonic import PyWrapper
from puresnmp.api.raw import Client
from puresnmp import V2C
from puresnmp.exc import SnmpError, Timeout

HOST = '0.0.0.0'
PORT = 35640
BUFFER_SIZE = 1024
DEFAULT_COMMUNITY_STRING = 'public'
DEFAULT_SNMP_OIDS_TO_TRY = ['1.3.6.1.2.1.1.5.0', '1.3.6.1.2.1.1.1.0'] # sysName, sysDescr
DEFAULT_SNMP_TIMEOUT = 1.0 # Segundos (puresnmp usa float para timeout)
PING_TIMEOUT_SECONDS = 1

def perform_snmp_query(target_ip, community_string, oids_to_try, snmp_timeout):
    """
    Tenta obter informações de um dispositivo via SNMP para uma lista de OIDs usando puresnmp.
    Retorna o primeiro OID e valor encontrados com sucesso.
    """
    try:
        credentials = V2C(community_string)
        raw_client = Client(
            ip=target_ip,
            port=161,
            credentials=credentials,
            timeout=float(snmp_timeout)
        )
        snmp_client = PyWrapper(raw_client)
        results = snmp_client.multiget(oids_to_try)
        
        for i, value in enumerate(results):
            oid_tried = oids_to_try[i]
            if not isinstance(value, SnmpError):
                if isinstance(value, bytes):
                    try:
                        value_str = value.decode('utf-8', errors='replace')
                    except UnicodeDecodeError:
                        value_str = repr(value)
                else:
                    value_str = str(value)
                return f"{target_ip} (SNMP - {oid_tried}): {value_str}"
    except Timeout:
        pass
    except SnmpError:
        pass
    except Exception:
        pass
    return None

def ping_ip(ip_address_str):
    """
    Verifica a disponibilidade de um IP usando o comando ping.
    Retorna True se o IP responder, False caso contrário.
    """
    param = '-n' if platform.system().lower() == 'windows' else '-c'
    timeout_param_val = '200' if platform.system().lower() == 'windows' else '0.2'
    timeout_flag = '-w' if platform.system().lower() == 'windows' else '-W'
    command = ['ping', param, '1', timeout_flag, timeout_param_val, ip_address_str]
    try:
        result = subprocess.run(command,
                                stdout=subprocess.PIPE,
                                stderr=subprocess.PIPE,
                                timeout=PING_TIMEOUT_SECONDS,
                                check=False)
        return result.returncode == 0
    except subprocess.TimeoutExpired:
        return False
    except Exception:
        return False

def handle_client(conn, addr):
    """
    Manipula a conexão de um cliente individual.
    """
    print(f"[NOVA CONEXAO] {addr} conectado.")
    active_devices_info = []
    try:
        data = conn.recv(BUFFER_SIZE)
        if not data:
            print(f" Cliente {addr} desconectou sem enviar dados.")
            return

        parts = data.decode('utf-8').strip().split(';')
        cidr_request = parts[0].strip()
        community_string_client = parts[1] if len(parts) > 1 else DEFAULT_COMMUNITY_STRING

        print(f"[{addr}] Recebido CIDR: {cidr_request}, Comunidade SNMP: {community_string_client}")

        try:
            network = ipaddress.ip_network(cidr_request, strict=False) # [2, 3]
            print(f"[{addr}] Processando {network.num_addresses} IPs na rede {cidr_request}...")

            for ip_obj in network.hosts(): # [2]
                ip_str = str(ip_obj)
                
                snmp_result = perform_snmp_query(
                    ip_str,
                    community_string_client,
                    DEFAULT_SNMP_OIDS_TO_TRY,
                    DEFAULT_SNMP_TIMEOUT
                )

                if snmp_result:
                    print(f"[{addr}] Dispositivo Ativo (SNMP): {snmp_result}")
                    active_devices_info.append(snmp_result)
                else:
                    if ping_ip(ip_str): # [4, 5]
                        print(f"[{addr}] Dispositivo Ativo (Ping): {ip_str}")
                        active_devices_info.append(f"{ip_str} (Ping)")

            if not active_devices_info:
                response_data = "Nenhum dispositivo ativo encontrado na faixa especificada.\n"
            else:
                response_data = "\n".join(active_devices_info) + "\n"
            
            conn.sendall(response_data.encode('utf-8')) # [6, 7, 8]
            print(f"[{addr}] Resposta enviada com {len(active_devices_info)} dispositivos ativos.")

        except ValueError: # [2, 9, 10]
            error_msg = f"Erro: CIDR '{cidr_request}' invalido.\n"
            print(f"[{addr}] {error_msg.strip()}")
            conn.sendall(error_msg.encode('utf-8'))
        except Exception as e:
            error_msg = f"Erro no servidor ao processar sua requisicao: {e}\n"
            print(f"[{addr}] Erro inesperado: {e}")
            conn.sendall(error_msg.encode('utf-8'))

    except socket.error as e:
        print(f" Erro de socket com {addr}: {e}")
    except Exception as e:
        print(f" Erro ao lidar com {addr}: {e}")
    finally:
        print(f" Conexao com {addr} fechada.")
        conn.close() # [6, 7]

def start_server():
    """
    Inicia o servidor TCP multithread.
    """
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM) # [6, 7]
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1) 
    
    try:
        server_socket.bind((HOST, PORT)) # [6, 7]
        server_socket.listen() # [6, 7]
        print(f"[INFO] Servidor esta escutando em {HOST}:{PORT}")

        while True:
            conn, addr = server_socket.accept() # [6, 7]
            client_thread = threading.Thread(target=handle_client, args=(conn, addr)) # [1, 11]
            client_thread.daemon = True 
            client_thread.start()
            print(f"[INFO] Conexoes ativas: {threading.active_count() - 1}") # [1]

    except socket.error as e:
        print(f" Nao foi possivel iniciar o servidor: {e}")
    except KeyboardInterrupt:
        print("\n[INFO] Servidor interrompido pelo usuario.")
    finally:
        print("[INFO] Servidor encerrando.")
        server_socket.close()

if __name__ == "__main__":
    start_server()