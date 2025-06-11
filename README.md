
Abra o terminal (PowerShell ou CMD) no diretório do seu projeto e execute:

```powershell
python -m venv windows



# 📡 Tutorial: Executando `ip_scanner_server.py` com ambiente virtual no Windows 10

Este guia ensina como ativar um ambiente virtual chamado `windows` e executar o script `ip_scanner_server.py`.

---

## ✅ Pré-requisitos

- Python 3.x instalado no sistema
- Windows 10
- Terminal (PowerShell ou CMD)
- Arquivo `ip_scanner_server.py` salvo no diretório do projeto
- Ambiente virtual chamado `windows` (se ainda não tiver, veja abaixo como criar)

---

## 📁 Passo 1 – Criar o ambiente virtual (se ainda não existir)

Abra o PowerShell ou CMD no diretório do seu projeto e execute:

```powershell
python -m venv windows
```

Isso criará uma pasta chamada `windows/` com o ambiente virtual.

---

## ⚙️ Passo 2 – Ativar o ambiente virtual

### ▶ PowerShell:

```powershell
.\windows\Scripts\activate
```

#### 🛑 Se aparecer erro de permissão:

```powershell
Set-ExecutionPolicy -Scope CurrentUser -ExecutionPolicy RemoteSigned
```

Depois, execute novamente:

```powershell
.\windows\Scripts\activate
```

---

### ▶ CMD (Prompt de Comando):

```cmd
windows\Scripts\activate
```

---

## 🚀 Passo 3 – Executar o servidor

Com o ambiente virtual ativo, execute:

```powershell
python ip_scanner_server.py
```

Se tudo estiver correto, você verá algo como:

```
[INFO] Servidor esta escutando em 0.0.0.0:35640
```

---

## ❌ Passo 4 – Encerrar o ambiente virtual

Para sair do ambiente virtual:

```powershell
deactivate
```

---

```powershell
python --version
```

---
