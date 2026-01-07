Markdown

# Atividade Prática de Gerenciamento de Redes: Extensão de Agente SNMP

Este projeto documenta a implementação de uma extensão para o agente SNMP nativo do Linux (Net-SNMP) utilizando o protocolo `pass` e scripts em Python. O objetivo foi criar MIBs personalizadas para monitoramento de processos, controle de serviços e envio de notificações (Traps) para um gerente externo.

## 📂 Estrutura do Projeto

```text
.
├── MIBs/                   # Arquivos de definição das MIBs (.txt)
│   ├── CUSTOM-CONTROL-MIB.txt
│   └── CUSTOM-PROCESS-MIB.txt
├── scripts/                # Scripts Python executados pelo Agente
│   ├── snmp_control.py
│   └── snmp_table.py
├── img/                    # Evidências (Prints dos testes)
│   ├── tarefa1_control.png
│   ├── tarefa2_table.png
│   └── tarefa3_trap.png
└── README.md               # Documentação do projeto
⚙️ Ambiente de Testes
Agente: Máquina Virtual Ubuntu Server 24.04 (IP: 10.0.0.X)

Gerente: Windows 10/11 com iReasoning MIB Browser

Conectividade: Rede em modo Bridge

Dependências do Agente:

snmp, snmpd, libsnmp-dev

python3

🚀 Configuração do Agente (snmpd.conf)
Para que o agente execute os scripts e aceite conexões externas, o arquivo /etc/snmp/snmpd.conf foi configurado da seguinte forma:

Plaintext

# 1. Escutar em todas as interfaces
agentAddress udp:161

# 2. Comunidades de acesso
rocommunity public
rwcommunity private

# 3. Integração com scripts Python (Pass Persist)
pass .1.3.6.1.4.1.99999.1 /usr/local/bin/snmp_control.py
pass .1.3.6.1.4.1.99999.2 /usr/local/bin/snmp_table.py

# 4. Configuração de Trap (Destino: Gerente Windows)
trapsink 192.168.0.XXX public
1️⃣ Tarefa 1: Controle de Serviço (Get/Set)
Objetivo: Monitorar se o serviço SNMP está ativo e permitir reiniciá-lo remotamente via comando Set.

Código: scripts/snmp_control.py
Python

#!/usr/bin/python3
import sys
import subprocess
import os

REQ_OID = ".1.3.6.1.4.1.99999.1"

def get_status():
    try:
        # Verifica status do systemd
        output = subprocess.check_output(["systemctl", "is-active", "snmpd"]).decode().strip()
        print(REQ_OID)
        print("integer")
        # Retorna 1 (Up) ou 2 (Down)
        print("1" if output == "active" else "2")
    except:
        print(REQ_OID)
        print("integer")
        print("2")

def set_status(value):
    try:
        val = int(value)
        if val == 3: # Restart
            os.system("(sleep 2; sudo systemctl restart snmpd) &")
        elif val == 2: # Stop
            os.system("(sleep 2; sudo systemctl stop snmpd) &")
    except:
        pass

if len(sys.argv) > 1:
    cmd = sys.argv[1]
    if cmd == "-g":
        get_status()
    elif cmd == "-s" and len(sys.argv) > 4:
        set_status(sys.argv[4])
📸 Evidência
Teste realizado alterando o valor para 3 (restart) e verificando o uptime do serviço.

2️⃣ Tarefa 2: Tabela de Processos (Walk/Table)
Objetivo: Retornar uma tabela SNMP contendo PID, Nome, CPU, Memória e Uptime dos 5 processos que mais consomem CPU no sistema.

Código: scripts/snmp_table.py
Python

#!/usr/bin/python3
import sys
import subprocess

BASE_OID = ".1.3.6.1.4.1.99999.2.1"

def get_processes():
    # Uso de caminho absoluto para o comando ps
    cmd = "/usr/bin/ps -eo pid,comm,pcpu,rss,etime --sort=-pcpu --no-headers | head -n 5"
    output = subprocess.check_output(cmd, shell=True).decode().strip().split('\n')
    
    processes = []
    for line in output:
        parts = line.split(None, 4)
        if len(parts) == 5:
            pid, name, cpu, mem_kb, uptime = parts
            processes.append({
                'pid': int(pid), 'name': name, 'cpu': cpu, 
                'mem': int(int(mem_kb) / 1024), 'uptime': uptime
            })
    return processes

def handle_get(oid):
    processes = get_processes()
    req_oid = oid.replace(BASE_OID + ".", "")
    try:
        col, pid = map(int, req_oid.split('.'))
    except: return

    proc = next((p for p in processes if p['pid'] == pid), None)
    if not proc: return

    print(oid)
    if col == 1: print("integer\n" + str(proc['pid']))
    elif col == 2: print("string\n" + proc['name'])
    elif col == 3: print("string\n" + proc['cpu'])
    elif col == 4: print("integer\n" + str(proc['mem']))
    elif col == 5: print("string\n" + proc['uptime'])

def handle_getnext(oid):
    processes = get_processes()
    processes.sort(key=lambda x: x['pid'])
    
    # Lógica simplificada de GetNext (Iteração sobre colunas e PIDs)
    # ... (Ver arquivo completo na pasta scripts)
📸 Evidência
Visualização da tabela no iReasoning MIB Browser (GetBulk desativado).

3️⃣ Tarefa 3: Notificações (Traps)
Objetivo: Configurar o agente para enviar alertas espontâneos (Traps) para o gerente na porta 162.

Configuração e Execução
Adicionado trapsink [IP_GERENTE] public no snmpd.conf.

Disparo manual do trap via terminal do Ubuntu:

Bash

sudo snmptrap -v 2c -c public 192.168.0.XXX "" .1.3.6.1.4.1.99999.3 \
.1.3.6.1.4.1.99999.3.1 s "Alerta: Falha Critica no Sistema"
📸 Evidência
Trap recebido no Trap Receiver do iReasoning.

🛠️ Como Reproduzir
Clone este repositório.

Copie os arquivos da pasta scripts para /usr/local/bin/ na VM Ubuntu.

Dê permissão de execução: chmod +x /usr/local/bin/*.py.

Substitua o arquivo /etc/snmp/snmpd.conf pelas configurações listadas acima.

Reinicie o serviço: sudo service snmpd restart.

Importe as MIBs da pasta MIBs no seu navegador SNMP favorito.

Disciplina: Gerenciamento de Redes