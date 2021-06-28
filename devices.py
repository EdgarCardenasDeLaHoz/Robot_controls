
import numpy as np

import serial
import serial.tools.list_ports as port_list
import time

import matplotlib.pyplot as plt
from datetime import datetime

import cv2
         
def clear_response(ard):

    bcleared = False
    n_tries = 5 
    for _ in range(n_tries):
        response = get_response(ard)
        if response == "": 
            bcleared = True
            break
            
    if not bcleared:
        print("response could not be cleared")
    print("Res cleared")    
    return 

def get_response(ard):
    
    response = ard.readline()
    #.split("\r")[0]
    print(response)
    return response.decode("utf-8")

def connect_to_ports(find_name):

#####        
    all_ports = list(port_list.comports())
    pos_ports = [p.device for p in all_ports  if "Arduino" in p.description]

    if len(pos_ports)==0:       print("No Port Found");       return
    
    ## Search for Suitable Port
    print(pos_ports)
    for port in pos_ports: 
        print(".")
        try:      ard = serial.Serial(port, 9600, timeout=0.1)
        except:   continue
        print("trying", port, "...", end="")
        response = read_info(ard)
        print(response, "...", end="")
        if response == find_name: 
            print("Port Found: ", port)
            break
        else:  
            ard.close()
            ard = None
    print("")

    return ard

def read_info(ard):

    for _ in range(10): 
        response = ard.readline().decode("utf-8").split("\r")[0]
        if response == "":
            print(".",end="")
        if response == "Startup":
            print("Starting up device")
            time.sleep(.1)
            break         
    ard.write(b"Info\r")
    Info = ard.readline().decode("utf-8").split("\r")[0]
    print("Device Info: "+ Info)  
    return Info

def wait_for_response(device):

    for _ in range(10): 
        response = device.readline().decode("utf-8").split("\r")[0]
        if response == "":
            print(".",end="")
        else:           
            print(response)
            return response
    return ""

class HangingRobot():

    def __init__(self, port=None):

        self.A = 180 
        self.B = 90
        self.C = 90

        #self.device = serial.Serial("COM4", 9600, timeout=0.1)

        self.connect_to_ports()

    def connect_to_ports(self):

        self.device = connect_to_ports("Robotic Arm")
        
    def set_position(self, A=None, B=None, C=None):

        print(A,B,C)
        if A is not None:             self.A = A 
        if B is not None:             self.B = B 
        if C is not None:             self.C = C 

    def move_motors(self, dA = 0, dB=0, dC = 0):

        resp = []
        
        if self.device is None: return
        ## Relative Angles to move motors
        if dA != 0:
            cmd = bytearray("M 0 "+ str(dA)+ "\r", "utf8")
            self.device.write(cmd)   
            resp.append ( self.device.readline() )
            
        if dB != 0:
            cmd = bytearray("M 1 "+ str(dB)+ "\r", "utf8")
            self.device.write(cmd) 
            resp.append ( self.device.readline() )

        if dC != 0:
            cmd = bytearray("M 2 "+ str(dC)+ "\r", "utf8")
            self.device.write(cmd) 
            resp.append ( self.device.readline() )
            # 
        print(resp)

        self.device.isMoving = True
   
    def move_to_position(self, A=None, B=None, C=None):

        ## Determine relative positions from stored absolutes
        dA,dB,dC = 0,0,0
        if A is not None:             
            #if A < 0: A = 360+A
            dA = (A - self.A)
        if B is not None:             
            dB = (-(B - self.B))
        if C is not None:             
            dC = (C - self.C)        
        
        dA, dB, dC = int(dA), int(dB), int(dC)
        #dA, dB, dC = dA, dB, dC

        self.move_motors(dA, dB, dC)
        self.set_position(A,B,C)

    def stop(self):

        if self.device is None: return

        cmd = bytearray("STOP \r", "utf8")
        self.device.write(cmd)   
        print(self.device.readline())

    def check_finished(self):

        cmd = bytearray("R \r", "utf8")
        self.device.write(cmd) 
        device = self.device
        response = wait_for_response(device)
        #print("Ready?",end="")
        if "Ready" in response:
            self.device.isMoving = False 
            print("Ready!")
        elif "Busy" in response:
            print("Busy")
        elif "" == response:
            print("No Response")

        return self.device.isMoving

