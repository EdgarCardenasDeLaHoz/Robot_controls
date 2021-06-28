import numpy as np
import cv2
from datetime import datetime
import math
import pandas as pd
import glob
import torch 
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.patches import Rectangle
from matplotlib.transforms import Affine2D
import matplotlib.animation as animation
from matplotlib.animation import FuncAnimation
from PIL import Image, ImageDraw, ImageFilter
from skimage import transform
from skimage import data, filters, measure, morphology, feature, color
from skimage.transform import hough_circle, hough_circle_peaks, warp, AffineTransform
from skimage.feature import canny, corner_harris, corner_subpix, corner_peaks
from skimage.draw import circle_perimeter
from skimage.util import img_as_ubyte#, compare_images
from skimage.measure import label, regionprops, regionprops_table
from skimage.data import camera
import skimage.morphology as mor
from scipy import ndimage as ndi
import mpl_toolkits.mplot3d.art3d as art3d
import plotly.express as px
import plotly.graph_objects as go
import mpl_toolkits.mplot3d.axes3d as p3

def take_picture(frame, x = None):
    print('Picture taken')
    now = datetime.now()
    current_time = now.strftime("%H_%M_%S")
    fn_out = "./Test images/Control pictures/" + current_time +"_"+ str(x) + ".jpg"
    cv2.imwrite(fn_out,frame) 
def change_camera(x):
    cap = cv2.VideoCapture(x) 
    print('changed to camera '+str(x))
def check_keys(x, y = None):
    frame = x
    if cv2.waitKey(1)& 0xFF == ord('p'):
        take_picture(frame, y)
    if cv2.waitKey(1)& 0xFF == ord('1'):
        change_camera(1)
