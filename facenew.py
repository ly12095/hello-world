#!/opt/python3.6/bin/python3.6
# -*- coding: utf-8 -*- 
from pynq import Overlay
from pynq.lib.usb_wifi import Usb_Wifi
from pynq.overlays.base import BaseOverlay
from pynq.lib.video import *
import numpy as np
import requests
import urllib
import urllib.request
import json
import base64
import cv2
import time
import threading
import os
import ctypes
import inspect

base = BaseOverlay("base.bit")

hdmix=1280
hdmiy=720
Mode = VideoMode(hdmix,hdmiy,24)
hdmi_out = base.video.hdmi_out
hdmi_out.configure(Mode,PIXEL_BGR)
hdmi_out.start()

frame_in_w = 640
frame_in_h = 480


port = Usb_Wifi()
ssid = "seu-wlan-6G"
pwd = "T5A201233"
ad=[]

port.connect(ssid, pwd)

place=[[int(70/800*hdmix),int(80/600*hdmiy)],[int(270/800*hdmix),int(80/600*hdmiy)],[int(70/800*hdmix),int(275/600*hdmiy)],
       [int(270/800*hdmix),int(275/600*hdmiy)],[int(600/800*hdmix),int(70/600*hdmiy)]]

p_lt=[[int(19/1280*hdmix),int(8/720*hdmiy)],[int(335/1280*hdmix),int(8/720*hdmiy)],[int(335/1280*hdmix),int(173/720*hdmiy)],
      [int(335/1280*hdmix),int(337/720*hdmiy)],[int(335/1280*hdmix),int(378/720*hdmiy)],[int(335/1280*hdmix),int(419/720*hdmiy)],
     [int(335/1280*hdmix),int(460/720*hdmiy)],[int(565/1280*hdmix),int(8/720*hdmiy)],[int(565/1280*hdmix),int(307/720*hdmiy)],
     [int(773/1280*hdmix),int(8/720*hdmiy)],[int(1019/1280*hdmix),int(8/720*hdmiy)],[int(773/1280*hdmix),int(254/720*hdmiy)],
     [int(1019/1280*hdmix),int(254/720*hdmiy)]]

p_rb=[[int(326/1280*hdmix),int(496/720*hdmiy)],[int(561/1280*hdmix),int(167/720*hdmiy)],[int(561/1280*hdmix),int(331/720*hdmiy)],
     [int(561/1280*hdmix),int(375/720*hdmiy)],[int(561/1280*hdmix),int(416/720*hdmiy)],[int(561/1280*hdmix),int(457/720*hdmiy)],
     [int(561/1280*hdmix),int(498/720*hdmiy)],[int(768/1280*hdmix),int(298/720*hdmiy)],[int(769/1280*hdmix),int(466/720*hdmiy)],
     [int(1015/1280*hdmix),int(250/720*hdmiy)],[int(1261/1280*hdmix),int(250/720*hdmiy)],[int(1015/1280*hdmix),int(495/720*hdmiy)],
     [int(1261/1280*hdmix),int(495/720*hdmiy)]]

place_pic=[]

post_path="/home/xilinx/picture/Mode2/Post/gg"

post_list=[]
post_num=25

post_imp=[]
post_queue=[]
post_place=[]
place_post=[-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1]
place_using=[0,0,0,0,0,0,0,0,0,0,0,0,0]

apiURL = "https://aip.baidubce.com/rest/2.0/face/v3/detect"
accesstokenURL = "https://aip.baidubce.com/oauth/2.0/token"
 
apikey = "Kwqb5ACzYMzreGmzO5RUYG8U"
secretkey = "GQ2wdfndGcp2qrbRN7sI4PnDrwYfbIWV"
 
imge_path = os.path.dirname(os.path.abspath(__file__))+'\\img.jpg'
faceinfo_type = ['face_type','face_shape','gender','emotion','age','glasses','beauty','mask','face_probability','location']

def _async_raise(tid, exctype):
    """raises the exception, performs cleanup if needed"""
    tid = ctypes.c_long(tid)
    if not inspect.isclass(exctype):
        exctype = type(exctype)
    res = ctypes.pythonapi.PyThreadState_SetAsyncExc(tid, ctypes.py_object(exctype))
    if res == 0:
        print("invalid thread id")
    elif res != 1:
        # """if it returns a number greater than one, you're in trouble,
        # and you should call it again with exc=NULL to revert the effect"""
        ctypes.pythonapi.PyThreadState_SetAsyncExc(tid, None)
        print("PyThreadState_SetAsyncExc failed")
        
def stop_thread(thread):
    _async_raise(thread.ident, SystemExit)
    
def get_AcessToken(fun_apikey,fun_secretkey):
    #print fun_apikey,fun_secretkey
    data = {
    "grant_type":"client_credentials",
    "client_id":fun_apikey,
    "client_secret":fun_secretkey
    }
    r = requests.post(accesstokenURL,data)
    #print (r.text)
    t = json.loads(r.text)

    #print t['access_token']
    at = t['access_token']
    return at

