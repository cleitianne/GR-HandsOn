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
            # Agenda o restart para daqui a 2 segundos para dar tempo de responder ao Mib Browser
            os.system("(sleep 2; sudo systemctl restart snmpd) &")
        elif val == 2: # Stop
            # CUIDADO: Se parar, o SNMP morre e voce nao consegue iniciar remotamente de novo
            os.system("(sleep 2; sudo systemctl stop snmpd) &")
    except:
        pass

# Logica de leitura de argumentos do protocolo PASS do Net-SNMP
if len(sys.argv) > 1:
    cmd = sys.argv[1]
    
    if cmd == "-g": # GET
        get_status()
        
    elif cmd == "-s": # SET
        # Argumentos: -s OID TYPE VALUE
        # Exemplo: -s .1.3.6.1.4.1.99999.1 integer 3
        if len(sys.argv) > 4:
            set_status(sys.argv[4])