def run_camera(x):
    cap = cv2.VideoCapture(x)
    record = 0
    release = 0 
    while(True):
        # Capture frame-by-frame
        ret, frame = cap.read()
        # Our operations on the frame come here
        # Display the resulting frame
        cv2.imshow('Camera image',frame)
        check_keys(frame)
        if cv2.waitKey(1)& 0xFF == ord('r'): 
            if record == 0:
                print('recording')
                now = datetime.now()
                current_time = now.strftime("%H_%M_%S")
                record = 1
                fourcc = cv2.VideoWriter_fourcc(*'XVID')
                fn_out = "./Test videos/" + current_time + ".avi"
                out = cv2.VideoWriter(fn_out,fourcc, 20.0, (640,480))
                release = 1

            else : 
                out.release()
                record = 0
                print('stopped recording')
            
        if record == 1:
            out.write(frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
    # When everything done, release the capture
    cap.release()
    if release == 1:
        out.release()
    cv2.destroyAllWindows()
def run_2cameras(x, y):
    cap1 = cv2.VideoCapture(x)
    cap2 = cv2.VideoCapture(y)
    record = 0
    release = 0 
    while(True):
        # Capture frame-by-frame
        ret1, frame1 = cap1.read()
        ret2, frame2 = cap2.read()
        # Our operations on the frame come here
        # Display the resulting frame
        cv2.imshow('Camera image 1',frame1)
        cv2.imshow('Camera image 2',frame2)
        check_keys(frame1, 1)
        check_keys(frame2, 2)
        if cv2.waitKey(1)& 0xFF == ord('r'): 
            if record == 0:
                print('recording')
                now = datetime.now()
                current_time = now.strftime("%H_%M_%S")
                record = 1
                fourcc = cv2.VideoWriter_fourcc(*'XVID')
                fn_out1 = "./Test videos/Robotarm mouse/" + current_time  + "_1.mp4"
                fn_out2 = "./Test videos/Robotarm mouse/" + current_time  + "_2.mp4"
                out1 = cv2.VideoWriter(fn_out1,fourcc, 20.0, (640,480))
                out2 = cv2.VideoWriter(fn_out2,fourcc, 20.0, (640,480))
                release = 1

            else : 
                out1.release()
                out2.release()
                record = 0
                print('stopped recording')
            
        if record == 1:
            out1.write(frame1)
            out2.write(frame2)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
    # When everything done, release the capture
    cap1.release()
    cap2.release()
    if release == 1:
        out1.release()
        out2.release()

    cv2.destroyAllWindows()
#Detect red object
def red_object(img):
    img = img[...,::-1]
    red = img[...,0] - img[...,[1,2]].mean(axis=2)
    red = red > 73
    plt.imshow(red)

#Detect blue object
def blue_object(img):
    img = img[...,::-1]
    blue = img[...,2] - img[...,[0,1]].mean(axis=2)
    blue = blue > 52     #52 for 2D
    plt.imshow(blue)
    
#Calculate centroid coordinates red object
def coord_centroid_red(img):
    img = img[...,::-1]
    red = img[...,0] - img[...,[1,2]].mean(axis=2)
    red = red > 73
    label_img = label(red)
    regions = regionprops(label_img)
    for props in regions:
        y0, x0 = props.centroid
        print(x0, y0)
    return x0, y0

#Calculate centroid coordinates blue object
def coord_centroid_blue(img):
    img = img[...,::-1]
    blue = img[...,2] - img[...,[0,1]].mean(axis=2)
    blue = blue > 38      #52 for 2D
    label_img = label(blue)
    regions = regionprops(label_img)
    for props in regions:
        y0, x0 = props.centroid
        print(x0, y0)
    return x0, y0
#Show centroids red and blue object
def red_blue(imfn):
    if ".jpg" in imfn:
        image = cv2.imread("./Test images/" + imfn)
        plt.imshow(image)
        imager= image[...,::-1]
        plt.imshow(imager)
        red_pts=coord_centroid_red(image)
        plt.plot(red_pts[0], red_pts[1],"ro")
        blue_pts= coord_centroid_blue(image)
        plt.plot(blue_pts[0], blue_pts[1],"bo")
    else:
        image = imfn
        imager= image[...,::-1]
        plt.imshow(imager)
        red_pts=coord_centroid_red(image)
        plt.plot(red_pts[0], red_pts[1],"ro")
        blue_pts= coord_centroid_blue(image)
        plt.plot(blue_pts[0], blue_pts[1],"bo")
#Pixel coordinates to real coordinates
def pix_to_real(Xp,Yp):
    Ax=0.05554086111917622
    Bx=-16.04448007940368
    Ay=-0.06657232583430062
    By=18.984407162484395
    Xr=Ax*Xp+Bx
    Yr=Ay*Yp+By
    return Xr, Yr
#Real coordinates to pixel coordinates
def real_to_pix(Xr,Yr):
    Ax=0.05554086111917622
    Bx=-16.04448007940368
    Ay=-0.06657232583430062
    By=18.984407162484395
    Xp=(Xr-Bx)/Ax
    Yp=(Yr-By)/Ay
    return Xp, Yp
def base_picture(imfn):
    plt.clf()
    folder = "./Test images/"
    image = im_or_fn(imfn,folder)
    imager= image[...,::-1]
    x0,y0=real_to_pix(0,0)
    plt.imshow(imager)
    red_pts=coord_centroid_red(image)
    plt.plot(red_pts[0], red_pts[1],"ro")
    blue_pts= coord_centroid_blue(image)
    plt.plot(blue_pts[0], blue_pts[1],"bo")
    plt.plot(x0, y0,"go")
#Draw dots
def draw_dots(imfn):
    folder = "./Test images/"
    image = im_or_fn(imfn,folder)
    base_picture(image)
    x_range = []
    for i in range(-16, 17,4):
        x_range.append(i)
    y_range = []
    for i in range(-12, 17,4):
        y_range.append(i)
    for i in range(0, 9):
        x=x_range[i]
        for i in range(0, 8):
            y=y_range[i]
            xd,yd=real_to_pix(x,y)
            plt.plot(xd, yd,"yo")
#Draw lines
def draw_lines(imfn):
    folder = "./Test images/"
    image = im_or_fn(imfn,folder)
    base_picture(image)
    draw_dots(image)
    x_range = []
    for i in range(-16, 17,4):
        x_range.append(i)
    y_range = []
    for i in range(-12, 17,4):
        y_range.append(i)
    for i in range(0, 8):
            y=y_range[i]
            pt1= real_to_pix(-16,y)
            pt2 = real_to_pix(16,y)
            x_val = [pt1[0],pt2[0]]
            y_val = [pt1[1],pt2[1]]
            plt.plot(x_val,y_val,'c')
    for i in range(0, 9):
            x=x_range[i]
            pt1= real_to_pix(x,-12)
            pt2 = real_to_pix(x,16)
            x_val = [pt1[0],pt2[0]]
            y_val = [pt1[1],pt2[1]]
            plt.plot(x_val,y_val,'c')
def corner_detection(filename):
    image = cv2.imread("./Test images/" + filename)
    image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    coords = corner_peaks(corner_harris(image), min_distance=5, threshold_rel=0.02)
    coords_subpix = corner_subpix(image, coords, window_size=13)
    fig, ax = plt.subplots()
    base_picture(filename)
    plt.plot(coords[:, 1], coords[:, 0], color='yellow', marker='o',
            linestyle='None', markersize=6)
    plt.show()
def centroids(imfn1,imfn2):
    plt.clf()
    folder = "./Test images/"
    image = im_or_fn(imfn1,folder)
    imager= image[...,::-1]
    plt.imshow(imager)
    red_pts_1=coord_centroid_red(image)
    plt.plot(red_pts_1[0], red_pts_1[1],"o",c='#f5054f', markersize = 10)
    blue_pts_1= coord_centroid_blue(image)
    plt.plot(blue_pts_1[0], blue_pts_1[1],"o",c='#069af3', markersize = 10)
    fig, ax = plt.subplots()
    image2 = im_or_fn(imfn2,folder)
    imager2= image2[...,::-1]
    ax.imshow(imager2)
    red_pts_2=coord_centroid_red(image2)
    ax.plot(red_pts_2[0], red_pts_2[1],"o",c='#f5054f', markersize = 10)
    blue_pts_2= coord_centroid_blue(image2)
    ax.plot(blue_pts_2[0], blue_pts_2[1],"o",c='#069af3', markersize = 10)
    font = {'family' : 'SimSun',
        'weight' : 'bold',
        'size'   : 20}

    plt.rc('font', **font)
    return red_pts_1, blue_pts_1, red_pts_2, blue_pts_2
def pts_plot_3D(xg,yg,zg,xb,yb,zb):
    fig = plt.figure()

    ax = fig.add_subplot(111, projection='3d')
 

    z_g = zg
    x_g = xg
    y_g = yg

    z_b = zb
    x_b =xb
    y_b = yb

    z_start = 50
    x_start =0
    y_start = 30

    z_c = [43.5,21]
    x_c = [0,6.5]
    y_c = [26,0]

    x =[x_g,x_b]
    y = [y_g,y_b]
    z =[z_g,z_b]

    x_v1g = [x_c[0],x_g]
    y_v1g = [y_c[0],y_g]
    z_v1g = [z_c[0],z_g]

    x_v1b = [x_c[0],x_b]
    y_v1b = [y_c[0],y_b]
    z_v1b = [z_c[0],z_b]

    x_v2g = [x_c[1],x_g]
    y_v2g = [y_c[1],y_g]
    z_v2g = [z_c[1],z_g]

    x_v2b = [x_c[1],x_b]
    y_v2b = [y_c[1],y_b]
    z_v2b = [z_c[1],z_b]

    x_stb = [x_start,x_g]
    y_stb = [y_start,y_g]
    z_stb = [z_start,z_g]

    #ax.scatter(x_c, y_c, z_c, c='y', marker='o')
    ax.scatter(x_g, y_g, z_g, c='#f5054f', marker='o',s=100)
    ax.scatter(x_b, y_b, z_b, c='#069af3', marker='o',s=100)
    ax.scatter(x_start, y_start, z_start, c='lightblue', marker='o',s=100)

    #ax.plot3D(x_v1g,y_v1g,z_v1g,'--', c='lightgray')
    #ax.plot3D(x_v1b,y_v1b,z_v1b,'--',c='lightgray')
    #ax.plot3D(x_v2g,y_v2g,z_v2g,'--',c='lightgray')
    #ax.plot3D(x_v2b,y_v2b,z_v2b,'--',c='lightgray')
    ax.plot3D(x,y,z,c='gray',linewidth=5)
    ax.plot3D(x_stb,y_stb,z_stb,c='gray',linewidth=5) 
    
    #x0 = 0
    #y0 = 0
    #rectangle = plt.Rectangle((x0,y0), 12, 8,ec="gray", fc="none")
    #ax.add_patch(rectangle)
    #art3d.pathpatch_2d_to_3d(rectangle, z=0, zdir="z")
   
    #x = x0+0.34
    #y = y0+0.04
    #for i in range(0, 8):
    #    y = y + 0.89
    #    i = i + 1
    #    x = x0+0.34
    #    for j in range(0,12):
    #        x = x + 0.89
    #        circle = plt.Circle((x,y),0.35,ec="gray", fc="none")
    #        ax.add_patch(circle)
    #        art3d.pathpatch_2d_to_3d(circle, z=0, zdir="z")

    
    ax.set_xlabel('Distance [cm]',fontsize=15)
    ax.set_ylabel('Distance [cm]',fontsize=15)
    #ax.set_zlabel('Distance [cm]',fontsize=12)
    ax.set_xlim3d(0, 50)
    ax.set_ylim3d(0, 50)
    ax.set_zlim3d(0, 50)
    
    #ax.view_init(azim=-95, elev=10)
    #ax.view_init(azim=-180, elev=90)

    #plt.show()
def pts_plot_3D_2(xg,yg,zg,xb,yb,zb,ax,fig):
    #fig = plt.figure()

    #ax = fig.add_subplot(111, projection='3d')
 

    z_g = zg
    x_g = xg
    y_g = yg

    z_b = zb
    x_b =xb
    y_b = yb

    z_start = 50
    x_start =0
    y_start = 30

    z_c = [43.5,21]
    x_c = [0,6.5]
    y_c = [26,0]

    x =[x_g,x_b]
    y = [y_g,y_b]
    z =[z_g,z_b]

    x_v1g = [x_c[0],x_g]
    y_v1g = [y_c[0],y_g]
    z_v1g = [z_c[0],z_g]

    x_v1b = [x_c[0],x_b]
    y_v1b = [y_c[0],y_b]
    z_v1b = [z_c[0],z_b]

    x_v2g = [x_c[1],x_g]
    y_v2g = [y_c[1],y_g]
    z_v2g = [z_c[1],z_g]

    x_v2b = [x_c[1],x_b]
    y_v2b = [y_c[1],y_b]
    z_v2b = [z_c[1],z_b]

    x_stb = [x_start,x_g]
    y_stb = [y_start,y_g]
    z_stb = [z_start,z_g]


    ax.scatter(x_g, y_g, z_g, c='b', marker='o')
    ax.scatter(x_b, y_b, z_b, c='g', marker='o')
    ax.scatter(x_start, y_start, z_start, c='lightblue', marker='o')


    ax.plot3D(x,y,z,c='gray')
    ax.plot3D(x_stb,y_stb,z_stb,c='gray') 
    
    #x0 = 0
    #y0 = 0
    #rectangle = plt.Rectangle((x0,y0), 12, 8,ec="gray", fc="none")
    #ax.add_patch(rectangle)
    #art3d.pathpatch_2d_to_3d(rectangle, z=0, zdir="z")
   
    #x = x0+0.34
    #y = y0+0.04
    #for i in range(0, 8):
    #    y = y + 0.89
    #    i = i + 1
    #    x = x0+0.34
    #    for j in range(0,12):
    #        x = x + 0.89
    #        circle = plt.Circle((x,y),0.35,ec="gray", fc="none")
    #        ax.add_patch(circle)
    #        art3d.pathpatch_2d_to_3d(circle, z=0, zdir="z")

    
    ax.set_xlabel('X Label')
    ax.set_ylabel('Y Label')
    ax.set_zlabel('Z Label')
    ax.set_xlim3d(0, 50)
    ax.set_ylim3d(0, 50)
    ax.set_zlim3d(0, 50)
    
    #ax.view_init(azim=-95, elev=10)
    #ax.view_init(azim=-180, elev=90)

    #plt.show()
def find_plate(folder,imfn):
    #find plate
    fldr = folder
    img = im_or_fn(imfn,fldr)
    bg = img
    cv2.imshow("Original", bg)
    img = img[...,::-1]
    image = img[...,2] - img[...,[1,0]].mean(axis=2)
    image = image > 6
    img = image
    img = cv2.cvtColor(np.float32(img), cv2.COLOR_RGB2BGR)
    img=np.array(img*255).astype('uint8')
    img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    ret,thresh = cv2.threshold(img,50,140,0)
    contours,hierarchy = cv2.findContours(thresh, 1, 2)
    #Nog automatisch de grootste rechthoek vinden en tekenen
    #cnt = contours[len(contours)-1]
    #cnt = contours[177]
    length = len(contours)
    keep = 0
    for i in range(0,length):
        area = cv2.contourArea(contours[i])
        if area > keep:
            keep = area
            x = i
    cnt = contours[x]
    rect = cv2.minAreaRect(cnt)
    box = cv2.boxPoints(rect)
    box = np.int0(box)
    im = cv2.drawContours(img,[box],0,(255,255,255),3)
    cv2.imshow('plate',im)

    img = im_or_fn(imfn,fldr)
    img = img[...,::-1]
    x = [box[0,0],box[1,0],box[2,0],box[3,0]]
    y = [box[0,1],box[1,1],box[2,1],box[3,1]]
    print(x)
    print(y)
    plt.imshow(img)
    plt.plot(x,y,'ro')
    def connectpoints(x,y,p1,p2):
        x1, x2 = x[p1], x[p2]
        y1, y2 = y[p1], y[p2]
        plt.plot([x1, x2], [y1, y2], 'k-',linewidth=3)
    connectpoints(x,y,0,1)
    connectpoints(x,y,2,1)
    connectpoints(x,y,2,3)
    connectpoints(x,y,3,0)
    plt.show
    
    # read image to be processed
    img = cv2.imread("./Test images/plate.jpg")
    hh, ww = img.shape[:2]

    # read background image
    bck = bg
    hhh, www = bck.shape[:2]

    # specify coordinates for corners of img in order TL, TR, BR, BL as x,y pairs
    img_pts = np.float32([[0,0], [ww-1,0], [ww-1,hh-1], [0,hh-1]])

    # manually pick coordinates of corners of rectangle in background image
    bck_pts = np.float32([[x[1],y[1]], [x[2],y[2]], [x[3],y[3]], [x[0],y[0]]])

    # compute perspective matrix
    matrix = cv2.getPerspectiveTransform(img_pts,bck_pts)
    #print(matrix)

    # change black and near-black to graylevel 1 in each channel so that no values 
    # inside panda image will be black in the subsequent mask
    img[np.where((img<=[5,5,5]).all(axis=2))] = [1,1,1]

    # do perspective transformation setting area outside input to black
    img_warped = cv2.warpPerspective(img, matrix, (www,hhh), cv2.INTER_LINEAR, borderMode=cv2.BORDER_CONSTANT, borderValue=(0,0,0))

    # make mask for area outside the warped region
    # (black in image stays black and rest becomes white)
    mask = cv2.cvtColor(img_warped, cv2.COLOR_BGR2GRAY)
    mask = cv2.threshold(mask, 0, 255, cv2.THRESH_BINARY)[1]
    mask = cv2.merge([mask,mask,mask])
    mask_inv = 255 - mask

    # use mask to blend between img_warped and bck
    result = ( 255 * (bck * mask_inv + img_warped * mask) ).clip(0, 255).astype(np.uint8)

    cv2.imshow("result", result)
    cv2.waitKey(0)
    cv2.destroyAllWindows()
def plate(x0,y0):
    
    rectangle = plt.Rectangle((x0,y0), 12, 8,ec="gray", fc="lightgray")
    plt.gca().add_patch(rectangle)
    
    plt.axis('scaled')
    x = x0+0.34
    y = y0+0.04
    for i in range(0, 8):
        y = y + 0.89
        i = i + 1
        x = x0+0.35
        for j in range(0,12):
            x = x + 0.89
            circle = plt.Circle((x,y),0.35,ec="gray", fc="none")
            plt.gca().add_patch(circle)
    plt.axis('scaled')
    plt.show()
def pipet(imfn):
    #Ruler
    folder = "./Pipettes/"
    image = im_or_fn(imfn,folder)
    scale_percent = 20 # percent of original size
    width = int(image.shape[1] * scale_percent / 100)
    height = int(image.shape[0] * scale_percent / 100)
    dim = (width, height)
    #Resize image
    img = cv2.resize(image, dim)
    res = img 
    #cv2.imshow('resized', img)
    #Process image 
    img = img[...,::-1]
    ruler = img[...,0] - img[...,[1,2]].mean(axis=2)
    ruler = ruler > 23
    #plt.imshow(ruler)
    img = ruler
    img = cv2.cvtColor(np.float32(img), cv2.COLOR_RGB2BGR)
    img=np.array(img*255).astype('uint8')
    img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    ret,thresh = cv2.threshold(img,50,140,0)
    contours,hierarchy = cv2.findContours(thresh, 1, 2)
    length = len(contours)
    keep = 0
    for i in range(0,length):
        area = cv2.contourArea(contours[i])
        if area > keep:
            keep = area
            x = i
    cnt = contours[x]
    epsilon = 0.01*cv2.arcLength(cnt,True)
    approx = cv2.approxPolyDP(cnt,epsilon,True)
    #Scale 
    x1 = approx[0,0][0]
    x2 = approx[3,0][0]
    y1 = approx[0,0][1]
    y2 = approx[3,0][1]
    dis1 = result= ((((x2 - x1 )**2) + ((y2-y1)**2) )**0.5)
    sc1 = 21/dis1
    x1 = approx[1,0][0]
    x2 = approx[2,0][0]
    y1 = approx[1,0][1]
    y2 = approx[2,0][1]
    dis2 = result= ((((x2 - x1 )**2) + ((y2-y1)**2) )**0.5)
    sc2 = 25/dis2
    scale = (sc1+sc2)/2

    #Draw contour
    im = cv2.drawContours(res,[approx],0,(0,255,0),2)
    #cv2.imshow('ruler',im)

    #Pipettes
    image = im_or_fn(imfn,folder)
    scale_percent = 20 # percent of original size
    width = int(image.shape[1] * scale_percent / 100)
    height = int(image.shape[0] * scale_percent / 100)
    dim = (width, height)
    #Resize image
    img = cv2.resize(image, dim)
    res = img 
    #cv2.imshow('resized', img)
    #Process image 
    img = img[...,::-1]
    pipet = img[...,2] - img[...,[0,1]].mean(axis=2)
    pipet = pipet > -6
    #plt.imshow(pipet)
    img = pipet
    img = cv2.cvtColor(np.float32(img), cv2.COLOR_RGB2BGR)
    img=np.array(img*255).astype('uint8')
    img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    ret,thresh = cv2.threshold(img,50,140,0)
    contours,hierarchy = cv2.findContours(thresh, 1, 2)
    length = len(contours)
    keep = 0
    good = 0
    e = 0
    for i in range(0,length):
        area = cv2.contourArea(contours[i])
        if area > keep:
            j = e
            good = keep
            keep = area
            e = i
    cnt = contours[j]
    length  = len(cnt)
    xref = 100
    while True:
        for i in range(0,length):
            x = cnt[i,0][0]
            if x < xref:
                cnt = contours[j]
                break 
            else:
                cnt = contours[e]
        break 
    epsilon = 0.002*cv2.arcLength(cnt,True)
    approx = cv2.approxPolyDP(cnt,epsilon,True)
    perimeter = cv2.arcLength(approx,True)
    realperimeter = scale*perimeter
    realperimeter = round(realperimeter, 2)
    print('Perimeter is',realperimeter,'cm')
    im = cv2.drawContours(res,[approx],0,(0,255,0),2)
    cv2.imshow('pipet',im)

def grey(indir, outdir):
    Input_dir = indir #'Test images/Duo_camera_images/'
    out_dir = outdir #'greyscale/'
    a = os.listdir(Input_dir)

    for i in a:
        print(i)
        I = Image.open(Input_dir+i)
        L = I.convert('L')
        L.save(out_dir+i)
def evaluate_image(model, im_rgb):
    sz_in  = np.array(im_rgb.shape[0:2])[::-1]
    sz_out  = np.array(im_rgb.shape[0:2])[::-1]* 0.5
    sz_out = (np.floor(sz_out/8)*8).astype(np.int)

    im_in = cv2.resize(im_rgb, tuple(sz_out))/255
    im_in = np.transpose(im_in,[2,0,1])
    im_in = torch.tensor([im_in]).float()

    predict = model(im_in).detach().numpy() 
    predict = np.transpose(predict[0],[1,2,0])     
    predict = cv2.resize(predict, tuple(sz_in))       
    return predict

def bi_close(bI,radius,down_sample=0.2):
    
    im_size = np.array( bI.shape )
    d_size = (im_size*down_sample).astype(np.int)

    im_size = tuple(im_size)
    d_size = tuple(d_size)
    #print(d_size)
    filt = cv2.resize(1.*(bI), d_size[::-1]) > 0.1

    sel = mor.disk(radius, dtype=np.bool)
    filt = mor.binary_closing(filt, selem=sel)
    bI_out = cv2.resize(1.*(filt), im_size[::-1])> 0.1

    return bI_out

def area_filter(ar, min_size=0, max_size=None):
    """
    """
    if ar.dtype == bool:
        ccs,l_max = ndi.label(ar)
    else:
        ccs = ar
        l_max = ar.max()

    component_sizes = np.bincount(ccs[ccs>0])
    #print(component_sizes)
    idxs = np.arange(l_max+1).astype(np.uint16)
    if min_size>0:
        too_small = component_sizes < min_size
        idxs[too_small]=0

    if max_size is not None:
        too_large = component_sizes > max_size
        idxs[too_large]=0

    out = np.zeros_like(ccs, np.uint16)
    _, idxs2 = np.unique(idxs,return_inverse=True)
    out[ccs>0] = idxs2[ccs[ccs>0]]

    return out

def detect_robot(model,img):
    #plt.close(2)
    #plt.figure(2) 
    x0 = None
    x1 = None
    x2 = None
    I = img[:,:,::-1]/255
    #cv2.imshow('img',img)
    pred1 = evaluate_image(model, img[:,:,::-1])
    n = pred1.shape[2]
    #print(n)
    #fig, ax = plt.subplots()
    for i in range(n):
        pred = pred1[:,:,i]
        #cv2.imshow('predict'+str(i), pred)
        #cv2.imwrite('predict'+str(i)+'.jpg',pred)
        bI = pred>0.6
        bI = bi_close(bI,5,down_sample=0.4)

        #bI = mor.remove_small_objects(bI,10)
        label_image = area_filter(bI, min_size=10, max_size=10000)
        if np.sum(label_image) == 0:
            topY = np.nan
            midX = np.nan

        else: 
        ## Getting the mean value  
            #for region in regionprops(label_image):
            region = regionprops(label_image)[0]
            minr, minc, maxr, maxc = region.bbox
            midX = (minc+maxc)/2
            topY = (minr+maxr)/2
            regions = regionprops(label_image)
            for props in regions:
                y, x = props.centroid
            #plt.imshow(I)
            if i == 0:
                x0 = x
                y0 = y
                #plt.plot(x, y,"o",c='#f5054f',markersize = 10)
            elif i == 1:
                x1 = x
                y1 = y
                #plt.plot(x, y,"o",c='#9acd32',markersize = 10)
            else :
                x2 = x
                y2 = y
                #plt.plot(x, y,"o",c='#069af3',markersize = 10)
    if x0 == None:
        x0 = 0
        y0 = 0
    if x1 == None:
        x1 = 0
        y1 = 0
    if x2 == None:
        x2 = 0
        y2 = 0
            #bx = (minc, maxc, maxc, minc, minc)
            #by = (minr, minr, maxr, maxr, minr)
            #ax.plot(bx, by, '-b', linewidth=2.5)
    coord_red = x0, y0
    coord_gr = x1, y1
    coord_bl = x2, y2
    return coord_red, coord_gr, coord_bl

def recon_3D(model, imside, imtop):    
    filename_top = imtop #"10.jpg"
    #imtop = cv2.imread("./" + folder + "/" + filename_top)
    filename_side = imside #"10B.jpg"
    #imside = cv2.imread("./" + folder + "/" + filename_side)
    pts_top = detect_robot(model,imtop)
    pts_side = detect_robot(model,imside)
    


    xg,yg,zg,xb,yb,zb = find_3D_pts(pts_side,pts_top)

    #pts_plot_3D(xg,yg,zg,xb,yb,zb)
    xg,yg,zg = xg*10,yg*10,zg*10
    return xg,yg,zg
def im_or_fn(imfn, folder = None):
    if ".jpg" in imfn :
        if folder is None:
            print("Specify folder: im_or_fn(filename, folder), or give image as input: im_or_fn(image)")
        else:
            img = cv2.imread("./"+ folder + "/" + imfn)
            return img
    else : 
        img = imfn
        return img
def float_to_int(p):
    x = p[0]
    y = p[1]
    x = int(round(x))
    y = int(round(y))
    center_coordinates = (x,y)
    return center_coordinates
def det_rob_vid(folder,fn,model):
    cap = cv2.VideoCapture("./" + folder + "/" + fn)
    blue = (255, 0, 0)
    green = (0, 255, 0)
    red = (0, 0, 255)
    while(cap.isOpened()):
        ret, frame = cap.read()
        crds = detect_robot(model, frame)
        cntr_crds_red = float_to_int(crds[0])
        cntr_crds_green = float_to_int(crds[1])
        cntr_crds_blue = float_to_int(crds[2])
        frame = cv2.circle(frame, cntr_crds_red, 3, red, 5)
        frame = cv2.circle(frame, cntr_crds_green, 3, green, 5)
        frame = cv2.circle(frame, cntr_crds_blue, 3, blue, 5)
        cv2.imshow('frame',frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()
def det_rob_2vid(folder,fn,fn1,model):
    cap = cv2.VideoCapture("./" + folder + "/" + fn)
    cap1 = cv2.VideoCapture("./" + folder + "/" + fn1)
    blue = (255, 0, 0)
    green = (0, 255, 0)
    red = (0, 0, 255)
    while(cap.isOpened()):
        ret, frame = cap.read()
        ret1, frame1 = cap1.read()
        crds = detect_robot(model, frame)
        crds1 = detect_robot(model, frame1)
        cntr_crds_red = float_to_int(crds[0])
        cntr_crds_green = float_to_int(crds[1])
        cntr_crds_blue = float_to_int(crds[2])
        cntr_crds_red1 = float_to_int(crds1[0])
        cntr_crds_green1 = float_to_int(crds1[1])
        cntr_crds_blue1 = float_to_int(crds1[2])
        frame = cv2.circle(frame, cntr_crds_red, 3, red, 5)
        frame = cv2.circle(frame, cntr_crds_green, 3, green, 5)
        frame = cv2.circle(frame, cntr_crds_blue, 3, blue, 5)
        frame1 = cv2.circle(frame1, cntr_crds_red1, 3, red, 5)
        frame1 = cv2.circle(frame1, cntr_crds_green1, 3, green, 5)
        frame1 = cv2.circle(frame1, cntr_crds_blue1, 3, blue, 5)
        final = cv2.hconcat([frame, frame1])
        cv2.imshow("Images", final)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()
def det_rob_2vid_faster(folder,fn,fn1,model):
    cap = cv2.VideoCapture("./" + folder + "/" + fn)
    cap1 = cv2.VideoCapture("./" + folder + "/" + fn1)
    blue = (255, 0, 0)
    green = (0, 255, 0)
    red = (0, 0, 255)
    i = 0
    now = datetime.now()
    current_time = now.strftime("%H_%M_%S")
    fourcc = cv2.VideoWriter_fourcc(*'XVID')
    fn_out1 = "./Test videos/Robotarm mouse/" + current_time  + "_1.mp4"
    out1 = cv2.VideoWriter(fn_out1,fourcc, 20.0, (1280,480))
    while(cap.isOpened()):
        ret, frame = cap.read()
        ret1, frame1 = cap1.read()
        if i % 1 == 0:
            crds = detect_robot(model, frame)
            crds1 = detect_robot(model, frame1)
            cntr_crds_red = float_to_int(crds[0])
            cntr_crds_green = float_to_int(crds[1])
            cntr_crds_blue = float_to_int(crds[2])
            cntr_crds_red1 = float_to_int(crds1[0])
            cntr_crds_green1 = float_to_int(crds1[1])
            cntr_crds_blue1 = float_to_int(crds1[2])
            frame = cv2.circle(frame, cntr_crds_red, 3, red, 5)
            frame = cv2.circle(frame, cntr_crds_green, 3, green, 5)
            frame = cv2.circle(frame, cntr_crds_blue, 3, blue, 5)
            frame1 = cv2.circle(frame1, cntr_crds_red1, 3, red, 5)
            frame1 = cv2.circle(frame1, cntr_crds_green1, 3, green, 5)
            frame1 = cv2.circle(frame1, cntr_crds_blue1, 3, blue, 5)
            i = i + 1
        else : 
            frame = cv2.circle(frame, cntr_crds_red, 3, red, 5)
            frame = cv2.circle(frame, cntr_crds_green, 3, green, 5)
            frame = cv2.circle(frame, cntr_crds_blue, 3, blue, 5)
            frame1 = cv2.circle(frame1, cntr_crds_red1, 3, red, 5)
            frame1 = cv2.circle(frame1, cntr_crds_green1, 3, green, 5)
            frame1 = cv2.circle(frame1, cntr_crds_blue1, 3, blue, 5)
            
            i = i + 1
        final = cv2.hconcat([frame, frame1])
        out1.write(final)
        cv2.imshow("Images", final)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
    out1.release()
    cap.release()
    cv2.destroyAllWindows()
def det_rob_2cam(cam1,cam2,model):
    cap = cv2.VideoCapture(cam1)
    cap1 = cv2.VideoCapture(cam2)
    blue = (255, 0, 0)
    green = (0, 255, 0)
    red = (0, 0, 255)
    while(cap.isOpened()):
        ret, frame = cap.read()
        ret1, frame1 = cap1.read()
        crds = detect_robot(model, frame)
        crds1 = detect_robot(model, frame1)
        cntr_crds_red = float_to_int(crds[0])
        cntr_crds_green = float_to_int(crds[1])
        cntr_crds_blue = float_to_int(crds[2])
        cntr_crds_red1 = float_to_int(crds1[0])
        cntr_crds_green1 = float_to_int(crds1[1])
        cntr_crds_blue1 = float_to_int(crds1[2])
        frame = cv2.circle(frame, cntr_crds_red, 3, red, 5)
        frame = cv2.circle(frame, cntr_crds_green, 3, green, 5)
        frame = cv2.circle(frame, cntr_crds_blue, 3, blue, 5)
        frame1 = cv2.circle(frame1, cntr_crds_red1, 3, red, 5)
        frame1 = cv2.circle(frame1, cntr_crds_green1, 3, green, 5)
        frame1 = cv2.circle(frame1, cntr_crds_blue1, 3, blue, 5)
        final = cv2.hconcat([frame, frame1])
        cv2.imshow("Images", final)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
def find_3D_pts(pts_side,pts_top):
    green_pts_1 = pts_side[1]
    blue_pts_1 = pts_side[2]
    green_pts_2 = pts_top[1]
    blue_pts_2 = pts_side[2]

    r_green_pts_1 = pix_to_real(green_pts_1[0],green_pts_1[1])
    r_blue_pts_1 = pix_to_real(blue_pts_1[0],blue_pts_1[1])
    r_green_pts_2 = pix_to_real(green_pts_2[0],green_pts_2[1])
    r_blue_pts_2 = pix_to_real(blue_pts_2[0],blue_pts_2[1])

    Dxg = 320 - blue_pts_2[0]
    Dxb = 320 - green_pts_2[0]
    yg = 26 + 0.0545*Dxg
    yb = 26 + 0.0545*Dxb

    Dyg = 480 - blue_pts_2[1]
    Dyb = 480 - green_pts_2[1]
    xg = 0.0638*Dyg + 20
    xb = 0.0638*Dyb

    Dzg = 480 - blue_pts_1[1]
    Dzb = 480 - green_pts_1[1]
    zg = 0.0426*Dzg
    zb = 0.0426*Dzb
    return xb,yb,zb,xg,yg,zg
def find_3D_pts_single(pts_side,pts_top):
    green_pts_1 = pts_side
    green_pts_2 = pts_top

    r_green_pts_1 = pix_to_real(green_pts_1[0],green_pts_1[1])
    r_green_pts_2 = pix_to_real(green_pts_2[0],green_pts_2[1])

    Dxg = 320 - green_pts_2[0]
    yg = 26 + 0.0545*Dxg

    Dyg = 480 - green_pts_2[1]
    xg = 0.0638*Dyg + 20

    Dzg = 480 - green_pts_1[1]
    zg = 0.0426*Dzg

    return xg,yg,zg
def grab_frame(cap):
    ret,frame = cap.read()
    return cv2.cvtColor(frame,cv2.COLOR_BGR2RGB)
def detect_mouse(img,model):
    I = img[:,:,::-1]/255
    pred1 = evaluate_image(model, img[:,:,::-1])
    n = 1
    for i in range(n):
        pred = pred1[:,:,i]
        #cv2.imshow('predict'+str(i), pred)
        bI = pred>0.6
        bI = bi_close(bI,5,down_sample=0.4)

        label_image = area_filter(bI, min_size=10, max_size=100000)
        if np.sum(label_image) == 0:
            topY = np.nan
            midX = np.nan
            print("np.sum is 0")

        else: 
            region = regionprops(label_image)[0]
            minr, minc, maxr, maxc = region.bbox
            midX = (minc+maxc)/2
            topY = (minr+maxr)/2
            regions = regionprops(label_image)

            fig, ax = plt.subplots()
            ax.imshow(I, cmap=plt.cm.gray)

            for props in regions:
                y0, x0 = props.centroid

                ax.plot(x0, y0, ".",c='#9acd32', markersize=15)

                minr, minc, maxr, maxc = props.bbox
                bx = (minc, maxc, maxc, minc, minc)
                by = (minr, minr, maxr, maxr, minr)
                ax.plot(bx, by, '-',c='#069af3', linewidth=2.5)

            plt.show()
def detect_mouse_prop(img,model):
    #cv2.imshow('im',img)
    I = img[:,:,::-1]/255
    pred1 = evaluate_image(model, img[:,:,::-1])
    n = 1
    x0= 0
    y0= 0
    minr, minc, maxr, maxc = 0,0,0,0
    for i in range(n):
        pred = pred1[:,:,i]
        bI = pred>0.6
        bI = bi_close(bI,5,down_sample=0.4)

        label_image = area_filter(bI, min_size=10, max_size=100000)
        if np.sum(label_image) == 0:
            topY = np.nan
            midX = np.nan

        else: 
            region = regionprops(label_image)[0]
            minr, minc, maxr, maxc = region.bbox
            midX = (minc+maxc)/2
            topY = (minr+maxr)/2
            regions = regionprops(label_image)

            

            for props in regions:
                y0, x0 = props.centroid

                

                minr, minc, maxr, maxc = props.bbox


    crds_cent = x0,y0
    bx = maxc,minr
    by = minc, maxr
    return crds_cent,bx,by
def just_a_test():
    from matplotlib.animation import FuncAnimation

    def grab_frame(cap):
        ret,frame = cap.read()
        return cv2.cvtColor(frame,cv2.COLOR_BGR2RGB)

    folder = 'Test videos'
    fn = "1.avi"
    fn2 = "1B.avi"
    cap1 = cv2.VideoCapture("./" + folder + "/" + fn)
    cap2 = cv2.VideoCapture("./" + folder + "/" + fn2)
    #Initiate the two cameras
    #cap1 = cv2.VideoCapture(0)
    #cap2 = cv2.VideoCapture(1)

    #create two subplots
    ax1 = plt.subplot(1,2,1)
    ax2 = plt.subplot(1,2,2)

    #create two image plots
    im1 = ax1.imshow(grab_frame(cap1))
    im2 = ax2.imshow(grab_frame(cap2))

    def grab_detection(cap):
        det = detect_robot(model,grab_frame(cap))
        return det
    plot = 0
    def update(i, xx = None):
        im1.set_data(grab_frame(cap1))
        im2.set_data(grab_frame(cap2))
        if xx is None:
            x,y = detect_robot(model, grab_frame(cap1))[0]
            xx = ax1.plot(x, y,"ro")
        else : 
            x,y = detect_robot(model, grab_frame(cap1))[0]
            xx[0].remove()
            xx = ax1.plot(x, y,"ro")

    ani = FuncAnimation(plt.gcf(), update, interval=1)
    plt.show()         
def detect_mouse_2im(NI,model):
    folder = 'Test images/Robotarm mouse'
    fn1 = str(NI) + ".jpg"
    fn2 = str(NI) + "B.jpg"
    img1 = cv2.imread("./" + folder + "/" + fn1)
    img2 = cv2.imread("./" + folder + "/" + fn2)
    detect_mouse(img1,model)
    detect_mouse(img2,model)
def det_mouse_2vid(folder,fn,fn1,model):
    cap = cv2.VideoCapture("./" + folder + "/" + fn)
    cap1 = cv2.VideoCapture("./" + folder + "/" + fn1)
    blue = (255, 0, 0)
    green = (0, 255, 0)
    red = (0, 0, 255)
    while(cap.isOpened()):
        ret, frame = cap.read()
        ret1, frame1 = cap1.read()
        crds = detect_mouse_prop(frame,model)
        crds1 = detect_mouse_prop(frame1,model)
        cntr_crds = float_to_int(crds[0])
        start_crds = float_to_int(crds[1])
        end_crds = float_to_int(crds[2])
        cntr_crds1 = float_to_int(crds1[0])
        start_crds1 = float_to_int(crds1[1])
        end_crds1 = float_to_int(crds1[2])
        frame = cv2.circle(frame, cntr_crds, 3, red, 5)
        frame = cv2.rectangle(frame, start_crds, end_crds, green, 5)
        frame1 = cv2.circle(frame1, cntr_crds1, 3, red, 5)
        frame1 = cv2.rectangle(frame1, start_crds1, end_crds1, green, 5)
        final = cv2.hconcat([frame, frame1])
        cv2.imshow("Images", final)
        xy_side = cntr_crds
        xy_top = cntr_crds1
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
        #return  xy_side, xy_top
def det_mouse_2cam(cam1,cam2,model):
    cap = cv2.VideoCapture(cam1)
    cap1 = cv2.VideoCapture(cam2)
    blue = (255, 0, 0)
    green = (0, 255, 0)
    red = (0, 0, 255)
    #now = datetime.now()
    #current_time = now.strftime("%H_%M_%S")
    #fourcc = cv2.VideoWriter_fourcc(*'XVID')
    #fn_out1 = "./Test videos/Robotarm mouse/" + current_time  + "_1.mp4"
    #out1 = cv2.VideoWriter(fn_out1,fourcc, 20.0, (640,480))
    while(cap.isOpened()):
        ret, frame = cap.read()
        ret1, frame1 = cap1.read()
        crds = detect_mouse_prop(frame,model)
        crds1 = detect_mouse_prop(frame1,model)
        cntr_crds = float_to_int(crds[0])
        start_crds = float_to_int(crds[1])
        end_crds = float_to_int(crds[2])
        cntr_crds1 = float_to_int(crds1[0])
        start_crds1 = float_to_int(crds1[1])
        end_crds1 = float_to_int(crds1[2])
        frame = cv2.circle(frame, cntr_crds, 3, red, 5)
        frame = cv2.rectangle(frame, start_crds, end_crds, green, 5)
        frame1 = cv2.circle(frame1, cntr_crds1, 3, red, 5)
        frame1 = cv2.rectangle(frame1, start_crds1, end_crds1, green, 5)
        #out1.write(frame)
        final = cv2.hconcat([frame, frame1])
        cv2.imshow("Images", final)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
            #out1.release()
def video_3D_plot(folder, sideview, topview,model,record) :
    #recording --> record = 1, not recording --> record = 0
    fn = sideview
    fn2 = topview
    cap1 = cv2.VideoCapture("./" + folder + "/" + fn)
    cap2 = cv2.VideoCapture("./" + folder + "/" + fn2)
    fig = plt.figure()
    ax = fig.add_subplot(111, projection='3d')
    imtop = grab_frame(cap1)
    imside = grab_frame(cap2)

    pts_side = detect_robot(model,imside)
    pts_top = detect_robot(model,imtop)

    xg,yg,zg,xb,yb,zb = find_3D_pts(pts_side,pts_top)

    xx = pts_plot_3D_2(xg,yg,zg,xb,yb,zb,ax,fig)
    def update(i, xx = None):
        imtop = grab_frame(cap1)
        imside = grab_frame(cap2)
        
        pts_side = detect_robot(model,imside)
        pts_top = detect_robot(model,imtop)

        xb,yb,zb,xg,yg,zg = find_3D_pts(pts_side,pts_top)
        ax.clear()
        xx = pts_plot_3D_2(xb,yb,zb,xg,yg,zg,ax,fig)
        
    ani = FuncAnimation(plt.gcf(), update, interval=200)
    plt.show()
    if record == 1 :
        writervideo = animation.FFMpegWriter(fps=5) 
        now = datetime.now()
        current_time = now.strftime("%H_%M_%S")
        fn_out1 = "./Test videos/3D_animations/" + current_time  + ".mp4"
        ani.save(fn_out1 , writer=writervideo)
def det_to_input(x_det,y_det,z_det):
    x = y_det
    y = 400 - x_det
    z = z_det
    return x, y, z
def detect_hand(img,model):
    I = img[:,:,::-1]/255
    pred1 = evaluate_image(model, img[:,:,::-1])
    n =1
    for i in range(n):
        pred = pred1[:,:,i]
        #cv2.imshow('predict'+str(i), pred)
        bI = pred>0.6
        bI = bi_close(bI,5,down_sample=0.4)

        label_image = area_filter(bI, min_size=10, max_size=100000)
        if np.sum(label_image) == 0:
            topY = np.nan
            midX = np.nan
            print("np.sum is 0")

        else: 
            region = regionprops(label_image)[0]
            minr, minc, maxr, maxc = region.bbox
            midX = (minc+maxc)/2
            topY = (minr+maxr)/2
            regions = regionprops(label_image)

            #fig, ax = plt.subplots()
            #ax.imshow(I, cmap=plt.cm.gray)

            for props in regions:
                y0, x0 = props.centroid
                #ax.text(x0, y0, "HAND", fontsize=12, color = 'red')
                #ax.plot(x0, y0, ".",c='#9acd32', markersize=15)
                minr, minc, maxr, maxc = props.bbox
                bx = (minc, maxc, maxc, minc, minc)
                by = (minr, minr, maxr, maxr, minr)
                #ax.plot(bx, by, '-',c='red', linewidth=2.5)
    bx = maxc,minr
    by = minc, maxr
    crds_cent = x0,y0
            #plt.show()
    return bx,by,crds_cent
def det_rob_2camh(cam1,cam2,model,hmodel):
    cap = cv2.VideoCapture(cam1)
    cap1 = cv2.VideoCapture(cam2)
    blue = (255, 0, 0)
    green = (0, 255, 0)
    red = (0, 0, 255)
    gray = (128,128,128)
    now = datetime.now()
    current_time = now.strftime("%H_%M_%S")
    fourcc = cv2.VideoWriter_fourcc(*'XVID')
    fn_out1 = "./Test videos/Robotarm mouse/" + current_time  + "_1.mp4"
    out1 = cv2.VideoWriter(fn_out1,fourcc, 20.0, (1280,480))
    while(cap.isOpened()):
        ret, frame = cap.read()
        ret1, frame1 = cap1.read()
        hcrds = detect_hand(frame1,hmodel)
        start_crds = float_to_int(hcrds[0])
        end_crds = float_to_int(hcrds[1])
        cntr_crds = float_to_int(hcrds[2])
        crds = detect_robot(model, frame)
        crds1 = detect_robot(model, frame1)
        cntr_crds_red = float_to_int(crds[0])
        cntr_crds_green = float_to_int(crds[1])
        cntr_crds_blue = float_to_int(crds[2])
        cntr_crds_red1 = float_to_int(crds1[0])
        cntr_crds_green1 = float_to_int(crds1[1])
        cntr_crds_blue1 = float_to_int(crds1[2])
        frame = cv2.line(frame, cntr_crds_blue, cntr_crds_green, gray, 3)
        frame = cv2.line(frame, cntr_crds_green, cntr_crds_red, gray, 3)
        frame = cv2.circle(frame, cntr_crds_red, 3, red, 5)
        frame = cv2.circle(frame, cntr_crds_green, 3, green, 5)
        frame = cv2.circle(frame, cntr_crds_blue, 3, blue, 5)
        
        frame1 = cv2.circle(frame1, cntr_crds_red1, 3, red, 5)
        frame1 = cv2.circle(frame1, cntr_crds_green1, 3, green, 5)
        
        #frame1 = cv2.circle(frame1, cntr_crds_blue1, 3, blue, 5)
        frame1 = cv2.rectangle(frame1, start_crds, end_crds, red, 5)
        frame1 = cv2.putText(frame1,"HAND", cntr_crds, cv2.FONT_HERSHEY_SIMPLEX, 1, red)
        final = cv2.hconcat([frame, frame1])
        out1.write(final)
        cv2.imshow("Images", final)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
    out1.release()
    cap.release()
    cv2.destroyAllWindows()

    