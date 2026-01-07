#!/usr/bin/python3
import sys

# OID BASE da tabela
BASE_OID = ".1.3.6.1.4.1.99999.2.1"

raw_data = {
    ".1.10": ["integer", "1001"],       # PID
    ".2.10": ["string", "python_test"], # Nome
    ".3.10": ["integer", "15"],         # CPU
    ".4.10": ["integer", "51200"],      # Mem
    ".5.10": ["timeticks", "111111"],   # Uptime

    ".1.20": ["integer", "1002"],
    ".2.20": ["string", "systemd_sim"],
    ".3.20": ["integer", "2"],
    ".4.20": ["integer", "102400"],
    ".5.20": ["timeticks", "222222"]
}

# Logica de Ordenacao para GetNext
sorted_entries = []
for suffix, val in raw_data.items():
    full_oid = BASE_OID + suffix
    oid_tuple = tuple(int(x) for x in full_oid.strip('.').split('.'))
    sorted_entries.append((oid_tuple, full_oid, val[0], val[1]))

sorted_entries.sort(key=lambda x: x[0])

def handle_get(req_oid):
    for oid_tuple, oid_str, type_, val in sorted_entries:
        if oid_str == req_oid:
            print(oid_str); print(type_); print(val)
            sys.exit(0)
    sys.exit(0)

def handle_next(req_oid):
    try:
        req_tuple = tuple(int(x) for x in req_oid.strip('.').split('.'))
    except ValueError: 
        print(sorted_entries[0][1]); print(sorted_entries[0][2]); print(sorted_entries[0][3])
        sys.exit(0)

    for oid_tuple, oid_str, type_, val in sorted_entries:
        if oid_tuple > req_tuple:
            print(oid_str); print(type_); print(val)
            sys.exit(0)
    sys.exit(0)

if __name__ == "__main__":
    if len(sys.argv) < 3: sys.exit(0)
    action, oid = sys.argv[1], sys.argv[2]
    if action == "-g": handle_get(oid)
    elif action == "-n": handle_next(oid)
