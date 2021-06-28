
import numpy as np 
import matplotlib.pyplot as plt 

import threading

from matplotlib.widgets import Button
from matplotlib.patches import Arc

from functools import partial 

from skimage import transform

import time
from devices import *
from kinematics import *
#from camera_tools import *
import torch

class control_gui():
    
    def __init__(self, model="Art", use_camera = True):

        if model == "Art":
        
            self.motors = HangingRobot()
            self.model = HangingModel()

        elif model == "Scara":

            self.motors = Scara()
            self.model = ScaraModel()
            
        self.p_idx = 0
        self.path =  []
        self.step_xyz = 1
        self.step_theta = 1

        self.command_queue = []

        limits = self.model.limits

        self.cameras = None 
        if use_camera:
            self.cameras = CameraConnection()
        else:
            self.cameras = None
        self.set_up_figure(limits)        
        axs = self.fig.get_axes()
        


        #self.Camera = Camera(fig = self.fig, ax = axs[4] )
        #self.Camera = Camera()


        plt.rcParams['keymap.fullscreen'] = []

    def run_commands(self, new_commands):

        self.command_queue.extend(new_commands)
        #while self.fig.isOpen:
            #if not plt.fignum_exists(self.fig): 
            #self.fig.isOpen  = False 

        while self.command_queue:
            
            isfinished = self.motors.check_finished()

            if not isfinished:
                print("Executing Command")
                pos = self.command_queue.pop()
                self.model.compute_inverse(*pos)
                self.draw_robot_2D()
                self.move_to_model()

            time.sleep(0.1) 
            
    def draw_image( self ):

        still_open = plt.fignum_exists(self.fig.number)

        if self.fig is None or  still_open==False:
            self.set_up_figure()
    
        self.draw_robot_2D()
        self.add_table()

        return self.fig
    
    def set_step(self, step):

        self.step_xyz = step

    def set_up_figure(self, limits=None):

        #fig, axs = plt.subplots(1,3, figsize=(40,20), facecolor=(0.1,0.1,0.3))
        #fig.subplots_adjust(left=.02, bottom=.45, right=.85, top=.98,   wspace=.08, hspace=.04)

        fig = plt.figure(figsize=(28,18), facecolor=(0.1,0.1,0.3))
        self.fig = fig
        self.fig.canvas.mpl_connect('button_press_event', self.onClick)
        self.fig.canvas.mpl_connect('key_press_event', self.onKey)
        self.fig.canvas.mpl_connect('scroll_event', self.onScroll)
        
        


        sx = 1.4

        ax1 = plt.axes([0.03*sx, 0.42, 0.22*sx, 0.56])
        ax2 = plt.axes([0.27*sx, 0.05, 0.25*sx, 0.42])
        ax3 = plt.axes([0.27*sx, 0.57, 0.25*sx, 0.42])
        ax4 = plt.axes([0.56*sx, 0.35, 0.12*sx, 0.63])
        #ax5 = plt.axes([0.7*sx, 0.5*sx, 0.28, 0.48])

        axs = [ax1,ax2,ax3,ax4]

        ax_list = [[0,1], [0,2], [1,2]]
        
        if limits is None: limits = ((-10,450),(-10,450),(-10,400))


        labels = ["X axis","Y axis","Z axis"]

        for a in range(3):
            axs[a].set_xlim(*limits[ax_list[a][0]])
            axs[a].set_ylim(*limits[ax_list[a][1]])
            axs[a].set_xlabel( labels[ax_list[a][0]],fontsize=10, color="w")
            axs[a].set_ylabel( labels[ax_list[a][1]],fontsize=10, color="w")  
            axs[a].grid("True")
            axs[a].set_aspect("equal")
    

        callbacks = []

        #################
        name_list = ["Home","Set Home", "Stop","Set Position"]
        self.make_button_panel( name_list, 0.02*sx,0.25*sx, 0.32,0.4, 2,2)

        callbacks.append(self.home )
        callbacks.append(self.home )
        callbacks.append(self.stop )
        callbacks.append(self.set_motor_position)

        ################
        ################
        name_list = [".5 mm", "1 mm","10 mm" ]
        self.make_button_panel( name_list, 0.02*sx,0.14*sx, 0.25, 0.3, 3,1)

        callbacks.append(partial(self.set_step, .5) )
        callbacks.append(partial(self.set_step,  1) )
        callbacks.append(partial(self.set_step, 10) )

        name_list = ["X--", "Y--","Z--", "X++","Y++", "Z++" ]
        self.make_button_panel( name_list, 0.04*sx,0.12*sx, 0.1,0.25, 2,3)

        callbacks.append( partial(self.move_step, dim = 0 ,dir = -1  ) )
        callbacks.append( partial(self.move_step, dim = 1 ,dir = -1  ) )
        callbacks.append( partial(self.move_step, dim = 2 ,dir = -1  ) )
        callbacks.append( partial(self.move_step, dim = 0 ,dir = 1  ) )
        callbacks.append( partial(self.move_step, dim = 1 ,dir = 1  ) )
        callbacks.append( partial(self.move_step, dim = 2 ,dir = 1  ) )

        #################
        #################
        name_list = ["1'", "10 '" ]
        self.make_button_panel( name_list, 0.16*sx,0.25*sx, 0.25,0.3, 2,1)

        callbacks.append(self.draw_image )
        callbacks.append(self.draw_image )

        name_list = ["A--", "B--","C--", "A++","B++", "C++" ]
        self.make_button_panel( name_list, 0.17*sx,0.24*sx, 0.1,0.25, 2,3)

        callbacks.append(self.draw_image )
        callbacks.append(self.draw_image )
        callbacks.append(self.draw_image )
        callbacks.append(self.draw_image )
        callbacks.append(self.draw_image )
        callbacks.append(self.draw_image )

        #################
        #################
        name_list = ["Remove Path", "Select Back", "Move Back","Path Add","Select Forward","Move Foward" ]
        self.make_button_panel( name_list, 0.55*sx,0.70*sx, 0.1,0.3, 2,3)

        callbacks.append( self.remove_path )
        callbacks.append( partial(self.next, -1) )  
        callbacks.append( partial(self.move_to_path, d=-1 ))
        callbacks.append( self.add_path )
        callbacks.append( partial(self.next, 1))
        callbacks.append( partial(self.move_to_path, d=1))  

        self.callbacks = callbacks

        self.draw_image()

    def next(self, d ):
        
        pidx = self.p_idx + d 
        pidx = np.minimum(pidx,  len(self.path)-1)
        pidx = np.maximum(pidx,  0)
        self.p_idx = pidx

        ax = self.fig.get_axes()[3]
        ax.set_xlabel(str(self.p_idx), color = "w", fontsize=35)

        self.fig.canvas.draw()
        self.fig.canvas.flush_events()

    def add_path(self):

        pos = np.array(self.model.joint_pos[-1])
        #self.path.insert(pos , int(self.p_idx))
        self.path.append(pos)
        self.add_table()

    def remove_path(self):
        if len(self.path)>0:
            self.path.pop()
        self.add_table()

    def move_to_path(self, d=1):
        
        #pos = np.array( self.model.joint_pos[-1]  )
        pos = np.array(self.path[int(self.p_idx)])
        self.model.compute_inverse(*pos)
        self.next(d)
        self.draw_robot_2D()
        self.move_to_model()
        
    def make_button_panel(self,names, x1,x2, y1,y2, nx,ny):

        xw = (x2-x1)/nx  
        yw = (y2-y1)/ny  

        xwp = xw - 0.01
        ywp = yw - 0.01        

        pos_list = []
        for x in np.linspace(x1,x2-xw,nx):
            for y in np.linspace(y2-yw,y1,ny):
                pos_list.append([x,y, xwp, ywp])

        for i in range(len(names)):
            self.add_button(pos_list[i], None , names[i] )

    def add_button(self, pos, function, text ):
        ax = plt.axes(pos)
        button = Button(ax, text )
        #button.on_clicked(function)
        button.label.set_fontsize(10)

    def home(self):
        print("home")
        self.model.home()
        self.move_to_model()
        self.draw_robot_2D()

    def stop(self):
        print("stop")
        self.motors.stop()
        self.draw_robot_2D()

    def set_motor_position_input(self, endxyz):
        print("Setting Motor Position")
        A,B,C = self.model.motor_rotation[3:]
        self.motors.set_position(A,B,C)


    def set_motor_position(self):
        print("Setting Motor Position")
        A,B,C = self.model.motor_rotation[3:]
        self.motors.set_position(A,B,C)

    def draw_robot_2D(self):

        self.clear_plots()
        self.draw_segments()
        self.draw_camera()
        self.draw_joint_angles()
       
        self.fig.canvas.draw()
        self.fig.canvas.flush_events()


    def clear_plots(self):

        axs = self.fig.get_axes()
        for ax in axs[0:3]:
            ax.texts = []
            ax.lines = []
            ax.patches = []

    def draw_segments(self):

        model = self.model
        model.compute_forward()
        
        #######
        colors = "rbgmcy"
        axs = self.fig.get_axes()
        ax_list = [[0,1], [0,2], [1,2]]
        
        P = model.joint_pos
        for i in range(1,len(P)):

            P_0 = P[i-1]
            clr = colors[i-1]
            for a in range(3):
                x0,y0 = np.array(P_0)[ax_list[a]]
                x1,y1 = np.array(P[i])[ax_list[a]]
                axs[a].plot([x0,x1],[y0,y1], clr, linewidth=10)
                axs[a].plot(x1,y1, clr+"o" , markersize=10)

            P_0 = P[i]
        # Write positions in title 
        End = np.round(P[-1],2)
        Rot = np.round(model.motor_rotation[-3:],2)

        if Rot[0] < 0: Rot[0] = 360+Rot[0]

        title_str = "X: " +  str(End[0]) + "         Y: " + str(End[1]) + "        Z: "  + str(End[2]) + "\n"
        title_str = title_str + "A: " +  str(Rot[0]) + "         B: " + str(Rot[1]) + "        C: "  + str(Rot[2])
        axs[1].set_title(title_str, color = "white", fontsize= 15)
        
    def draw_camera(self):
        cameras = self.cameras
        if cameras is None: return 

        #######
        colors = "rbgmcy"
        axs = self.fig.get_axes()
        ax_list = [[0,1], [0,2], [1,2]]
        rotation_math = [[0,0],[1,2],[0,2]]
        rotation_math2 = [[2,1],[0,0],[1,0]]
        P_0 = cameras.position
        ori = cameras.orientation
        for a in range(3):
            x0,y0 = P_0[ax_list[a]]
            rot1 = np.cos(np.radians(ori[rotation_math[a]]))
            #print("rot1",rot1)
            rot2 = np.sin(np.radians(ori[rotation_math2[a]]))
            #print("rot2",rot2)
            dx = rot1*rot2*50
            #print("coord",x0,y0)
            #print("direction",dx)
            x1,y1 = P_0[ax_list[a]] + dx
            axs[a].plot([x0,x1],[y0,y1], "k", linewidth=1)
            axs[a].plot(x0,y0, "k"+"o" , markersize=5)

        im,im2 = cameras.get_frame()
        extent = (440, 10, 380, 97.5)
        axs[0].imshow(im, cmap= plt.cm.hot, origin='upper', extent=extent)

        #im2 = cameras.get_frame()[1]
        extent = (400, 0, -85, 215)
        axs[2].imshow(im2, cmap=plt.cm.hot, origin='upper', extent=extent)
        
    def get_position_camera(self,model,side,top):
        x,y,z = recon_3D(model, side, top) 
        End = round(x),round(y),round(z)
        return End

    def get_position(self, joint=-1):

        P = self.model.joint_pos
        End = np.round(P[joint],2)
        return End

    def draw_joint_angles(self):

        model = self.model
        axs = self.fig.get_axes()

        ax_list = [[0,1], [0,2], [1,2]]
        colors = "rbgmcy"
        P = model.joint_pos

        for i in range(2,len(P)):

            for a in range(3):
        
                A = np.array(P[i-2])
                Ori = np.array(P[i-1])
                B = np.array(P[i])

                x0,y0 = Ori[ax_list[a]]
                x1,y1 = A[ax_list[a]]
                x2,y2 = B[ax_list[a]]

                line1 = [x0,x1,y0,y1]
                line2 = [x0,x2,y0,y2]

                draw_angle( axs[a], line1, line2,  color=colors[i-1])

    def add_table(self):

        positions = self.path
        
        columns = ('X', 'Y', 'Z')

        cell_text = []
        for _ in range(30):
            cell_text.append(["." for _ in range(3)])

        for n, pos in enumerate(positions):
            cell_text[n] = ['%1.1f' % x for x in pos]

        ax = self.fig.get_axes()[3]
        ax.table(cellText=cell_text,  colLabels=columns, bbox=[0,0,1,1], fontsize=10)
        ax.set_xlabel(str(self.p_idx), color="w", fontsize=10)

        self.fig.canvas.draw()
        self.fig.canvas.flush_events()

    #######################

    def onKey(self, event):

        if event.key == 'right':      print("x")
        if event.key == 'left':       print("x")
        if event.key == 'up':         print("x")
        if event.key == 'down':       print("x")
        if event.key == 'enter':
            move_to_camera(self,event,1)  
        if event.key == 'backspace':
            move_to_camera(self,event,2) 
        if event.key == 'escape':     print("x")
        if event.key == 'space':      print("x")
        if event.key == "f":          print("x")

    def onClick(self,event):

        if event.button==1 or event.button==3:
            if event.inaxes:

                ax_idx = np.where([ax is event.inaxes for ax in self.fig.get_axes()])[0][0]
                print(ax_idx)

                if ax_idx <= 2:

                    axs_axis = np.array([[0,1],[0,2],[1,2]])
                    ax_change = axs_axis[ax_idx]

                    x,y = event.xdata ,event.ydata
                    pos = np.array( self.model.joint_pos[-1]  )
                    pos[ax_change] = x,y
                    self.model.compute_inverse(*pos)
                    self.draw_robot_2D()

                    if event.button==3: ## Right Button
                        self.move_to_model()

                if ax_idx>3:
                    self.callbacks[ax_idx-4]()

    def onScroll(self,event):
        print("scrolling")

    #######################
    def move_to_model(self):
        mot_rot = self.model.motor_rotation[3:]
        self.motors.move_to_position(*mot_rot)  

    def move_relative(self, x=0, y=0, z=0):
        pos = np.array( self.model.joint_pos[-1]  )
        pos = pos + np.array((x,y,z))
        self.model.compute_inverse(*pos) 
        self.move_to_model()
        self.draw_robot_2D()

    def move_step(self, dim=0, dir=1.):

        step = np.array((0.,0.,0.))
        step[dim] = step[dim] + self.step_xyz * dir
        pos = np.array( self.model.joint_pos[-1]  )
        pos = pos + step

        self.model.compute_inverse(*pos) 
        self.move_to_model()
        self.draw_robot_2D()

