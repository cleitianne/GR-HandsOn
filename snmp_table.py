#!/usr/bin/python3
import sys
import subprocess

# OID Base da tabela
BASE_OID = ".1.3.6.1.4.1.99999.2.1"

def get_processes():
    # Coleta dados brutos: pid, comm(nome), %cpu, rss(mem kb), etime(uptime)
    cmd = "/usr/bin/ps -eo pid,comm,pcpu,rss,etime --sort=-pcpu --no-headers | head -n 5"
    output = subprocess.check_output(cmd, shell=True).decode().strip().split('\n')
    
    processes = []
    for line in output:
        parts = line.split(None, 4) # Split em 5 partes
        if len(parts) == 5:
            pid, name, cpu, mem_kb, uptime = parts
            mem_mb = int(int(mem_kb) / 1024)
            processes.append({
                'pid': int(pid),
                'name': name,
                'cpu': cpu,
                'mem': mem_mb,
                'uptime': uptime
            })
    return processes # Lista ordenada por CPU (devido ao comando ps) mas o SNMP requer ordem por OID

def handle_get(oid):
    processes = get_processes()
    req_oid = oid.replace(BASE_OID + ".", "")
    try:
        col, pid = map(int, req_oid.split('.'))
    except:
        return

    proc = next((p for p in processes if p['pid'] == pid), None)
    if not proc: return

    print(oid)
    if col == 1: # PID
        print("integer")
        print(proc['pid'])
    elif col == 2: # Name
        print("string")
        print(proc['name'])
    elif col == 3: # CPU
        print("string")
        print(proc['cpu'])
    elif col == 4: # Mem
        print("integer")
        print(proc['mem'])
    elif col == 5: # Uptime
        print("string")
        print(proc['uptime'])

def handle_getnext(oid):
    processes = get_processes()
    # O SNMP espera que retornemos o PROXIMO OID lexicograficamente
    # Precisamos criar uma lista de todos os OIDs possiveis e achar o proximo
    
    all_oids = []
    # Ordena processos por PID para respeitar ordem SNMP
    processes.sort(key=lambda x: x['pid'])
    
    for col in range(1, 6): # Colunas 1 a 5
        for p in processes:
            # Estrutura: BASE.coluna.pid
            all_oids.append(f"{BASE_OID}.{col}.{p['pid']}")
            
    # Ordenacao de OIDs eh complexa, mas aqui vamos simplificar
    # O correto eh ordenar por (coluna, pid)
    all_oids.sort(key=lambda x: [int(y) for y in x.replace(BASE_OID+".", "").split('.')])

    # Se o OID pedido eh o BASE, retorna o primeiro
    if oid == BASE_OID or oid == ".1.3.6.1.4.1.99999.2":
        next_oid = all_oids[0]
    else:
        try:
            idx = all_oids.index(oid)
            if idx + 1 < len(all_oids):
                next_oid = all_oids[idx + 1]
            else:
                return # Fim da tabela
        except:
            # Se o OID nao existe na lista, ache o proximo maior
            # Simplificacao: retorna o primeiro para evitar travamento
            return 

    # Chama o GET para o proximo OID encontrado
    handle_get(next_oid)

if len(sys.argv) > 1:
    cmd = sys.argv[1]
    req_oid = sys.argv[2]

    if cmd == "-g":
        handle_get(req_oid)
    elif cmd == "-n": # GET NEXT
        handle_getnext(req_oid)
