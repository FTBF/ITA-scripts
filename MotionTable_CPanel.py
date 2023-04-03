from tkinter import Label, Tk
import tkinter as tk
import time
import sys
#from pyModbusTCP.client import ModbusClient
from easymodbus.modbusClient import *
import tkinter.messagebox as messagebox
#from PIL import ImageTk, Image 

app_window = Tk() 
app_window.title("Control Panel") 
app_window.geometry("600x350") 
app_window.resizable(0,0)
app_window.configure(background="#00ffff")
text_font= ("Arial", 30, 'bold')
background = "#00ffff"
foreground= "#000000"
border_width = 25
##LLimit = True
##RLimit = True
##Up = False
##Dwn = False

def HHome():

    try:
        modbusClient = ModbusClient("131.225.125.17", int("8000"))
        if (not modbusClient.is_connected()):
            modbusClient.connect()
        modbusClient.write_single_register(129, 2)

    except Exception as e:
        messagebox.showerror('Exception Reading coils from Server', str(e))
    finally:
        modbusClient.close()
    print ("Hor Home")

def HGOTO():

    try:
        modbusClient = ModbusClient("131.225.125.17", int("8000"))
        if (not modbusClient.is_connected()):
            modbusClient.connect()
        print (float(H_GOTO_1.get()))   
        modbusClient.write_single_register(0, (int(float(H_GOTO_1.get())))*100)
        time.sleep(.5)
    
        modbusClient.write_single_register(129, 3)

    except Exception as e:
        messagebox.showerror('Exception Reading coils from Server', str(e))
    finally:
        modbusClient.close()

    print ("Hor GOTO")

def STOP():

    try:
        modbusClient = ModbusClient("131.225.125.17", int("8000"))
        if (not modbusClient.is_connected()):
            modbusClient.connect()
        modbusClient.write_single_coil(3, 1)

    except Exception as e:
        messagebox.showerror('Exception Reading coils from Server', str(e))
    finally:
        modbusClient.close()
    print ("STOP")
    
def VHome():

    try:
        modbusClient = ModbusClient("131.225.125.17", int("8000"))
        if (not modbusClient.is_connected()):
            modbusClient.connect()
        modbusClient.write_single_register(129, 4)

    except Exception as e:
        messagebox.showerror('Exception Reading coils from Server', str(e))
    finally:
        modbusClient.close()
    print ("Ver Home")

def VGOTO():

    try:
        modbusClient = ModbusClient("131.225.125.17", int("8000"))
        if (not modbusClient.is_connected()):
            modbusClient.connect()
        print (float(V_GOTO_1.get()))   
        modbusClient.write_single_register(2, (int(float(V_GOTO_1.get())))*10)
        time.sleep(.5)
    
        modbusClient.write_single_register(129, 5)

    except Exception as e:
        messagebox.showerror('Exception Reading coils from Server', str(e))
    finally:
        modbusClient.close()
    print ("Ver GOTO")
    
    
      

def digital_clock(): 
    time_live = time.strftime("%H:%M:%S")
    label.config(text=time_live)
    #Read_Modbus()

    label.after(1000, digital_clock)

    
    
def Read_Modbus():    
    try:
        modbusClient = ModbusClient("131.225.125.17", int("8000"))
        if (not modbusClient.is_connected()):
            modbusClient.connect()
        holdingRegisters = modbusClient.read_holdingregisters(6, 1)

        for register in holdingRegisters:
            V_Pos=(str((register)/10))     

        holdingRegisters = modbusClient.read_holdingregisters(2, 1)

        for register in holdingRegisters:
            VGOTO_1=(str((register)/10))     

        holdingRegisters = modbusClient.read_holdingregisters(4, 1)

        for register in holdingRegisters:
            H_Pos=(str((register)/100))     

        holdingRegisters = modbusClient.read_holdingregisters(0, 1)

        for register in holdingRegisters:
            HGOTO_1=(str((register)/100))     

        LLimit = modbusClient.read_coils(0, 1)
        RLimit = modbusClient.read_coils(1, 1)
        MotorUp = modbusClient.read_coils(3, 1)
        MotorDwn = modbusClient.read_coils(4, 1)

        Text12.config(text=" ")
        Text11.config(text=" ")
        
        if  LLimit[0] == 1:
            Text11.config(text="<")
        if  RLimit[0] == 1:
            Text11.config(text=">")   
        if not MotorUp[0] == 1:
            Text12.config(text="UP ^")
        if not MotorDwn[0] == 1:
            Text12.config(text="Dwn")
            
            
   
        modbusClient.close()
        
    except Exception as e:
            messagebox.showerror('Exception Reading input Registers from Server', str(e))
    sys.stdout.flush()

    Text1.config(text=H_Pos)
    Text2.config(text=V_Pos)

    Text1.after(2000, Read_Modbus)

    
label = Label(app_window, font=text_font, bg=background, fg=foreground, bd=border_width) 
label.place(relx=0.3, rely=0.026, height=31, width=254)

Label1 = Label(app_window, font=text_font, bg=background, fg=foreground, bd=border_width) 
Label1.place(relx=0.05, rely=0.15, height=31, width=254)
Label1.configure(activebackground="#f9f9f9")
Label1.configure(activeforeground="black")
Label1.configure(background="#00ffff")
Label1.configure(disabledforeground="#a3a3a3")
Label1.configure(font="-family {Arial Black} -size 18")
Label1.configure(foreground="#000000")
Label1.configure(highlightbackground="#d9d9d9")
Label1.configure(highlightcolor="black")
Label1.configure(text='''Horizontal Position''')