def camer_open():
    cap2 = cv2.VideoCapture(0)  # 默认的摄像头
    cap2.set(cv2.CAP_PROP_FRAME_WIDTH, frame_in_w);
    cap2.set(cv2.CAP_PROP_FRAME_HEIGHT, frame_in_h);
    return cap2

globalimage=np.zeros((640,480,3), np.uint8) 

def camer_close(fun_cap):
    fun_cap.release()
    cv2.destroyAllWindows()

cap=0
ret_cap=0
frame=0
ret=1
face_num=0
info_list=0
img=0
label_choose=0
label_work=0
label=[]
img_back=0
label_changing=0
place_curshin=[-100,-100,-100,-100,-100,-100,-100,-100,-100,-100,-100,-100,-100]
place_curshout=[-100,-100,-100,-100,-100,-100,-100,-100,-100,-100,-100,-100,-100]

def make_photo(capp):
    global ret_cap,frame,ret,face_num,info_list,img,label_choose,label_work
    global post_queue,post_place,place_post,place_using,post_imp,label,label_changing,place_pic
    
    access_token=get_AcessToken(apikey,secretkey)  
    imgxx = cv2.imread('/home/xilinx/picture/System/start3.jpg')
    imgxx = cv2.resize(imgxx,(hdmix,hdmiy))
    outframe = hdmi_out.newframe()
    outframe[:] = imgxx
    hdmi_out.writeframe(outframe)
    while True:
        if(base.buttons[3].read()==1):
            break
        if(base.buttons[2].read()==1):
            break
        if(base.buttons[1].read()==1):
            break
        if(base.buttons[0].read()==1):
            break
    while True:
        if(label_work==0):
            if(label_choose==0):
                imgchoose=cv2.imread('/home/xilinx/picture/Choose/choose1.jpg')
            else:
                imgchoose=cv2.imread('/home/xilinx/picture/Choose/choose2.jpg')
            imgchoose = cv2.resize(imgchoose,(hdmix,hdmiy))
            outframe[:] = imgchoose
            hdmi_out.writeframe(outframe)
            while True:
                if(base.buttons[3].read()==1):
                    label_choose=1-label_choose
                    if(label_choose==0):
                        imgchoose=cv2.imread('/home/xilinx/picture/Choose/choose1.jpg')
                    else:
                        imgchoose=cv2.imread('/home/xilinx/picture/Choose/choose2.jpg')
                    imgchoose = cv2.resize(imgchoose,(hdmix,hdmiy))
                    outframe[:] = imgchoose
                    hdmi_out.writeframe(outframe)
                if(base.buttons[2].read()==1):
                    break
            label_work=1
            label_changing=0
            if(label_choose==0):
                fakecam1()
            else:
                img = cv2.imread('/home/xilinx/picture/Mode2/background.jpg')
                img = cv2.resize(img,(hdmix,hdmiy))
                outframe1 = hdmi_out.newframe()
                outframe1[:] = img
                hdmi_out.writeframe(outframe1)
                
                img_post=cv2.imread('/home/xilinx/picture/Mode2/Post/time.png')
                tttt2=threading.Thread(target=postin,args=(img_post,7,))
                tttt2.start()
                
                place_post=[-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1]
                for i0 in range(13):
                    img_tempxx = img_back[p_lt[i0][1]:p_rb[i0][1],p_lt[i0][0]:p_rb[i0][0]]
                    place_pic[i0]=img_tempxx
                
                for i0 in range(7):
                    post_imp[i0]=0
                    post_queue[i0]=i0
                    post_place[i0]=i0
                    place_post[i0]=i0
                
                for i0 in range(7,post_num):
                    post_imp[i0]=-100
                    post_queue[i0]=i0
                    post_place[i0]=-100
                    label[i0-7]=0
                
                place_using=[0,0,0,0,0,0,0,0,0,0,0,0,0]
                place_curshin=[-100,-100,-100,-100,-100,-100,-100,-100,-100,-100,-100,-100,-100]
                place_curshout=[-100,-100,-100,-100,-100,-100,-100,-100,-100,-100,-100,-100,-100]
                
                for i0 in range(7):
                    tttt2=threading.Thread(target=dopost,args=(i0,0,i0,))
                    tttt2.start()
                tttt2=threading.Timer(10,turn_around1)
                tttt2.start()
                tttt2=threading.Timer(2,judg)
                tttt2.start()
                #tttt2=threading.Timer(3,turn_around2)
                #tttt2.start()
                
                fakecam2()
        ret_cap, frame = cap.read()
        frame2=frame
        color=(0,0,0)
        img_gray= cv2.cvtColor(frame2,cv2.COLOR_RGB2GRAY)
        cv2.imwrite(imge_path, img_gray)
        image_base64=imgeTobase64()
        ret,face_num,info_list=get_face_response(access_token,image_base64)

