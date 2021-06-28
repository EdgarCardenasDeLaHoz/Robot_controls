
import numpy as np

class robot_model():
    
    def __init__(self):
        
        #self.origin = [300,400,350]
        self.motor_orients = [[0,0,-1],[0,0,-1],[-1,0,0],[0,0,-1],[0,0,-1],[-1,0,0]]

        self.lengths = [[0,0,50],[0,0,50],[40,0,0],[0,0,180],[0,0,30],[190,0,0]]

        self.home_position = [0,90,90]

        self.motor_rotation = [0,90,90]
        self.joint_pos = [[0,0,0]] * len(self.motor_rotation)
        self.home()
          
    def home(self):

        self.motor_rotation = self.home_position.copy()
        self.compute_forward()
        print(self.joint_pos)

                
    def compute_forward(self):
        self.origin = [300,400,250]
        self.origin2 = [300,400,250]
        x0, y0, z0 = self.origin2

        joint_pos = []

        x = x0
        y = y0
        z = z0
        pos = [x,y,z]
        joint_pos.append(pos)
      
        ######joint3
        L0=40
        theta1=np.radians(self.motor_rotation[0])
        self.origin3 = [260,400,250]
        x3, y3, z3 = self.origin3

        L0x=L0*self.motor_orients[2][0]
        L0y=L0*self.motor_orients[2][1]
        z_LOr=self.lengths[2][2]*self.motor_orients[2][2]

        x = x - np.cos(theta1) * L0
        y = y - np.sin(theta1) * L0
        z = z
        pos = [x,y,z]
        joint_pos.append(pos)

        ######joint4
        Al=177
        theta2=np.radians(self.motor_rotation[1])

        Alx=Al*self.motor_orients[3][0]
        Aly=Al*self.motor_orients[3][1]
        Alz=Al*self.motor_orients[3][2]
      
        x = x - (np.cos(theta1) * (np.cos(theta2) * Al))
        y = y - (np.sin(theta1) * (np.cos(theta2) * Al))
        z = z - (np.sin(theta2) * Al)
        pos = [x,y,z]
        joint_pos.append(pos)

        ######joint5
        Ju=30

        Jux=(self.lengths[4][0]+Ju)*self.motor_orients[4][0]
        Juy=(self.lengths[4][1]+Ju)*self.motor_orients[4][1]
        Juz=(self.lengths[4][2]+Ju)*self.motor_orients[4][2]
        
        x = x - (np.cos(theta1) * np.cos(theta2) * Ju)
        y = y - (np.sin(theta1) * np.cos(theta2) * Ju)
        z = z - (np.sin(theta2) * Ju)
        pos = [x,y,z]
        joint_pos.append(pos)

        ######joint6

        theta3=np.radians(self.motor_rotation[2])
        Auu=190
        Au=Auu/(np.sin(np.pi-theta3))
        
        Aux=Au*self.motor_orients[5][0]
        Auy=Au*self.motor_orients[5][1]
        Auz=Au*self.motor_orients[5][2]
                
        x = x - np.cos(theta1) * np.sin(theta3 - ((np.pi/2)-theta2)) * Au
        y = y - np.sin(theta1) * np.sin(theta3 - ((np.pi/2)-theta2)) * Au
        z = z - np.cos(theta3 - ((np.pi/2)-theta2)) * Au
        pos = [x,y,z]
        joint_pos.append(pos)
        self.joint_pos = joint_pos
        print(self.joint_pos[-4][0])
        print(self.joint_pos[-4][1])
        print(self.joint_pos[-4][2])
        
    def compute_inverse(self,x=None,y=None,z=None):        

        dx = x - self.joint_pos[-4][0]
        dy = y - self.joint_pos[-4][1]
        z1 = z - self.joint_pos[-4][2] 

        z1 = z1 * -1

        theta1 = np.arctan2(dy, dx)
        #########
        
        Al=177+30
        theta3=np.radians(self.motor_rotation[2])
        Auu=190
        Au=Auu/(np.sin(np.pi-theta3))
        L_1=self.lengths[5][0]
        #L_1,A_L,A_U = self.lengths[3:]

        L1 = np.sqrt(dx**2 + dy**2) - L_1
        L7 = np.sqrt(L1**2 + z1**2)
        
        A_L2 = Al ** 2 
        A_U2 = Au ** 2
        L72  = L7  ** 2 
        #########
        a = z1 / L7
        b = ( L72  + A_L2 - A_U2 ) / (2 * L7 * Al)
        c = ( A_L2 + A_U2 - L72  ) / (2 * Au * Al)    

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

        theta_1 = -np.degrees(theta1)
        theta_2 = np.degrees(theta2)
        theta_3 = 180 - np.degrees(theta3)

        self.motor_rotation = [theta_1,theta_2,theta_3]
        self.compute_forward()
        print("new angle")
        print(theta1)
        print(theta2)
        print(theta3)
        print("new position")