class Scara():
    
    def __init__(self, port=None):
        
       
        #cv2.namedWindow( "frame", cv2.WINDOW_NORMAL)
        #self.is_on = False
        #self.run()
        self.A = 180 
        self.B = 90
        self.C = 90
        self.connect_to_ports()
        
    def run(self):      
        
        while(self.is_on):
            self.check_keys()

        self.close()
        
        print("done") 
        
    def connect_to_ports(self):

        self.device = connect_to_ports("Scara")
        
    def send_command(self, tag, value=None):
        
        ard = self.device
        
        if value is None:          value = ""
        else:                      value = str(value)
            
        cmd = bytearray(tag +  " " + value + "\r", "utf8")
        ard.write(cmd) 
        response = get_response(ard)
        return response
                
    def close(self):
        if self.device is not None:  self.device.close()
        cv2.destroyAllWindows()
         
    def move_motors(self, dA = 0, dB=0, dC = 0):

        resp = []
        print("moving robot to ")
        print(dA,dB,dC)
        if self.device is None: return
        ## Relative Angles to move motors
        if dA != 0:
            cmd = bytearray("M 0 "+ str(dA)+ "\r", "utf8")
            self.device.write(cmd)   
            resp.append ( self.device.readline() )
            
        if dB != 0:
            cmd = bytearray("M 1 "+ str(dB)+ "\r", "utf8")
            self.device.write(cmd) 
            resp.append ( self.device.readline() )

        if dC != 0:
            cmd = bytearray("M 2 "+ str(dC)+ "\r", "utf8")
            self.device.write(cmd) 
            resp.append ( self.device.readline() )
            # 
        
        print(resp)

        self.device.isMoving = True
   
    def move_b(self, b):
        self.send_command("M 0 ", b)
    
    def move_a(self,a): 
        self.send_command("M 1 ", a)
    
    def move_z(self,z):
        self.send_command("M 2 ", z)
        
    def check_keys(self): 
        
        key = cv2.waitKeyEx(1)
        if key <= 0: return

        elif key == ord("q"):     self.is_on = False 

        elif key == 2424832: ##left
            self.move_b(-2)
        elif key == 2555904: ##Right
            self.move_b(2)
        elif key == 2490368: ##up
            self.move_z(30)
        elif key == 2621440: ##Down
            self.move_z(-30)
        elif key == ord("1"):
            self.move_a(-5)
        elif key == ord("2"): 
            self.move_a(5)

    def move_to_position(self, A=None, B=None, C=None):

        ## Determine relative positions from stored absolutes
        dA,dB,dC = 0,0,0
        if A is not None:             
            #if A < 0: A = 360+A
            dA = (A - self.A)
        if B is not None:             
            dB = (-(B - self.B))
        if C is not None:             
            dC = (C - self.C)        
        
        dA, dB, dC = int(dA), int(dB), int(dC)
        #dA, dB, dC = dA, dB, dC

        self.move_motors(dA, dB, dC)
        self.set_position(A,B,C)

    def stop(self):

        if self.device is None: return

        cmd = bytearray("STOP \r", "utf8")
        self.device.write(cmd)   
        print(self.device.readline())

    def check_finished(self):

        device = self.device

        cmd = bytearray("R \r", "utf8")
        device.write(cmd) 
        response = wait_for_response(device)
        print("Ready?",end="")
        if "Ready" in response:
            device.isMoving = False 
            print("Ready!")
        elif "Busy" in response:
            print("Busy")
        elif "" == response:
            print("No Response")

        return self.device.isMoving

    def set_position(self, A=None, B=None, C=None):

        print(A,B,C)
        if A is not None:             self.A = A 
        if B is not None:             self.B = B 
        if C is not None:             self.C = C 

class Camera():
    
    def __init__(self, port=None, cam_id=None, fig= None, ax= None ):
        
        #self.device = None

        if port is not None:
            self.connect_to_ports()
        if cam_id is None: cam_id = 1
        #if cam_id2 is None: cam_id = 2
            
        self.cam = cv2.VideoCapture( cam_id )  
        #self.cam2 = cv2.VideoCapture(cam_id2) 
        self.fig = fig
        self.ax = ax
        if ax is None:
            cv2.namedWindow( "frame", cv2.WINDOW_NORMAL)
        
        self.is_on = True
        self.run()
        
    def run(self):
        
        #try:
        i = 0
        tic = time.perf_counter()
        #self.is_on = False
        while(self.is_on):

            ret, frame = self.cam.read()  
            frame = np.array(frame)
            #frame = np.rot90(frame,k=-1)
            if not frame == None:
                if self.ax is None:
                    cv2.imshow('frame',frame)
                else:
                    self.ax.imshow(frame)

            self.check_keys()

            i = i+1
            if i>100:
                toc = time.perf_counter()
                d_t = toc-tic 
                print(str(i)+ " loops takes " +str(d_t) + " seconds")
                tic = toc
                i = 0

            #self.fig.canvas.draw()
            #self.fig.canvas.flush_events()    
        #except:
        #finally:
        self.close()
        
        print("done") 
        
    def connect_to_ports(self):
        self.device = connect_to_ports("Camera")
     
    def send_command(self, tag, value=None):
        
        ard = self.device
        if value is None:          value = ""
        else:                      value = str(value)
            
        cmd = bytearray(tag +  " " + value + "\r", "utf8")

        response = ""
        if ard is not None:
            ard.write(cmd) 
            response = get_response(ard)

        return response
        
    def read_info(self,ard=None):

        return read_info(ard)
                
    def close(self):
        if self.device is not None:
            self.device.close()
        self.cam.release()
        cv2.destroyAllWindows()
         
    def rest(self):
        self.set_tilt( 125)
        self.set_rotation( 10)
        
    def home(self):
        self.set_tilt( 45)
        self.set_rotation( 120)

    def set_tilt(self, theta):                
        self.send_command("T", theta)
        
    def set_rotation(self, theta):
        self.send_command("R", theta)
        
    def tilt(self, theta ):
        self.send_command("Ts", theta)

    def rotate(self, theta):
        self.send_command("Rs", theta)
        
    def move_z(self,z):
        self.send_command("M", z)
        
    def check_keys(self): 
        
        key = cv2.waitKeyEx(1)
        if key <= 0: return

        if   key == ord("h"):     self.home()
        elif key == ord("r"):     self.rest()
        elif key == ord("q"):     self.is_on = False 

        elif key == 2424832: ##left
            self.rotate(5)
        elif key == 2555904: ##Right
            self.rotate(-5)
        elif key == 2490368: ##up
            #self.tilt(5)
            self.move_z(20)
        elif key == 2621440: ##Down
            #self.tilt(-5)
            self.move_z(-20)