def fakecam1():
    global ret_cap,frame,ret,face_num,info_list,cap,img,label_work
    img = cv2.imread('/home/xilinx/picture/Mode1/nb.jpg')
    img = cv2.resize(img,(hdmix,hdmiy))
    ret_cap, frame = cap.read()
    ret2,face_num2,info_list2=ret,face_num,info_list
    label=[0,0,0,0,0,0,0,0]
    dy = int(20/600*hdmiy)
    if(ret2==0 and ret_cap):
        for i0 in range(face_num2):
            w=int(info_list2[i0][faceinfo_type.index('location')])+100
            h=int(info_list2[i0][faceinfo_type.index('location')+1])+100
            y=int(info_list2[i0][faceinfo_type.index('location')+2])-80
            x=int(info_list2[i0][faceinfo_type.index('location')+3])-50
            fun_str=[]
            fun_str.append('age:'+ str(info_list2[i0][faceinfo_type.index('age')]))
            fun_str.append('emotion:'+info_list2[i0][faceinfo_type.index('emotion')])
            fun_str.append('beauty:'+str(info_list2[i0][faceinfo_type.index('beauty')]))
            fun_str.append('gender:'+info_list2[i0][faceinfo_type.index('gender')])
            fun_str.append('mask:'+str(info_list2[i0][faceinfo_type.index('mask')]))
            fun_str.append('glasses:'+info_list2[i0][faceinfo_type.index('glasses')])
            fun_str.append('face_probability:'+str(info_list2[i0][faceinfo_type.index('face_probability')]))
            cv2.circle(frame,(int(x+w/2),int(y+h/2)),int(((w*w+h*h)**0.5)/2.5),(80,180,230),8)
            x =place[i0][0]
            y1=place[i0][1]
            if (info_list2[i0][faceinfo_type.index('emotion')] == 'happy'):
                label[0]=1
            if (info_list2[i0][faceinfo_type.index('glasses')] == 'common'):
                label[1]=1
            if (info_list2[i0][faceinfo_type.index('beauty')] > 40):
                label[2]=1
            if (face_num2 > 1):
                label[3]=1
            if (info_list2[i0][faceinfo_type.index('age')]<30):
                label[4]=1
            if (info_list2[i0][faceinfo_type.index('mask')] == 0):
                label[5]=1
            for i in range(len(fun_str)): 
                y2= y1+i*dy
                cv2.putText(img,fun_str[i],(x,y2),cv2.FONT_HERSHEY_DUPLEX,0.5, (0, 0, 0),1)
    temp=0
    if(label[5]):
        cv2.putText(img,'Wear your mask!!',(place[4][0],place[4][1]+dy*3*temp),cv2.FONT_HERSHEY_DUPLEX,0.5,  (0, 0, 255),1)
        cv2.putText(img,'Lives matters!',(place[4][0],place[4][1]+dy+dy*3*temp),cv2.FONT_HERSHEY_DUPLEX,0.5,  (0, 0, 255),1)
        temp=temp+1
    if(label[0]):
        cv2.putText(img,'You are happy.',(place[4][0],place[temp][1]+dy*3*temp),cv2.FONT_HERSHEY_DUPLEX,0.5,  (101, 67, 254),1)
        cv2.putText(img,'Congratulations!',(place[4][0],place[temp][1]+dy+dy*3*temp),cv2.FONT_HERSHEY_DUPLEX,0.5,  (101, 67, 254),1)
        temp=temp+1
    if(label[1]):
        cv2.putText(img,'You wear glasses. ',(place[4][0],place[4][1]+dy*3*temp),cv2.FONT_HERSHEY_DUPLEX,0.5, (43, 116, 217),1)
        cv2.putText(img,'Protect your eyes!',(place[4][0],place[4][1]+dy+dy*3*temp),cv2.FONT_HERSHEY_DUPLEX,0.5, (43, 116, 217),1)
        temp=temp+1
    if(label[2]):
        cv2.putText(img,'You are beautiful!',(place[4][0],place[4][1]+dy*3*temp),cv2.FONT_HERSHEY_DUPLEX,0.5, (213, 188, 38),1)
        cv2.putText(img,'Nice to see you!',(place[4][0],place[4][1]+dy+dy*3*temp),cv2.FONT_HERSHEY_DUPLEX,0.5, (213, 188, 38),1)
        temp=temp+1
    if(label[3] and temp<3):
        cv2.putText(img,'So many people!',(place[4][0],place[4][1]+dy*3*temp),cv2.FONT_HERSHEY_DUPLEX,0.5, (103, 77, 1),1)
        cv2.putText(img,'Surprise!',(place[4][0],place[4][1]+dy+dy*3*temp),cv2.FONT_HERSHEY_DUPLEX,0.5, (103, 77, 1),1)
        temp=temp+1
    if(label[4] and temp<3):
        cv2.putText(img,'Go to study!',(place[4][0],place[4][1]+dy*3*temp),cv2.FONT_HERSHEY_DUPLEX,0.5, (4, 218, 253),1)
        cv2.putText(img,'Day day up!',(place[4][0],place[4][1]+dy+dy*3*temp),cv2.FONT_HERSHEY_DUPLEX,0.5, (4, 218, 253),1)
        temp=temp+1
    outframe1 = hdmi_out.newframe()
    outframe1[:] = img
    xxx=int(245/800*hdmix)
    yyy=int(200/600*hdmiy)
    frame3 = cv2.resize(frame,(xxx,yyy))
    outframe1[hdmiy-yyy:hdmiy,hdmix-xxx:hdmix,:] = frame3
    hdmi_out.writeframe(outframe1)
    global tttt
    #stop_thread(tttt)
    if(base.buttons[0].read()==1):
        label_work=0
        return
    tttt = threading.Timer(0.1, fakecam1)
    tttt.start()
    return

