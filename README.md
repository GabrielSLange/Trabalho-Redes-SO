
# Tutorial de Execução: Scanner de IP em Python

Este tutorial guiará você através dos passos para executar o servidor e o cliente do scanner de IP em seu ambiente local usando o Visual Studio Code (VS Code) ou um terminal padrão.

## Pré-requisitos

- Python 3.8 ou superior instalado.
- Visual Studio Code (opcional, mas recomendado para facilitar a execução e depuração).
- Os arquivos `ip_scanner_server.py` e `test_client.py` no mesmo diretório do projeto.

## Passo 1: Descobrindo o Endereço IP da Sua Máquina e a Faixa da Rede Local

### No Windows

1. **Abra o Prompt de Comando:**
   - Pressione a tecla Windows, digite `cmd` e pressione Enter.
2. **Execute o comando `ipconfig`:**
   ```bash
   ipconfig
   ```
3. **Identifique sua Conexão Ativa** e anote:
   - Endereço IPv4: ex: `192.168.1.105`
   - Máscara de Sub-rede: ex: `255.255.255.0`

### No Linux

1. **Abra o Terminal**
2. **Execute o comando:**
   ```bash
   ip addr
   ```
3. **Anote:**
   - `inet`: ex: `192.168.1.105/24`

### Convertendo para Notação CIDR

- Endereço de Rede: se seu IP é `192.168.1.105` e sua máscara é `255.255.255.0`, o endereço de rede geralmente é `192.168.1.0`.
- Prefixo CIDR:
  - `255.255.255.0` → `/24`
  - `255.255.0.0` → `/16`
- Exemplo: `192.168.1.0/24`

## Passo 2: Executando o Servidor (`ip_scanner_server.py`)

### Usando o VS Code

```bash
python ip_scanner_server.py
```

Você verá algo como: `[INFO] Servidor esta escutando em 0.0.0.0:35640`

### Usando um Terminal Padrão

```bash
cd caminho/para/seu/projeto
python ip_scanner_server.py
```

## Passo 3: Executando o Cliente (`test_client.py`)

### No VS Code

```bash
python test_client.py
```

- Digite a faixa CIDR quando solicitado, ex: `192.168.1.0/24`.

### No Terminal Padrão

```bash
python test_client.py
```

## Testando Múltiplos Clientes

- Mantenha o servidor em execução.
- Em múltiplos terminais, execute:

```bash
python test_client.py
```

## Encerrando a Aplicação

- Para parar o cliente: ele encerra automaticamente.
- Para parar o servidor: `Ctrl + C` no terminal onde ele está rodando.
