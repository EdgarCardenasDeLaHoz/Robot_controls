
import numpy as np 

class HangingModel():
    
    def __init__(self):
        
        self.motor_orients = [[0,0,1],[0,1,0],[0,0,1],
                              [0,0,1],[0,1,0],[0,1,0]]

        self.lengths = [350,300,71,41,230,180]
        self.home_position = [0,0,0,180,90,90]
        self.motor_rotation = [0,0,0,180,90,90]
        self.joint_pos = np.zeros((7,3))
        self.limits = np.array([[-10,400],[-10,450],[-10,400]])

        self.joint_pos[0] = np.array([10,400,0])

        self.home()
          
    def home(self):

        self.motor_rotation = self.home_position.copy()
        self.compute_forward()
        print(self.joint_pos)
                
    def compute_forward(self):

        x0, y0, z0 = self.joint_pos[0]

        joint_pos = []
        
        ######
        pos = [x0,y0,z0]
        joint_pos.append(pos)

        L = self.lengths[0]
        theta1 = np.radians(self.motor_rotation[0])
        pos = set_joint1(pos,theta1,L)
        joint_pos.append(pos) 

        ######
        L = self.lengths[1]
        theta2 = np.radians(self.motor_rotation[1])
        pos = set_joint2(pos,theta2,L)
        joint_pos.append(pos) 

        ######
        L = self.lengths[2]
        theta3 = np.radians(self.motor_rotation[2])
        pos = set_joint3(pos,theta3,L)
        joint_pos.append(pos) 

        ###########################################################
        theta1 = np.radians(self.motor_rotation[3])
        theta2 = np.radians(self.motor_rotation[4])
        theta3 = np.radians(self.motor_rotation[5])
        thetas = (theta1,theta2,theta3)
        ######

        Ls = self.lengths[3:6]
        joints = forward_art_robot(pos, thetas, Ls)
        joint_pos.extend(joints)
        ###### 

        self.joint_pos = np.array(joint_pos)
        
    def compute_inverse(self,x=None,y=None,z=None):        

        dx = x - self.joint_pos[-4][0]
        dy = y - self.joint_pos[-4][1]
        z1 = z - self.joint_pos[-4][2] 

        z1 = z1 * -1

        theta1 = np.arctan2(dy, dx)
        #########
        L_1,A_L,A_U = self.lengths[3:]

        L1 = np.sqrt(dx**2 + dy**2) - L_1
        L7 = np.sqrt(L1**2 + z1**2)
        
        A_L2 = A_L ** 2 
        A_U2 = A_U ** 2
        L72  = L7  ** 2 
        #########
        a = z1 / L7
        b = ( L72  + A_L2 - A_U2 ) / (2 * L7 * A_L)
        c = ( A_L2 + A_U2 - L72  ) / (2 * A_U * A_L)    

        sides = np.array([a,b,c])
        if any(np.abs(sides) > 1):
            print("Clicked Out of Range") 
            sides = np.minimum(sides,1)
            sides = np.maximum(sides,-1)
        a,b,c = sides

        ############
        theta2 = np.arctan2( a , np.sqrt(1 - a**2)) + \
                 np.arctan2( np.sqrt(1-b**2) , b) 
        
        theta3 = np.arctan2( np.sqrt(1 - c**2), c )
        ##########

        theta_1 = np.degrees(theta1)
        theta_2 = np.degrees(theta2)
        theta_3 = 180 - np.degrees(theta3)

        self.motor_rotation[3:] = [theta_1,theta_2,theta_3]
        self.compute_forward()

##########

def set_joint1(pos0, theta, L):

    x0,y0,z0 = pos0

    x = x0 + theta
    y = y0 + theta 
    z = z0 + L
    pos = np.array([x,y,z])

    return pos
 
def set_joint2(pos0, theta, L):

    x0,y0,z0 = pos0

    x = x0 + np.cos(theta) * L
    y = y0 + np.sin(theta) * L
    z = z0 + 0
    pos = np.array([x,y,z])

    return pos

def set_joint3(pos0, theta, L):

    x0,y0,z0 = pos0

    x = x0 + np.cos(theta) * 0 
    y = y0 + np.sin(theta) * 0
    z = z0 - L
    pos = np.array([x,y,z])

    return pos