Label2 = Label(app_window, font=text_font, bg=background, fg=foreground, bd=border_width) 
Label2.place(relx=0.55, rely=0.15, height=31, width=254)
Label2.configure(activebackground="#f9f9f9")
Label2.configure(activeforeground="black")
Label2.configure(background="#00ffff")
Label2.configure(disabledforeground="#a3a3a3")
Label2.configure(font="-family {Arial Black} -size 18")
Label2.configure(foreground="#000000")
Label2.configure(highlightbackground="#d9d9d9")
Label2.configure(highlightcolor="black")
Label2.configure(text='''Vertical Position''')

Text1 = Label(app_window, font=text_font, bg=background, fg=foreground, bd=border_width)
Text1.place(relx=0.07, rely=0.25, height=31, width=200)
Text1.configure(background="#00ffff")
Text1.configure(font="-family {Arial Black} -size 14")
Text1.configure(foreground="black")
Text1.configure(highlightbackground="#d9d9d9")
Text1.configure(highlightcolor="black")
##Text1.configure(text=H_Pos)

Text11 = Label(app_window, font=text_font, bg=background, fg=foreground, bd=border_width)
Text11.place(relx=0.10, rely=0.25, height=31, width=30)
Text11.configure(background="#00ffff")
Text11.configure(font="-family {Arial Black} -size 14")
Text11.configure(foreground="red")
Text11.configure(highlightbackground="#d9d9d9")
Text11.configure(highlightcolor="black")

Text2 = Label(app_window, font=text_font, bg=background, fg=foreground, bd=border_width)
Text2.place(relx=0.57, rely=0.25, height=31, width=200)
Text2.configure(background="#00ffff")
Text2.configure(font="-family {Arial Black} -size 14")
Text2.configure(foreground="black")
Text2.configure(highlightbackground="#d9d9d9")
Text2.configure(highlightcolor="black")

Text12 = Label(app_window, font=text_font, bg=background, fg=foreground, bd=border_width)
Text12.place(relx=0.59, rely=0.25, height=31, width=50)
Text12.configure(background="#00ffff")
Text12.configure(font="-family {Arial Black} -size 14")
Text12.configure(foreground="red")
Text12.configure(highlightbackground="#d9d9d9")
Text12.configure(highlightcolor="black")

H_GOTO_1 = tk.Entry(fg="black", bg="blue", width=150)
H_GOTO_1.place(relx=0.1, rely=0.371, height=31, width=150)
H_GOTO_1.configure(background="white")
H_GOTO_1.configure(disabledforeground="#a3a3a3")
H_GOTO_1.configure(font="Arial")
H_GOTO_1.configure(foreground="#000000")
H_GOTO_1.configure(highlightbackground="#d9d9d9")
H_GOTO_1.configure(highlightcolor="black")
H_GOTO_1.configure(insertbackground="black")
H_GOTO_1.configure(selectbackground="blue")
H_GOTO_1.configure(selectforeground="white")
#H_GOTO_1.configure(textvariable=HGOTO)

V_GOTO_1 = tk.Entry(fg="black", bg="blue", width=150)
V_GOTO_1.place(relx=0.60, rely=0.371, height=31, width=150)
V_GOTO_1.configure(background="white")
V_GOTO_1.configure(disabledforeground="#a3a3a3")
V_GOTO_1.configure(font="Arial")
V_GOTO_1.configure(foreground="#000000")
V_GOTO_1.configure(highlightbackground="#d9d9d9")
V_GOTO_1.configure(highlightcolor="black")
V_GOTO_1.configure(insertbackground="black")
V_GOTO_1.configure(selectbackground="blue")
V_GOTO_1.configure(selectforeground="white")
#H_GOTO_1.configure(textvariable=HGOTO)

HHome_Button = tk.Button(app_window, text="Home",command = HHome)
HHome_Button.place(relx=0.033, rely=0.486, height=34, width=77)
HHome_Button.configure(font="-family {Arial Black} -size 12")

HGOTO_Button = tk.Button(app_window, text="GOTO",command = HGOTO)
HGOTO_Button.place(relx=0.283, rely=0.486, height=34, width=77)
HGOTO_Button.configure(font="-family {Arial Black} -size 12")

STOP_Button = tk.Button(app_window, text="STOP/RESET",command = STOP)
STOP_Button.place(relx=0.35, rely=0.743, height=38, width=130)
STOP_Button.configure(font="-family {Arial Black} -size 12")

VHome_Button = tk.Button(app_window, text= "Home",command = VHome)
VHome_Button.place(relx=0.55, rely=0.486, height=34, width=77)
VHome_Button.configure(font="-family {Arial Black} -size 12")

VGOTO_Button = tk.Button(app_window, text="GOTO", command= VGOTO)
VGOTO_Button.place(relx=0.783, rely=0.486, height=34, width=77)
VGOTO_Button.configure(font="-family {Arial Black} -size 12")

Read_Modbus()
digital_clock()
#label.after(1000, digital_clock)
app_window.mainloop()