############################
##
############################


def draw_angle(ax, line1, line2, color = None, offset = 50 ):

    l1x0,l1x2,l1y0,l1y2 = line1
    l2x0,l2x2,l2y0,l2y2 = line2

    # Angle between line1 and x-axis
    dy1,dx1 = (l1y2 - l1y0), (l1x2 - l1x0)
    angle1 = np.degrees(np.arctan2(dy1,dx1))

    # Angle between line2 and x-axis
    dy2,dx2 = (l2y2 - l2y0), (l2x2 - l2x0)
    angle2 = np.degrees(np.arctan2(dy2,dx2))

    dx_mid = (dx1 + dx2) / 2
    dy_mid = (dy1 + dy2) / 2

    angle = angle2 - angle1
    angle = int(angle)
    label = str(angle)+u"\u00b0"

    if color is None:
        color = "k"

    origin = (l1x0,l1y0)

    arc = Arc(origin, offset, offset, 0, angle1, angle2, color=color, label = label )

    ax.add_patch(arc)
    x = origin[0] + dx_mid * 0.1
    y = origin[1] + dy_mid * 0.1
    ax.text( x,y,    label     )

    return 
def move_to_camera(self,event,t):
    imside = self.cameras.getNextFrame1()
    imtop = self.cameras.getNextFrame()
    x_det,y_det,z_det = recon_3D(self.cameras.robot_model, imside, imtop)
    x_in,y_in,z_in = det_to_input(x_det,y_det,z_det)
    x,y,z = x_in,y_in,z_in
    print("xyz",x,y,z)
    update_2D_robots(self,x,y,z)
    ok = check_range(self,x,y)
    if ok == 1 :
        self.set_motor_position()
    else :
        print("Motor position not set, retry")
    tx,ty = 175,310
    tx1,ty1 = 340,150
    tz = 50
    pts_side = detect_mouse_prop(imside,self.cameras.mouse_model)[0]
    pts_top = detect_mouse_prop(imtop,self.cameras.mouse_model)[0]

    print("pts",pts_side,pts_top)
    #tx,ty,tz = find_3D_pts_single(pts_side,pts_top)
    #tx,ty,tz = det_to_input(tx,ty,tz)
    print(tx,ty,tz)
    tar = float_to_int(pts_top)
    image = cv2.circle(imtop, tar, radius=1, color=(0, 0, 255), thickness=2)
    cv2.imshow("img",image)
    dx = abs(tx-x)
    dx1 = abs(tx1-x)

    dy = abs(ty-x)
    dy1 = abs(ty1-x)

    dz = abs(tz - z)
    print("ok",ok)
    if (ok == 1):
        if (t==1)&((dx >10) | (dy > 10)|(dz > 10)):
            x,y,z = tx,ty,tz
            update_2D_robots(self,x,y,z)
            self.move_to_model()
            while self.motors.check_finished() == True:
                time.sleep(1)
            self.draw_robot_2D()
        if (t==2)&((dx1 > 10) | (dy1 > 10)|(dz > 10)): 
            x,y,z = tx1,ty1,tz 
            update_2D_robots(self,x,y,z)
            self.move_to_model()
            while self.motors.check_finished() == True:
                time.sleep(1)
            self.draw_robot_2D()