def postin(post,placeid):
    global img_back,img,place_pic,place_using
    while(place_using[placeid]==1):
        time.sleep(0.1)
    place_using[placeid]=1
    alpha=0.1
    x1=p_lt[placeid][0]
    y1=p_lt[placeid][1]
    x2=p_rb[placeid][0]
    y2=p_rb[placeid][1]
    post=cv2.resize(post,(x2-x1,y2-y1))
    img_temp=img_back[y1:y2,x1:x2]
    for i0 in range(1,11):
        place_pic[placeid]=cv2.addWeighted(img_temp,1.0-alpha,post,alpha,0)
        alpha=alpha+0.1
        time.sleep(0.05)
    place_using[placeid]=0
    return

def postout(post,placeid):
    global img_back,img,place_pic,place_using
    while(place_using[placeid]==1):
        time.sleep(0.1)
    place_using[placeid]=1
    alpha=0.9
    x1=p_lt[placeid][0]
    y1=p_lt[placeid][1]
    x2=p_rb[placeid][0]
    y2=p_rb[placeid][1]
    post=cv2.resize(post,(x2-x1,y2-y1))
    img_temp=img_back[y1:y2,x1:x2]
    for i0 in range(1,11):
        place_pic[placeid]=cv2.addWeighted(img_temp,1.0-alpha,post,alpha,0)
        alpha=alpha-0.1
        time.sleep(0.05)
    place_using[placeid]=0
    return

def dopost(post_id,postio,place_temp):
    if(place_temp<0):
        return
    if(place_temp>=9):
        global place_post
        if(postio==0):
            for i0 in range(9,13):
                if(place_post[i0]<0):
                    place_temp=i0
                    place_post[i0]=post_id
                    postout(ad[i0-9],i0)
                    break
            else:
                return
        else:
            for i0 in range(9,13):
                if(place_post[i0]==post_id):
                    place_temp=i0
                    place_post[i0]=-1
                    break
            else:
                return
    if(place_temp==0):
        post_form=1
    elif(place_temp<3):
        post_form=2
    else:
        post_form=0
    if(postio==0):
        postin(post_list[post_id][post_form],place_temp)
        return
    elif(postio==1):
        postout(post_list[post_id][post_form],place_temp)
        return
    global place_curshin,place_curshout
    if(postio==3):
        if(place_curshout[place_temp]==post_id):
            place_curshout[place_temp]=-100
            return
        if(place_curshin[place_temp]==-100):
            place_curshin[place_temp]=post_id
        return
    elif(postio==4):
        if(place_curshin[place_temp]==post_id):
            place_curshin[place_temp]=-100
            return
        if(place_curshout[place_temp]==-100):
            place_curshout[place_temp]=post_id
        return   
    return

def curshrelease():
    global place_curshout,place_curshin,place_post
    for i0 in range(7):
        if(place_curshout[i0]>-100):
            tttt2=threading.Thread(target=dopost,args=(place_curshout[i0],1,i0,))
            tttt2.start()
            place_curshout[i0]=-100
    for i0 in range(7):
        if(place_curshin[i0]>-100):
            tttt2=threading.Timer(0.5,dopost,args=(place_curshin[i0],0,i0,))
            tttt2.start()
            place_curshin[i0]=-100
    for i0 in range(9,13):
        if(place_post[i0]==-1):
            tttt2=threading.Thread(target=postin,args=(ad[i0-9],i0,))
            tttt2.start()
            place_post[i0]=-2
    return

