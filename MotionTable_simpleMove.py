import argparse
import pandas as pd
import time
import sys
import pdb
#from pyModbusTCP.client import ModbusClient
from easymodbus.modbusClient import *
#from PIL import ImageTk, Image 
import json
from datetime import datetime, timedelta
from integrateITA import getITAdata
import requests

def notify(msg):
    payload = {
        "token": "a2et4br1v9ckjhwy5mqnfdooonhkbf",
        "user": "urmrsjqcatf817r93gfqo2g29fhiiv",
        "message": msg,
        "title": "Python Alert"
    }
    requests.post("https://api.pushover.net/1/messages.json", data=payload)

def log(msg, filename="file_stepper.log"):
    timestamp = datetime.now().strftime("[%H:%M:%S]")
    with open(filename, "a") as logfile:
        logfile.write(f"{timestamp}: {msg}\n")

def progress_bar(duration_seconds):
    start = time.time()
    end = start + duration_seconds
    bar_length = 80  # length of the bar in characters

    while True:
        now = time.time()
        elapsed = now - start
        remaining = end - now

        if remaining < 0:
            remaining = 0

        # Compute percentage
        pct = min(elapsed / duration_seconds, 1.0)
        filled = int(bar_length * pct)
        bar = "#" * filled + "-" * (bar_length - filled)

        # Print bar
        sys.stdout.write(
            f"\r[{bar}] {pct*100:6.2f}% | {remaining:6.1f}s remaining"
        )
        sys.stdout.flush()

        if pct >= 1.0:
            break

        time.sleep(0.1)  # update rate
    print("\nDone!")
        
def ReadH():
    H_Pos = 999999
    try:
        modbusClient = ModbusClient("131.225.125.17", int("8000"))
        if (not modbusClient.is_connected()):
            modbusClient.connect()
        holdingRegisters = modbusClient.read_holdingregisters(4, 1)

        for register in holdingRegisters:
            H_Pos=(str((register)/100))

        modbusClient.close()
        
    except Exception as e:
        notify("STOP BEAM!!! Table is stuck! Call the MCR at 1-630-840-3721!")
        print('Exception Reading input Registers from Server', str(e))

    return round(float(H_Pos),1)

def ReadV():
    V_Pos = 999999
    try:
        modbusClient = ModbusClient("131.225.125.17", int("8000"))
        if (not modbusClient.is_connected()):
            modbusClient.connect()
        holdingRegisters = modbusClient.read_holdingregisters(6, 1)

        for register in holdingRegisters:
            V_Pos=(str((register)/10))

        modbusClient.close()
        
    except Exception as e:
        notify("STOP BEAM!!! Table is stuck! Call the MCR at 1-630-840-3721!")
        print('Exception Reading input Registers from Server', str(e))

    return round(float(V_Pos),1)
            
def HHome():

    try:
        modbusClient = ModbusClient("131.225.125.17", int("8000"))
        if (not modbusClient.is_connected()):
            modbusClient.connect()
        modbusClient.write_single_register(129, 2)

    except Exception as e:
        print('Exception Reading coils from Server', str(e))
    finally:
        modbusClient.close()
    print("Hor Home")

def HGOTO(h_pos):

    try:
        modbusClient = ModbusClient("131.225.125.17", int("8000"))
        if (not modbusClient.is_connected()):
            modbusClient.connect()
        modbusClient.write_single_register(0, int(h_pos*100))
        time.sleep(.5)
    
        modbusClient.write_single_register(129, 3)

    except Exception as e:
        notify("STOP BEAM!!! Table is stuck! Call the MCR at 1-630-840-3721!")
        print('Exception Reading coils from Server', str(e))
    finally:
        modbusClient.close()

    print("HGOTO:", h_pos)

def STOP():

    try:
        modbusClient = ModbusClient("131.225.125.17", int("8000"))
        if (not modbusClient.is_connected()):
            modbusClient.connect()
        modbusClient.write_single_coil(3, 1)

    except Exception as e:
        print('Exception Reading coils from Server', str(e))
    finally:
        modbusClient.close()
    print("STOP")
    
def VHome():

    try:
        modbusClient = ModbusClient("131.225.125.17", int("8000"))
        if (not modbusClient.is_connected()):
            modbusClient.connect()
        modbusClient.write_single_register(129, 4)

    except Exception as e:
        print('Exception Reading coils from Server', str(e))
    finally:
        modbusClient.close()
    print("Ver Home")

def VGOTO(v_pos):

    try:
        modbusClient = ModbusClient("131.225.125.17", int("8000"))
        if (not modbusClient.is_connected()):
            modbusClient.connect()
        modbusClient.write_single_register(2, int(v_pos*10))
        time.sleep(.5)
    
        modbusClient.write_single_register(129, 5)

    except Exception as e:
        notify("STOP BEAM!!! Table is stuck! Call the MCR at 1-630-840-3721!")
        print('Exception Reading coils from Server', str(e))
    finally:
        modbusClient.close()
    print("VGOTO:", v_pos)
    