def check_range(self,x,y):
    if (x > 450) | (x < -20) : 
        print("Robot detected out of range")
        ok = 0
    elif (y > 380) | (y < 97.5):
        print("Robot detected out of range")
        ok = 0
    else : 
        ok = 1
    return ok
def adjust_position(self,tpos,rpos):
    t=1
def update_2D_robots(self,x,y,z):
    axs_axis = np.array([[0,1],[0,2],[1,2]])
    ax_idx = [0,2]
    ax_change = axs_axis[ax_idx]
    pos = np.array( self.model.joint_pos[-1]  )
    pos[ax_change] = [x,y],[y,z]
    self.model.compute_inverse(*pos)
    self.draw_robot_2D()
def move_to_cameraCOPY(self,event,t):
    if event.inaxes:
        ax_idx = np.where([ax is event.inaxes for ax in self.fig.get_axes()])[0][0]
        print(ax_idx)
    if ax_idx <= 2:
        axs_axis = np.array([[0,1],[0,2],[1,2]])
        ax_change = axs_axis[ax_idx]
        imside = self.cameras.getNextFrame1()
        imtop = self.cameras.getNextFrame()
        x_det,y_det,z_det = recon_3D(self.cameras.robot_model, imside, imtop)
        x_in,y_in,z_in = det_to_input(x_det,y_det,z_det)
        x,y = x_in,y_in
        pos = np.array( self.model.joint_pos[-1]  )
        pos[ax_change] = x,y
        self.model.compute_inverse(*pos)
        self.draw_robot_2D()
        ok = check_range(self,x,y)
        if ok == 1 :
            self.set_motor_position()
        else :
            print("Motor position not set, retry")
        
        tx,ty = 175,310
        tx1,ty1 = 340,150

        dx = abs(tx-x)
        dx1 = abs(tx1-x)

        dy = abs(ty-x)
        dy1 = abs(ty1-x)
        if (ok == 1):
            if (t==1)&((dx >10) | (dy > 10)):
                x,y = tx,ty
                pos = np.array( self.model.joint_pos[-1]  )
                pos[ax_change] = x,y
                self.model.compute_inverse(*pos)
                self.draw_robot_2D()
                self.move_to_model()
                time.sleep(2)
                self.draw_robot_2D()
                print("image updated")
            if (t==2)&((dx1 > 10) | (dy1 > 10)): 
                x,y = tx1,ty1
                pos = np.array( self.model.joint_pos[-1]  )
                pos[ax_change] = x,y
                self.model.compute_inverse(*pos)
                self.draw_robot_2D()
                self.move_to_model()
                self.draw_camera()

        if ax_idx>3:
            self.callbacks[ax_idx-4]()