class robot_model1():
    
    def __init__(self):
        
        self.origin = [300,400,350]
        self.motor_orients = [[0,0,-1],[0,0,-1],[-1,0,0],[0,0,-1],[0,0,-1],[-1,0,0]]

        self.lengths = [[0,0,50],[0,0,50],[40,0,0],[0,0,180],[0,0,30],[190,0,0]]

        self.home_position = [0,90,90]

        self.motor_rotation = [0,90,90]
        self.joint_pos = [[0,0,0]] * len(self.motor_rotation)
        self.home()
          
    def home(self):

        self.motor_rotation = self.home_position.copy()
        self.compute_forward()
        print(self.joint_pos)

                
    def compute_forward(self):

        x0, y0, z0 = self.origin

        joint_pos = []

        ######joint1  
        
        x_LOr=self.lengths[0][0]*self.motor_orients[0][0]
        y_LOr=self.lengths[0][1]*self.motor_orients[0][1]
        z_LOr=self.lengths[0][2]*self.motor_orients[0][2]

        x = x0
        y = y0
        z = z0 + z_LOr
        pos = [x,y,z]
        joint_pos.append(pos)

        ######joint2
        x_LOr=self.lengths[1][0]*self.motor_orients[1][0]
        y_LOr=self.lengths[1][1]*self.motor_orients[1][1]
        z_LOr=self.lengths[1][2]*self.motor_orients[1][2]
        
        x = x0 + x_LOr
        y = y0 + y_LOr
        z = z + z_LOr
        pos = [x,y,z]
        joint_pos.append(pos)  
       
        ######joint3
        L0=40
        theta1=np.radians(self.motor_rotation[0])

        L0x=L0*self.motor_orients[2][0]
        L0y=L0*self.motor_orients[2][1]
        z_LOr=self.lengths[2][2]*self.motor_orients[2][2]

        x = x + np.cos(theta1) * L0x
        y = y + np.sin(theta1) * L0y
        z = z
        pos = [x,y,z]
        joint_pos.append(pos)

        ######joint4
        Al=177
        theta2=np.radians(self.motor_rotation[1])

        Alx=Al*self.motor_orients[3][0]
        Aly=Al*self.motor_orients[3][1]
        Alz=Al*self.motor_orients[3][2]
      
        x = x + (np.cos(theta1) * (np.cos(theta2) * Alx))
        y = y + (np.sin(theta1) * (np.cos(theta2) * Aly))
        z = z + (np.sin(theta2) * Alz)
        pos = [x,y,z]
        joint_pos.append(pos)

        ######joint5
        Ju=30

        Jux=(self.lengths[4][0]+Ju)*self.motor_orients[4][0]
        Juy=(self.lengths[4][1]+Ju)*self.motor_orients[4][1]
        Juz=(self.lengths[4][2]+Ju)*self.motor_orients[4][2]
        
        x = x + (np.cos(theta1) * np.cos(theta2) * Jux)
        y = y + (np.sin(theta1) * np.cos(theta2) * Juy)
        z = z + (np.sin(theta2) * Juz)
        pos = [x,y,z]
        joint_pos.append(pos)

        ######joint6

        theta3=np.radians(self.motor_rotation[2])
        Auu=190
        Au=Auu/(np.sin(np.pi-theta3))
        
        Aux=Au*self.motor_orients[5][0]
        Auy=Au*self.motor_orients[5][1]
        Auz=Au*self.motor_orients[5][2]
                
        x = x + np.cos(theta1) * np.sin(theta3 - ((np.pi/2)-theta2)) * Aux
        y = y + np.sin(theta1) * np.sin(theta3 - ((np.pi/2)-theta2)) * Auy
        z = z - np.cos(theta3 - ((np.pi/2)-theta2)) * Auz
        pos = [x,y,z]
        joint_pos.append(pos)
        self.joint_pos = joint_pos
        print(x)
        print(y)
        print(z)

    def compute_inverse(self,x=None,y=None,z=None):        

        dx = x - self.joint_pos[-4][0]
        dy = y - self.joint_pos[-4][1]
        z1 = z - self.joint_pos[-4][2] 

        z1 = z1 * -1

        theta1 = np.arctan2(dy, dx)
        #########
        
        Al=177+30
        theta3=np.radians(self.motor_rotation[2])
        Auu=190
        Au=Auu/(np.sin(np.pi-theta3))
        L_1=self.lengths[5][0]
        #L_1,A_L,A_U = self.lengths[3:]

        L1 = np.sqrt(dx**2 + dy**2) - L_1
        L7 = np.sqrt(L1**2 + z1**2)
        
        A_L2 = Al ** 2 
        A_U2 = Au ** 2
        L72  = L7  ** 2 
        #########
        a = z1 / L7
        b = ( L72  + A_L2 - A_U2 ) / (2 * L7 * Al)
        c = ( A_L2 + A_U2 - L72  ) / (2 * Au * Al)    

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

        self.motor_rotation = [theta_1,theta_2,theta_3]
        self.compute_forward()
        print("new angle")
        print(theta1)
        print(theta2)
        print(theta3)
        print("new position")