def main():

    parser = argparse.ArgumentParser(description="Reads in a JSON file with a list of positions and doses and moves the table accordingly.")
    parser.add_argument('-v', dest='debug', action="store_true", default=False, help="Turn on verbose debugging. (default: False)")
    parser.add_argument('-b', dest='simulatebeam', action="store_true", default=False, help="Simulate a spill every spill delay. The size of the spill is spillsize (default: False)")
    parser.add_argument('-f', dest='filename', default="file_stepper.json", help="Input JSON file name. (default: file_stepper.json)")
    parser.add_argument('-p', dest='progress_bar', action="store_true", default=False, help="Enable progress bar for vertical table motion (default: False)")
    parser.add_argument('-s', dest='spillsize', type=float, default=1.85E13, help="Number of protons in the event (default: 1.85E13)")
    parser.add_argument('-t', dest='datetimeformat', default="%%d-%%b-%%Y-%%H:%%M:%%S", help="Date/time format for integrateITA (default: %%d-%%b-%%Y-%%H:%%M:%%S)")
    parser.add_argument('--dryrun', dest='dryrun', action="store_true", default=False, help="Just move the table, and don't wait for beam (default: False)")
    parser.add_argument('--delay', dest='delay', type=float, default=3.0, help="Delay to start table motion. (default: 3s)")
    parser.add_argument('--hdelay', dest='hdelay', type=float, default=10.0, help="Delay for horizontal motion. (default: 10s)")
    parser.add_argument('--sdelay', dest='sdelay', type=float, default=10.0, help="Delay for checking the dose of the spill. (default: 10s)")
    parser.add_argument('--vdelay', dest='vdelay', type=float, default=30.0, help="Delay for vertical motion. (default: 30s)")
    parser.add_argument('--tolerance', dest='tolerance', type=float, default=0.5, help="Tolerance for the motion table. (default: 0.5mm)")
    args = parser.parse_args()

    with open(args.filename, "r") as stepfile:
        steps = json.load(stepfile)

    for step in steps:
        if "comment" in step:
            print("COMMENT:", step["comment"])
            log(step["comment"])
            continue
        
        position = 999999
        print(step["stepname"], step["pos"], step["dose"])
        log(" ".join([str(step["stepname"]), str(step["pos"]), "Target:", str(step["dose"])]))

        if "HSTEP" in step["stepname"]:
            hReadBack = ReadH()
            HGOTO(step["pos"])
            time.sleep(args.delay)
            if hReadBack == ReadH():
                HGOTO(step["pos"])
                time.sleep(args.delay)
            print(hReadBack, step["pos"], abs(hReadBack - step["pos"]))
            while abs(hReadBack - step["pos"]) > args.tolerance:
                hReadBack = ReadH()
                time.sleep(args.hdelay)
                if hReadBack == ReadH(): HGOTO(step["pos"])
                hReadBack = ReadH()
                print(hReadBack, step["pos"], round(abs(hReadBack - step["pos"]),1))
            position = ReadH()

        if "VSTEP" in step["stepname"]:
            vReadBack = ReadV()
            VGOTO(step["pos"])
            time.sleep(args.delay)
            if vReadBack == ReadV():
                VGOTO(step["pos"])
                time.sleep(args.delay)
            print(vReadBack, step["pos"], abs(vReadBack - step["pos"]))
            while abs(vReadBack - step["pos"]) > args.tolerance:
                vReadBack = ReadV()
                if args.progress_bar: progress_bar(args.vdelay)
                else: time.sleep(args.vdelay)
                if vReadBack > step["pos"]+args.tolerance:
                    VGOTO(step["pos"]-10)
                    if args.progress_bar: progress_bar(args.vdelay)
                    else: time.sleep(args.vdelay)
                    VGOTO(step["pos"])
                    if args.progress_bar: progress_bar(args.vdelay)
                    else: time.sleep(args.vdelay)
                elif vReadBack == ReadV(): VGOTO(step["pos"])
                vReadBack = ReadV()
                print(vReadBack, step["pos"], round(abs(vReadBack - step["pos"]),1))
            position = ReadV()

        if int(step["dose"]) == 0 or args.dryrun: continue
        dose = 0
        start = pd.Timestamp.now()
        print("Target Dose:", step["dose"])
        while dose <= int(step["dose"]):
            time.sleep(args.sdelay)
            now = pd.Timestamp.now()
            if args.simulatebeam: dose += args.spillsize
            else:
                dose, df = getITAdata(start.strftime(args.datetimeformat_str), now.strftime(args.datetimeformat_str), 'E:UTR112', 'MTA')
            print("Delivered Dose:", dose)
            DeltaT = (start - now).total_seconds()
            if (float(DeltaT)/60 > float(step["dose"])/args.spillsize+1):
                notify("Check if the Beam has Stopped!")
        log(" ".join([str(step["stepname"]), str(position), "Delivered", str(dose)]))

if __name__ == "__main__": main()
print("Done!")