def judg():
    global ret_cap,ret,face_num,info_list,label_work,label_changing,label
    if(label_work==0):
        return
    while(label_changing==1):
        time.sleep(0.1)
    label_changing=1
    ret2,face_num2,info_list2=ret,face_num,info_list
    label_temp=[-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,
            -1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1]
    if(ret2==0 and ret_cap):
        for i0 in range(face_num2):
            if( info_list2[i0][faceinfo_type.index('face_probability')]<0.99):
                continue
            
            if (info_list2[i0][faceinfo_type.index('age')]<30 and info_list2[i0][faceinfo_type.index('gender')]=='male'):
                label_temp[0]=1
            else :
                if(label_temp[0]==-1):
                    label_temp[0]=0
            if (info_list2[i0][faceinfo_type.index('mask')] == 0):
                label_temp[8]=1
            else :
                if(label_temp[8]==-1):
                    label_temp[8]=0
            if (info_list2[i0][faceinfo_type.index('age')]>30 and info_list2[i0][faceinfo_type.index('age')]<60 and
                info_list2[i0][faceinfo_type.index('gender')]=='male'):
                label_temp[1]=1
            else :
                if(label_temp[1]==-1):
                    label_temp[1]=0
            if ( info_list2[i0][faceinfo_type.index('age')]<10 and info_list2[i0][faceinfo_type.index('age')] >5 and
                info_list2[i0][faceinfo_type.index('gender')]=='male'):
                label_temp[2]=1
            else :
                if(label_temp[2]==-1):
                    label_temp[2]=0
            if (info_list2[i0][faceinfo_type.index('age')]<10 and info_list2[i0][faceinfo_type.index('age')]>5 and
                info_list2[i0][faceinfo_type.index('gender')]=='female'):
                label_temp[3]=1
            else :
                if(label_temp[3]==-1):
                    label_temp[3]=0
            if (info_list2[i0][faceinfo_type.index('age')]>10 and info_list2[i0][faceinfo_type.index('age')]<30 and 
                info_list2[i0][faceinfo_type.index('gender')]=='male'):
                label_temp[4]=1
            else :
                if(label_temp[4]==-1):
                    label_temp[4]=0
            if (info_list2[i0][faceinfo_type.index('age')]>10 and info_list2[i0][faceinfo_type.index('age')]<30 and 
                info_list2[i0][faceinfo_type.index('gender')]=='female'):
                label_temp[5]=1
            else :
                if(label_temp[5]==-1):
                    label_temp[5]=0
            if (info_list2[i0][faceinfo_type.index('age')]>30 and info_list2[i0][faceinfo_type.index('age')]<60 and
                info_list2[i0][faceinfo_type.index('gender')]=='female'):
                label_temp[6]=1
            else :
                if(label_temp[6]==-1):
                    label_temp[6]=0
            if (info_list2[i0][faceinfo_type.index('glasses')] == 'common'):
                label_temp[7]=1
            else :
                if(label_temp[7]==-1):
                    label_temp[7]=0
            if (info_list2[i0][faceinfo_type.index('mask')] == 0):
                label_temp[9]=1
            else :
                if(label_temp[9]==-1):
                    label_temp[9]=0
            if (info_list2[i0][faceinfo_type.index('age')]<30 and info_list2[i0][faceinfo_type.index('gender')]=='female'):
                label_temp[11]=1
            else :
                if(label_temp[11]==-1):
                    label_temp[11]=0
    
    if(face_num2==1 and label[10]==0):
        img_temp123=cv2.imread("/home/xilinx/picture/Mode2/Post/note.png")
        postin(img_temp123,8)
        label[10]=1
    if(face_num2!=1 and label[10]==1):
        img_temp123=cv2.imread("/home/xilinx/picture/Mode2/Post/note.png")
        postout(img_temp123,8)
        label[10]=0
    
    if(label_temp[0]==1 and label[0]==0):
        label[0]=1
        changeimp(7,10)
    if(label_temp[0]==-1 and label[0]>0):
        label[0]=label[0]+1
        if(label[0]>3):
            label_temp[0]=0
    if(label_temp[0]==0 and label[0]>0):
        label[0]=0
        changeimp(7,-100)
        
    if(label_temp[8]==1 and label[8]==0):
        label[8]=1
        changeimp(9,1)
    if(label_temp[8]==-1 and label[8]>0):
        label[8]=label[8]+1
        if(label[8]>3):
            label_temp[8]=0
    if(label_temp[8]==0 and label[8]>0):
        label[8]=0
        changeimp(9,-100)
    
    if(label_temp[1]==1 and label[1]==0):
        label[1]=1
        changeimp(8,10)
        dopost(18,0,11)
        dopost(19,0,12)
    if(label_temp[1]==-1 and label[1]>0):
        label[1]=label[1]+1
        if(label[1]>3):
            label_temp[1]=0
    if(label_temp[1]==0 and label[1]>0):
        label[1]=0
        changeimp(8,-100)
        dopost(18,1,11)
        dopost(19,1,12)
        
    if(label_temp[2]==1 and label[2]==0):
        label[2]=1
        dopost(10,0,9)
        dopost(11,0,10)
    if(label_temp[2]==-1 and label[2]>0):
        label[2]=label[2]+1
        if(label[2]>3):
            label_temp[2]=0
    if(label_temp[2]==0 and label[2]>0):
        label[2]=0
        dopost(10,1,9)
        dopost(11,1,10)
        
    
    if(label_temp[3]==1 and label[3]==0):
        label[3]=1
        dopost(12,0,9)
        dopost(13,0,10)
    if(label_temp[3]==-1 and label[3]>0):
        label[3]=label[3]+1
        if(label[3]>3):
            label_temp[3]=0
    if(label_temp[3]==0 and label[3]>0):
        label[3]=0
        dopost(12,1,9)
        dopost(13,1,10)
    
    if(label_temp[4]==1 and label[4]==0):
        label[4]=1
        dopost(14,0,9)
        dopost(15,0,10)
    if(label_temp[4]==-1 and label[4]>0):
        label[4]=label[4]+1
        if(label[4]>3):
            label_temp[4]=0
    if(label_temp[4]==0 and label[4]>0):
        label[4]=0
        dopost(14,1,9)
        dopost(15,1,10)
    
    if(label_temp[5]==1 and label[5]==0):
        label[5]=1
        dopost(16,0,9)
        dopost(17,0,10)
    if(label_temp[5]==-1 and label[5]>0):
        label[5]=label[5]+1
        if(label[5]>3):
            label_temp[5]=0
    if(label_temp[5]==0 and label[5]>0):
        label[5]=0
        dopost(16,1,9)
        dopost(17,1,10)
    
    if(label_temp[6]==1 and label[6]==0):
        label[6]=1
        dopost(20,0,9)
        dopost(21,0,10)
    if(label_temp[6]==-1 and label[6]>0):
        label[6]=label[6]+1
        if(label[6]>3):
            label_temp[6]=0
    if(label_temp[6]==0 and label[6]>0):
        label[6]=0
        dopost(20,1,9)
        dopost(21,1,10)
    
    if(label_temp[7]==1 and label[7]==0):
        label[7]=1
        dopost(23,0,11)
    if(label_temp[7]==-1 and label[7]>0):
        label[7]=label[7]+1
        if(label[7]>3):
            label_temp[7]=0
    if(label_temp[7]==0 and label[7]>0):
        label[7]=0
        dopost(23,1,11)
    
    if(label_temp[9]==1 and label[9]==0):
        label[9]=1
        dopost(22,0,12)
    if(label_temp[9]==-1 and label[9]>0):
        label[9]=label[9]+1
        if(label[9]>3):
            label_temp[9]=0
    if(label_temp[9]==0 and label[9]>0):
        label[9]=0
        dopost(22,1,12)
    
    if(label_temp[11]==1 and label[11]==0):
        label[11]=1
        changeimp(24,10)
    if(label_temp[11]==-1 and label[11]>0):
        label[11]=label[11]+1
        if(label[11]>3):
            label_temp[11]=0
    if(label_temp[11]==0 and label[11]>0):
        label[11]=0
        changeimp(24,-100)
    
    curshrelease()
    time.sleep(1)
    label_changing=0
    tttt2=threading.Timer(2,judg)
    tttt2.start()
    return   



