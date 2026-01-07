#!/usr/bin/python3
import sys
import subprocess

# OID Base da tabela
BASE_OID = ".1.3.6.1.4.1.99999.2.1"

def get_processes():
    # Coleta dados: pid, comm(nome), %cpu, rss(mem kb), etime(uptime)
    cmd = "/usr/bin/ps -eo pid,comm,pcpu,rss,etime --sort=-pcpu --no-headers | head -n 5"
    output = subprocess.check_output(cmd, shell=True).decode().strip().split('\n')
    
    processes = []
    for line in output:
        parts = line.split(None, 4) 
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
    return processes 

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
   
    all_oids = []
    processes.sort(key=lambda x: x['pid'])
    
    for col in range(1, 6): 
        for p in processes:
            
            all_oids.append(f"{BASE_OID}.{col}.{p['pid']}")
            
   
    all_oids.sort(key=lambda x: [int(y) for y in x.replace(BASE_OID+".", "").split('.')])

    if oid == BASE_OID or oid == ".1.3.6.1.4.1.99999.2":
        next_oid = all_oids[0]
    else:
        try:
            idx = all_oids.index(oid)
            if idx + 1 < len(all_oids):
                next_oid = all_oids[idx + 1]
            else:
                return 
        except:
            return 

    handle_get(next_oid)

if len(sys.argv) > 1:
    cmd = sys.argv[1]
    req_oid = sys.argv[2]

    if cmd == "-g":
        handle_get(req_oid)
    elif cmd == "-n": 
        handle_getnext(req_oid)