class CameraConnection():

    def __init__(self):
        self.position = np.array([200,400,350])
        self.orientation = np.array([30,90,0])
        
        self.orientation[0] = self.orientation[0] + 180

        self.robot_model = torch.load('.\\models\\robot_all_1.pt',map_location=torch.device('cpu'))
        self.mouse_model = torch.load('.\\models\\robot_mouse_2.pt',map_location=torch.device('cpu'))

        self.t = 0

        self.lock = threading.Lock()
        self.openVideo(1)
        self.openVideo1(0)


    def openVideo(self, camid):
        self.lock.acquire()
        self.videoCap = cv2.VideoCapture(camid)
        #self.videoCap = cv2.VideoCapture('./Test videos/5B.avi')
        self.lock.release()
    
    def openVideo1(self, camid):
        self.lock.acquire()
        self.videoCap1 = cv2.VideoCapture(camid)
        #self.videoCap1 = cv2.VideoCapture('./Test videos/5.avi')
        if self.videoCap1.isOpened():
            ret, img = self.videoCap1.read()
            #cv2.imshow('frame',img)
        self.lock.release()
    
    def getNextFrame(self):
        self.lock.acquire()
        img = None
        # if no video opened return None
        if self.videoCap.isOpened():
            ret, img = self.videoCap.read()
            #cv2.imshow('frame',img)
        self.lock.release()
        return img
    
    def getNextFrame1(self):
        self.lock.acquire()
        img = None
        # if no video opened return None
        if self.videoCap1.isOpened():
            ret, img = self.videoCap1.read()
        self.lock.release()
        return img

    def get_frame(self):
        fn = "C:\\Users\\jarne\\Universiteit Antwerpen\\Plasma Robotics - General\\Camera\\Test images\\WARP1B.jpg"
        fn2 = "C:\\Users\\jarne\\Universiteit Antwerpen\\Plasma Robotics - General\\Camera\\Test images\\WARP1.jpg"
        #im = cv2.imread(fn)
        points_of_interest =[[134 ,367], 
                            [152, 56], 
                            [548, 29], 
                            [589, 350]]
        projection = [[134, 367],
                    [134, 17],
                    [554, 17],
                    [554, 367]]
        points_of_interest = np.array(points_of_interest)
        projection = np.array(projection)
        tform = transform.estimate_transform('projective', points_of_interest, projection)
        im = self.getNextFrame()
        im = transform.warp(im, tform.inverse, mode = 'edge')
        #im2 = cv2.imread(fn2)
        im2 = self.getNextFrame1()
        im2 = transform.warp(im2, tform.inverse, mode = 'edge')
        
        return im, im2