def changeimp(post_id,newimp):
    global post_queue,post_place,place_post,post_imp
    
    if(newimp==post_imp[post_id]):
        return
    
    dlabel=1
    if(newimp>post_imp[post_id]):
        dlabel=-1
    post_imp[post_id]=newimp
    i0=post_queue.index(post_id)
    i0=i0+dlabel
    while(i0>=0 and i0<len(post_queue)):
        if(post_imp[post_queue[i0]]*dlabel>newimp*dlabel):
            post_queue[i0-dlabel]=post_queue[i0]
        else:
            break
        i0=i0+dlabel
    i0=i0-dlabel
    post_queue[i0]=post_id
    
    if(post_place[post_id]==0):
        return
    
    blockzone1=3
    rank_temp=post_queue.index(place_post[0])
    if(rank_temp>2 and dlabel==-1):
        blockzone1=2
    if(rank_temp>1 and dlabel==1):
        blockzone1=2
    blockzone2=7
    if(rank_temp>6 and dlabel==-1):
        blockzone2=6
    if(rank_temp>5 and dlabel==1):
        blockzone2=6
    
    if(i0<blockzone1 and post_place[post_id]<3 and post_place[post_id]>=0):
        return
    if(i0>=blockzone1 and i0<blockzone2 and post_place[post_id]>2 and post_place[post_id]<7):
        return
    if(i0>=blockzone2 and post_place[post_id]<0):
        return
    if(dlabel==-1):
        if(i0<blockzone2 and post_place[post_id]<0):
            post_id2=post_queue[blockzone2]
            dopost(post_id2,4,post_place[post_id2])
            dopost(post_id,4,post_place[post_id])
            place_post[post_place[post_id2]]=post_id
            post_place[post_id2],post_place[post_id]=-100,post_place[post_id2]
            dopost(post_id2,3,post_place[post_id2])
            dopost(post_id,3,post_place[post_id])
        if(i0<blockzone1):
            post_id2=post_queue[blockzone1]
            dopost(post_id2,4,post_place[post_id2])
            dopost(post_id,4,post_place[post_id])
            place_post[post_place[post_id]],place_post[post_place[post_id2]]=place_post[post_place[post_id2]],place_post[post_place[post_id]]
            post_place[post_id],post_place[post_id2]=post_place[post_id2],post_place[post_id]
            dopost(post_id2,3,post_place[post_id2])
            dopost(post_id,3,post_place[post_id])
        return
    else:
        if(post_place[post_id]>=0 and post_place[post_id]<7 and i0>=blockzone2):
            post_id2=post_queue[blockzone2-1]
            dopost(post_id2,4,post_place[post_id2])
            dopost(post_id,4,post_place[post_id])
            place_post[post_place[post_id]]=post_id2
            post_place[post_id],post_place[post_id2]=post_place[post_id2],post_place[post_id]
            dopost(post_id2,3,post_place[post_id2])
            dopost(post_id,3,post_place[post_id])
            i0=post_queue.index(post_id2)
            post_id=post_id2
        if(post_place[post_id]<3 and post_place[post_id]>=0 and i0>=blockzone1):
            post_id2=post_queue[blockzone1-1]
            dopost(post_id2,4,post_place[post_id2])
            dopost(post_id,4,post_place[post_id])
            place_post[post_place[post_id]],place_post[post_place[post_id2]]=place_post[post_place[post_id2]],place_post[post_place[post_id]]
            post_place[post_id],post_place[post_id2]=post_place[post_id2],post_place[post_id]
            dopost(post_id2,3,post_place[post_id2])
            dopost(post_id,3,post_place[post_id])
        return  
    return

