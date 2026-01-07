#!/usr/bin/python3
import sys
import subprocess
import os
import time

# OID que este script responde (passado pelo snmpd)
REQ_OID = ".1.3.6.1.4.1.99999.1"

def get_status():
    try:
        # Verifica status via systemctl
        output = subprocess.check_output(["systemctl", "is-active", "snmpd"]).decode().strip()
        if output == "active":
            print(REQ_OID)
            print("integer")
            print("1") # running
        else:
            print(REQ_OID)
            print("integer")
            print("2") # stopped
    except:
        print(REQ_OID)
        print("integer")
        print("2")

def set_status(value):
    # O snmpd passa o valor a ser setado
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
    
    if cmd == "-g": # GET
        get_status()
        
    elif cmd == "-s": # SET

        if len(sys.argv) > 4:
            set_status(sys.argv[4])