def foward_joint(pos, orient1, theta, orient2, L):

    orient = np.cross(orient1,orient2)

    x0,y0,z0 = pos

    x = x0 + np.cos(theta) * orient[0] * L
    y = y0 + np.cos(theta) * orient[1] * L
    z = z0 + np.cos(theta) * orient[2] * L
    pos = np.array([x,y,z])

    return pos

def forward_art_robot(pos0, thetas, Ls):

    x,y,z = pos0
    theta1, theta2, theta3 = thetas
    L1,L2,L3 = Ls 

    x = x + np.cos(theta1) * L1
    y = y + np.sin(theta1) * L1
    z = z + 0

    pos1 = [x,y,z]
    
    #####
    R1 = np.cos(theta2)*L2
        
    x = np.cos(theta1)*R1 + x
    y = np.sin(theta1)*R1 + y
    z = -np.sin(theta2) * L2  + z

    pos2 = [x,y,z]

    ####
    theta4 = theta3 - (theta2)

    H2 = np.sin(theta4)*L3
    R2 = np.cos(theta4)*L3

    x = np.cos(theta1)*R2 + x
    y = np.sin(theta1)*R2 + y 
    z = z + H2 

    pos3 = [x,y,z]  

    return np.array([pos1,pos2,pos3])

###########

class ScaraModel():
    
    def __init__(self):
        
        self.motor_orients = [[0,0,1],[0,1,0],[0,0,1]]

        self.joint_pos = np.zeros((4,3))
        self.joint_pos[0] = np.array([0,0,0])
        self.limits = np.array([[-500,500],[-500,500],[-10,500]])

        self.home()
          
    def home(self):

        self.lengths = np.array([100,250,150])
        self.motor_rotation = np.array([0,0,0])
        self.compute_forward()
                        
    def compute_forward(self):

        x0, y0, z0 = self.joint_pos[0]

        joint_pos = []
        
        ######
        pos = np.array([x0,y0,z0])
        joint_pos.append(pos)

        L = self.lengths[0]
        #theta1 = np.radians(self.motor_rotation[0])
        pos = pos + np.array([0,0,1]) * L

        ##
        joint_pos.append(pos) 

        ######
        L = self.lengths[1]
        rot = self.motor_rotation[1]
        theta2 =  np.radians(rot)
        pos = pos + np.array([np.cos(theta2), np.sin(theta2), 0]) * L
        joint_pos.append(pos) 

        ######
        L = self.lengths[2]
        rot = self.motor_rotation[2]
        theta3 = np.radians(rot)

        thetaC =  theta2 + theta3
        pos = pos + np.array([np.cos(thetaC), np.sin(thetaC), 0]) * L
        joint_pos.append(pos) 
        ###### 

        self.joint_pos = np.array(joint_pos)
        
    def compute_inverse(self,x=None,y=None,z=None):   

        lengths = self.lengths
        rotations = self.motor_rotation

        x1,y1,z1 = self.joint_pos[-1]

        if x is None: x = x1
        if y is None: y = y1
        if z is None: z = z1

        lengths[0] = z 
        rotations[0] = 0 

        L_AC = np.sqrt(x**2 + y**2)        
        L_AB = lengths[1]
        L_BC = lengths[2]
        #########
        a = y / L_AC
        b = ( L_AC**2  + L_AB**2 - L_BC**2 ) / (2 * L_AC * L_AB)
        c = ( L_AB**2  + L_BC**2 - L_AC**2  ) / (2 * L_BC * L_AB)    

        sides = np.array([a,b,c])
        if any(np.abs(sides) > 1): print("Clicked Out of Range") 
        sides = np.minimum(sides,1)
        sides = np.maximum(sides,-1)
        a,b,c = sides

        ############
        theta2 = np.arctan2( a , np.sqrt(1 - a**2)) + \
                 np.arctan2( np.sqrt(1-b**2) , b) 
        
        theta3 = np.arctan2( np.sqrt(1 - c**2), c )
        ##########

        theta2 = np.degrees(theta2)
        theta3 = np.degrees(theta3)-180

        rotations[1] = theta2
        rotations[2] = theta3 

        self.lengths = lengths
        self.motor_rotation = rotations
        self.compute_forward()