def turn_around1():
    global label_work,post_queue,post_place,place_post,label_changing
    if(label_work==0):
        return
    while(label_changing==1):
        time.sleep(0.1)
    label_changing=1
    if(place_post[0]==post_queue[0]):
        tttt2=threading.Thread(target=dopost,args=(post_queue[0],1,post_place[post_queue[0]],))
        tttt2.start()
        tttt2=threading.Thread(target=dopost,args=(post_queue[1],1,post_place[post_queue[1]],))
        tttt2.start()
        
        place_post[0],place_post[post_place[post_queue[1]]]=place_post[post_place[post_queue[1]]],place_post[0]
        post_place[post_queue[0]],post_place[post_queue[1]]=post_place[post_queue[1]],post_place[post_queue[0]]
        
        tttt2=threading.Timer(0.5,dopost,args=(post_queue[0],0,post_place[post_queue[0]],))
        tttt2.start()
        tttt2=threading.Timer(0.5,dopost,args=(post_queue[1],0,post_place[post_queue[1]],))
        tttt2.start()
        
    elif(place_post[0]==post_queue[1]):
        tttt2=threading.Thread(target=dopost,args=(post_queue[1],1,post_place[post_queue[1]],))
        tttt2.start()
        tttt2=threading.Thread(target=dopost,args=(post_queue[2],1,post_place[post_queue[2]],))
        tttt2.start()
        
        place_post[0],place_post[post_place[post_queue[2]]]=place_post[post_place[post_queue[2]]],place_post[0]
        post_place[post_queue[1]],post_place[post_queue[2]]=post_place[post_queue[2]],post_place[post_queue[1]]
        
        tttt2=threading.Timer(0.5,dopost,args=(post_queue[1],0,post_place[post_queue[1]],))
        tttt2.start()
        tttt2=threading.Timer(0.5,dopost,args=(post_queue[2],0,post_place[post_queue[2]],))
        tttt2.start()
     
    elif(place_post[0]==post_queue[2]):
        tttt2=threading.Thread(target=dopost,args=(post_queue[2],1,post_place[post_queue[2]],))
        tttt2.start()
        tttt2=threading.Thread(target=dopost,args=(post_queue[0],1,post_place[post_queue[0]],))
        tttt2.start()
        
        place_post[0],place_post[post_place[post_queue[0]]]=place_post[post_place[post_queue[0]]],place_post[0]
        post_place[post_queue[0]],post_place[post_queue[2]]=post_place[post_queue[2]],post_place[post_queue[0]]
        
        tttt2=threading.Timer(0.5,dopost,args=(post_queue[2],0,post_place[post_queue[2]],))
        tttt2.start()
        tttt2=threading.Timer(0.5,dopost,args=(post_queue[0],0,post_place[post_queue[0]],))
        tttt2.start()
    
    else:
        tttt2=threading.Thread(target=dopost,args=(place_post[0],1,post_place[place_post[0]],))
        tttt2.start()
        tttt2=threading.Thread(target=dopost,args=(post_queue[0],1,post_place[post_queue[0]],))
        tttt2.start()
        tttt2=threading.Thread(target=dopost,args=(post_queue[2],1,post_place[post_queue[2]],))
        tttt2.start()
        
        tempxtg=place_post[0]
        place_post[0],place_post[post_place[post_queue[0]]],place_post[post_place[post_queue[2]]]=post_queue[0],post_queue[2],place_post[0]
        post_place[post_queue[0]],post_place[post_queue[2]],post_place[tempxtg]=0,post_place[post_queue[0]],post_place[post_queue[2]]
        
        tttt2=threading.Timer(0.5,dopost,args=(post_queue[2],0,post_place[post_queue[2]],))
        tttt2.start()
        tttt2=threading.Timer(0.5,dopost,args=(post_queue[0],0,post_place[post_queue[0]],))
        tttt2.start()
        
        if(post_queue.index(tempxtg)>6):
            place_post[post_place[tempxtg]]=post_queue[6]
            post_place[post_queue[6]]=post_place[tempxtg]
            post_place[tempxtg]=-100
            tempxtg=post_queue[6]
        tttt2=threading.Timer(0.5,dopost,args=(tempxtg,0,post_place[tempxtg],))
        tttt2.start()
    time.sleep(1)
    label_changing=0
    tttt2=threading.Timer(9,turn_around1)
    tttt2.start()
    return

        
    
def fakecam2():
    global img,label_work
    if(label_work==0):
        return
    for i0 in range(13):
        img[p_lt[i0][1]:p_rb[i0][1],p_lt[i0][0]:p_rb[i0][0]]=place_pic[i0]
    
    outframe1 = hdmi_out.newframe()
    outframe1[:] = img
    hdmi_out.writeframe(outframe1)
    
    if(base.buttons[0].read()==1):
        label_work=0
        return
    
    global tttt
    tttt = threading.Timer(0.05, fakecam2)
    tttt.start()
    return

def response_parse(result_res):
    r = json.loads(result_res)
    #print (r)
    if r['error_code'] != 0:
       # print (ret)
        return  r['error_code'],0, 0
    face_num=r['result']['face_num']
    result_parse= []
    for i0 in range(face_num):
        face_list = r['result']['face_list'][i0]
        #print face_list
        #print ( len(face_list) )
        result_parse.append([])
        for i in range(len(faceinfo_type)):
            if ((faceinfo_type[i] == 'age') or (faceinfo_type[i] == 'beauty') or (faceinfo_type[i] == 'face_probability')):
                result_parse[i0].append(face_list[faceinfo_type[i]])
            elif(faceinfo_type[i] == 'location'):
                result_parse[i0].append(face_list[faceinfo_type[i]]['width'])
                result_parse[i0].append(face_list[faceinfo_type[i]]['height'])
                result_parse[i0].append(face_list[faceinfo_type[i]]['top'])
                result_parse[i0].append(face_list[faceinfo_type[i]]['left'])

            else:
                result_parse[i0].append(face_list[faceinfo_type[i]]['type'])
    return 0,face_num,result_parse

def get_face_response(fun_access_token,base64_imge):
    header = {
    "Content-Type":"application/json"
    }
    data={
    "image":base64_imge,
    "image_type":"BASE64",
    "face_field":"faceshape,facetype,age,gender,glasses,eye_status,emotion,race,beauty,mask,face_probability",
    "max_face_num":5
    }
    url = apiURL + "?access_token="+fun_access_token
    r = requests.post(url,json.dumps(data),header)
    #print (r.url)
    #print (r.text)
    ret=response_parse(r.text)
    return ret
 
def imgeTobase64():
    with open(imge_path,'rb') as f:
        base64_data = base64.b64encode(f.read())
    s = base64_data.decode()
    #print("data:imge/jpeg;base64,%s"%s)
    s = s[s.find(',')+1:]
    #print s
    return s



def main():
    global img_back,ad
    img_back = cv2.imread('/home/xilinx/picture/Mode2/background.jpg')
    img_back = cv2.resize(img_back,(hdmix,hdmiy))
    imgxx = cv2.imread('/home/xilinx/picture/System/start1.jpg')
    imgxx = cv2.resize(imgxx,(hdmix,hdmiy))
    outframe = hdmi_out.newframe()
    outframe[:] = imgxx
    hdmi_out.writeframe(outframe)
    access_token=get_AcessToken(apikey,secretkey)
    global cap,post_list,post_imp,post_queue,post_place,label
    cap=camer_open()
    imgxx = cv2.imread('/home/xilinx/picture/System/start2.jpg')
    imgxx = cv2.resize(imgxx,(hdmix,hdmiy))
    
    outframe[:] = imgxx
    hdmi_out.writeframe(outframe)
    
    for i0 in range(13):
        img_tempxx = img_back[p_lt[i0][1]:p_rb[i0][1],p_lt[i0][0]:p_rb[i0][0]]
        place_pic.append(img_tempxx)
    
    for i0 in range(post_num):
        post_list.append([])
        post_imp.append(-100)
        post_queue.append(i0)
        post_place.append(-100)
        label.append(0)
        img_xtemp=cv2.imread(post_path+str(i0+1)+'h.png')
        post_list[i0].append(img_xtemp)
    for i0 in range(3):
        img_xtemp=cv2.imread(post_path+str(i0+1)+'s.png')
        post_list[i0].append(img_xtemp)
    for i0 in range(7,10):
        img_xtemp=cv2.imread(post_path+str(i0+1)+'s.png')
        post_list[i0].append(img_xtemp)
    for i0 in range(3):
        img_xtemp=cv2.imread(post_path+str(i0+1)+'.png')
        post_list[i0].append(img_xtemp)
    for i0 in range(7,10):
        img_xtemp=cv2.imread(post_path+str(i0+1)+'.png')
        post_list[i0].append(img_xtemp)
    for i0 in range(4):
        img_xtemp=cv2.imread("/home/xilinx/picture/Mode2/Post/ad"+str(i0+1)+'.png')
        ad.append(img_xtemp)
    for i0 in range(24,post_num):
        img_xtemp=cv2.imread(post_path+str(i0+1)+'s.png')
        post_list[i0].append(img_xtemp)
        img_xtemp=cv2.imread(post_path+str(i0+1)+'.png')
        post_list[i0].append(img_xtemp)
    make_photo(cap)
    return


if __name__ == '__main__':
    main()
