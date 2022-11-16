import tkinter as tk
import cv2
import os
import numpy as np
import math
import pymysql as mysql
from tkinter import *
from PIL import Image, ImageTk
import RPi.GPIO as GPIO

def dbconnect():
	db = mysql.connect(host = '140.136.150.94',
	port= 3306,
	user = "hank",
	passwd ="0920",
	db = "cloth",
	charset = 'utf8')
	global cursor
	cursor = db.cursor()
	
def datacount():
	global cm,cw,pm,pw
	cursor.execute("SELECT COUNT(大小) FROM cloth_men")
	cm = int(str(cursor.fetchone()).replace("(",'').replace(',)',''))
	cursor.execute("SELECT COUNT(大小) FROM cloth_women")
	cw = int(str(cursor.fetchone()).replace("(",'').replace(',)',''))
	cursor.execute("SELECT COUNT(大小) FROM pant_men")
	pm = int(str(cursor.fetchone()).replace("(",'').replace(',)',''))
	cursor.execute("SELECT COUNT(大小) FROM pant_women")
	pw = int(str(cursor.fetchone()).replace("(",'').replace(',)',''))
	
def clothdata(number):
	global sex,cursor
	if sex == 1:
		s = "SELECT 名稱,大小,價錢 FROM cloth_men where 編號 = " + str(number)
	else:
		s = "SELECT 名稱,大小,價錢 FROM cloth_women where 編號 = " + str(number)
	cursor.execute(s)
	return cursor.fetchone()
	
def pantdata(number):
	global sex,cursor
	if sex == 1:
		s = "SELECT 名稱,大小,價錢 FROM pant_men where 編號 = " + str(number)
	else:
		s = "SELECT 名稱,大小,價錢 FROM pant_women where 編號 = " + str(number)
	cursor.execute(s)
	return cursor.fetchone()

def findPos(thresh,imgray):
	face_cascade = cv2.CascadeClassifier('haarcascade_frontalface_default.xml')
	faces = face_cascade.detectMultiScale(imgray, 1.1 , 4)
	face_x, face_y, face_w, face_h = findPart(imgray,faces)
	face = [face_x, face_y, face_w, face_h]

	upper_cascade = cv2.CascadeClassifier('haarcascade_upperbody.xml')
	upper = upper_cascade .detectMultiScale(imgray, 1.1 , 3)
	upper_x, upper_y, upper_w, upper_h = findPart(imgray,upper)
	up = [upper_x,upper_y,upper_w/2,upper_h]

	lower_cascade = cv2.CascadeClassifier('haarcascade_lowerbody.xml')
	lower = lower_cascade.detectMultiScale(thresh, 1.1 , 3)

	lower_x, lower_y, lower_w, lower_h = findPart(thresh,lower)
	low = [lower_x, lower_y, lower_w/2,lower_h]

	if face ==[0,0,0,0] or up ==[0,0,0,0] or low ==[0,0,0,0]:
		global stop
		stop = 1
	return face, up, low
	
def findPart(img,part):
	part_x = part_y = part_w = part_h = 0
	for (x,y,w,h) in part:
		part_x = x
		part_y = y
		part_w = w
		part_h = h
	print(part_x,part_y,part_w,part_h)
	return part_x,part_y,part_w,part_h

#衣服褲子等比例縮放
def clothResize(cloth_img,size,changesize):
	rows,cols = cloth_img.size
	p = size/rows
	(cloth_w,cloth_h) = (int(rows*p*changesize),int(cols*p*changesize))
	return (cloth_w,cloth_h)

#將衣服褲子與人圖片結合
def wear(pos,cloth_img,man_img):
	row,cols = cloth_img.size
	resultPicture = Image.new('RGBA', man_img.size, (0, 0, 0, 0))
	resultPicture.paste(man_img,(0,0))
	resultPicture.paste(cloth_img, pos ,cloth_img)
	return resultPicture

#基底
class basedesk():
	def __init__(self,master):
		self.root = master
		self.root.config()
		self.root.title('換衣穿搭系統')
		self.root.geometry('1024x540')
		initface(self.root)

#初始頁面
class initface():
	#視窗初始化
	def __init__(self,master):
		self.master = master
		self.initface = Frame(self.master,bg = '#97CBFF')
		self.initface.pack(fill = BOTH, expand = YES)
		global img_camera, img_picture
		img_camera = Image.open("icon/camera.png").resize((290,290),Image.ANTIALIAS)
		img_camera = ImageTk.PhotoImage(img_camera)
		img_picture = Image.open("icon/image.png").resize((290,290),Image.ANTIALIAS)
		img_picture = ImageTk.PhotoImage(img_picture)
		self.title()
		self.button()
	#顯示標題
	def title(self):
		l_title = Label(self.initface, text = '換衣穿搭系統',bg = '#0080FF', font=('Arial', 68),fg = "white")
		l_title.place(x = 230,y = 55)
	#顯示按鈕
	def button(self):
		b_camera = Button(self.initface,image = img_camera, bg = '#FCFCFC', command = self.camera)
		b_camera.place(x = 140,y = 210)
		b_picture = Button(self.initface, image = img_picture, bg = '#FCFCFC',command = self.album)
		b_picture.place(x = 580,y = 210)
	#切換至拍照頁面
	def camera(self):
		self.initface.destroy()
		takephoto(self.master)
	#切換至登入頁面
	def album(self):
		self.initface.destroy()
		show_picture(self.master)

#拍照頁面
class takephoto():
	#視窗初始化
	def __init__(self,master):
		self.master = master
		self.takephoto = Frame(self.master, bg = '#97CBFF')
		self.takephoto.pack(fill = BOTH, expand = YES)
		global img_takephoto
		img_takephoto = Image.open("icon/camera.png").resize((150,150),Image.ANTIALIAS)
		img_takephoto = ImageTk.PhotoImage(img_takephoto)
		global takewindow
		takewindow = Label(self.takephoto)
		takewindow.place(x = 65,y = 0)
		global flag
		flag = 0
		self.text()
		self.button()
		self.take()
	#顯示文字
	def text(self):
		l_text1 = Label(self.takephoto, text = '請依指定的線',bg = '#FFFF37', font=('Arial', 25),fg = "black")
		l_text1.place(x = 750,y = 150)
		l_text2 = Label(self.takephoto, text = '拍攝全身照',bg = '#FFFF37', font=('Arial', 25),fg = "black")
		l_text2.place(x = 766,y = 200)
	#拍照畫面
	def take(self):
		ret, frame = cap.read()
		frame1 = cv2.resize(frame,(640,480))
		frame2 = frame[0 : 480, 85 : 535]
		#輔助線放置
		color=(0,255,0)
		cv2.line(frame1, (85,0), (535,0), color,3) 
		cv2.line(frame1, (85,480), (535,480), color,3)
		cv2.line(frame1, (85,0), (85,480), color,3)
		cv2.line(frame1, (535,0), (535,480), color,3)
		cv2.line(frame1, (270,120), (370,120), color,3)
		cv2.putText(frame1, 'Chin', (490,120), cv2.FONT_HERSHEY_COMPLEX, 0.5, (0,255,0), 1, 4)
		cv2.line(frame1, (245,150), (395,150), color,3)
		cv2.putText(frame1, 'Shoulder', (415,150), cv2.FONT_HERSHEY_COMPLEX, 0.5, (0,255,0), 1, 4)
		cv2.line(frame1, (275,150), (250,230), color,3)
		cv2.line(frame1, (375,150), (395,230), color,3)
		cv2.putText(frame1, 'Arm', (410,190), cv2.FONT_HERSHEY_COMPLEX, 0.5, (0,255,0), 1, 4)
		cv2.line(frame1, (220,230), (420,230), color,3)
		cv2.line(frame1, (220,250), (420,250), color,3)
		cv2.putText(frame1, 'Waist', (423,400), cv2.FONT_HERSHEY_COMPLEX, 0.5, (0,255,0), 1, 4)
		cv2.line(frame1, (320,100), (320,400), color,3)
		cv2image = cv2.cvtColor(frame1, cv2.COLOR_BGR2RGBA) 
		img = Image.fromarray(cv2image)
		imgtk = ImageTk.PhotoImage(image = img) 
		takewindow.imgtk = imgtk 
		takewindow.configure(image=imgtk) 
		takewindow.after(10,self.take) 
		#按下按鈕後將圖片儲存
		if flag == 1:
			cv2.imwrite(path + "/alluser/user" + str(usercount)+ ".png", frame2)
			#建立使用者資料夾
			filepath = path + "/alluser/user" + str(usercount)
			if not os.path.isdir(filepath):
				os.makedirs(filepath)
			cloth_file = open(path + "/alluser/user" +str(usercount) + "/user" + str(usercount)+ "_cloth.txt","a")
			pant_file = open(path + "/alluser/user" +str(usercount) + "/user" + str(usercount)+ "_pant.txt","a")
			info_cloth_file = open(path + "/alluser/user" +str(usercount) + "/user" + str(usercount)+ "_infocloth.txt","a")
			info_pant_file = open(path + "/alluser/user" +str(usercount) + "/user" + str(usercount)+ "_infopant.txt","a")
			#LED燈暗
			GPIO.output(21,GPIO.LOW)
	#顯示按鈕
	def button(self):
		b_takephoto = Button(self.takephoto,image = img_takephoto, bg = '#FCFCFC', command = self.save)
		b_takephoto.place(x = 780,y = 350)
	#拍照
	def save(self):
		#LED燈亮
		GPIO.output(21,GPIO.HIGH)
		#使用者計數
		global flag,usercount
		usercount = usercount + 1
		flag = 1
		self.take()
		self.check()
	#確認使用此照片
	def check(self):
		global username
		username = 'user' + str(usercount)
		print(username)
		self.takephoto.destroy()
		retakephoto(self.master)

#重拍頁面
class retakephoto():
	#視窗初始化
	def __init__(self,master):
		self.master = master
		self.retakephoto = Frame(self.master, bg = '#97CBFF')
		self.retakephoto.pack(fill = BOTH, expand = YES)

		global img_takephoto
		img_takephoto = Image.open("icon/camera.png").resize((150,150),Image.ANTIALIAS)
		img_takephoto = ImageTk.PhotoImage(img_takephoto)
		global img_person
		img_person = Image.open(path + "/alluser/user" + str(usercount)+ ".png")
		img_person = ImageTk.PhotoImage(img_person)
		global stop
		stop = 0

		self.checkpos()
		self.show_person()
		self.text()
		self.button()

	#確認照片偵測無誤
	def checkpos(self):
		person_img = cv2.imread(path + "/alluser/user" + str(usercount)+ ".png")
		imgray = cv2.cvtColor(person_img, cv2.COLOR_BGR2GRAY)
		ret, thresh = cv2.threshold(imgray, 100, 255,cv2.THRESH_BINARY)
		face, up, low = findPos(thresh,imgray)
		if stop == 1:
			l_retakephoto = Label(self.retakephoto, text = '無法偵測請重新拍攝',bg = '#FF2D2D', font=('Arial', 28),fg = "black") 
			l_retakephoto.place(x = 640,y = 200)
	#顯示拍攝照片
	def show_person(self):
		photowindow = Label(self.retakephoto,image = img_person)
		photowindow.place(x = 150,y = 0)
	#顯示文字
	def text(self):
		if stop == 0:
			l_retakephoto = Label(self.retakephoto, text = '確認是否使用此張照片',bg = '#FFFF37', font=('Arial', 28),fg = "black") 
			l_retakephoto.place(x = 625,y = 210)
	#顯示按鈕
	def button(self):
		b_retakephoto = Button(self.retakephoto,image = img_takephoto, bg = '#FCFCFC', command = self.back_takephote)
		b_retakephoto.place(x = 640,y = 350)
		if stop == 0:
			b_check = Button(self.retakephoto,text = '確認', command = self.check, bg = '#FCFCFC', font=('Arial', 48),fg = "black")
			b_check.place(x = 840,y = 350,width = 150, height = 150)
	#切回至拍照頁面
	def back_takephote(self):
		global usercount
		usercount = usercount - 1
		self.retakephoto.destroy()
		takephoto(self.master)
	#切回至選擇模式頁面
	def check(self):
		global username
		username = 'user' + str(usercount)
		usercount_file = open(path + "/alluser/usercount.txt",'w')
		usercount_file.write(str(usercount)+ '\n')
		usercount_file.close()
		self.retakephoto.destroy()
		choose(self.master)

#選擇已拍攝照片登入頁面
class show_picture():
	#視窗初始化
	def __init__(self,master):
		self.master = master
		self.show_picture = Frame(self.master, bg = '#97CBFF')
		self.show_picture.pack(fill = BOTH, expand = YES)

		global img_previouspage,img_nextpage,img_takephoto1
		img_previouspage = Image.open("icon/previouspage.png").resize((100,100),Image.ANTIALIAS)
		img_previouspage = ImageTk.PhotoImage(img_previouspage)
		img_nextpage = Image.open("icon/nextpage.png").resize((100,100),Image.ANTIALIAS)
		img_nextpage = ImageTk.PhotoImage(img_nextpage)
		img_takephoto1 = Image.open("icon/camera.png").resize((100,100),Image.ANTIALIAS)
		img_takephoto1 = ImageTk.PhotoImage(img_takephoto1)
		global img_user
		img_user = [0]
		for i in range (1,usercount + 1):
			img_user.append('img_user' + str(i))
			img_user[i] = Image.open(path + "/alluser/user" + str(i)+ ".png").resize((280,340),Image.ANTIALIAS)
			img_user[i] = ImageTk.PhotoImage(img_user[i])
		global time_photocount, last_photocount
		time_photocount = int(usercount / 3) 
		last_photocount = usercount % 3 
		if last_photocount != 0:
			time_photocount = time_photocount + 1 

		self.show_photo()
		self.text()
		self.button()

	#顯示已拍攝圖片
	def show_photo(self):
		global time_photocount, nowpage, last_photocount
		if nowpage <= time_photocount:
			if nowpage == time_photocount and last_photocount == 1:
				button_user1 = Button(self.show_picture,image = img_user[(nowpage - 1) * 3 + 1], bg = '#FCFCFC', command = self.go_choose1)
				button_user1.place(x = 40 ,y = 33)
			elif nowpage == time_photocount and last_photocount == 2:
				button_user1 = Button(self.show_picture,image = img_user[(nowpage - 1) * 3 + 1], bg = '#FCFCFC', command = self.go_choose1)
				button_user1.place(x = 40 ,y = 33)
				button_user2 = Button(self.show_picture,image = img_user[(nowpage - 1) * 3 + 2], bg = '#FCFCFC', command = self.go_choose2)
				button_user2.place(x = 370,y = 33)
			else:
				button_user1 = Button(self.show_picture,image = img_user[(nowpage - 1) * 3 + 1], bg = '#FCFCFC', command = self.go_choose1)
				button_user1.place(x = 40 ,y = 33)
				button_user2 = Button(self.show_picture,image = img_user[(nowpage - 1) * 3 + 2], bg = '#FCFCFC', command = self.go_choose2)
				button_user2.place(x = 370,y = 33)
				button_user3 = Button(self.show_picture,image = img_user[(nowpage - 1) * 3 + 3], bg = '#FCFCFC', command = self.go_choose3)
				button_user3.place(x = 700,y = 33)
	#顯示文字
	def text(self):
		l_choosephoto = Label(self.show_picture, text = '請選擇所需的照片',bg = '#0080FF', font=('Arial', 30),fg = "black") 
		l_choosephoto.place(x = 75,y = 440)
	#顯示按鈕
	def button(self):
		b_retakephoto = Button(self.show_picture,image = img_takephoto1, bg = '#FCFCFC', command = self.go_takephote)
		b_retakephoto.place(x = 775,y = 410)
		b_previouspage = Button(self.show_picture,image = img_previouspage, bg = '#FCFCFC', command = self.previouspage)
		b_previouspage.place(x = 650,y = 410)
		b_nextpage = Button(self.show_picture,image = img_nextpage, bg = '#FCFCFC', command = self.nextpage)
		b_nextpage.place(x = 900,y = 410)
	#下一頁
	def nextpage(self):
		global nowpage
		if nowpage < time_photocount:
			nowpage = nowpage + 1
		self.show_picture.destroy()
		show_picture(self.master)
	#上一頁
	def previouspage(self):
		global nowpage
		if nowpage > 1:
			nowpage = nowpage - 1
		self.show_picture.destroy()
		show_picture(self.master)
	#切回至拍照頁面
	def go_takephote(self):
		self.show_picture.destroy()
		takephoto(self.master)
	#切回至選擇模式頁面
	def go_choose1(self):
		global nowpage, username
		username = 'user' + str((nowpage - 1) * 3 + 1)
		self.show_picture.destroy()
		choose(self.master)
	def go_choose2(self):
		global nowpage,username
		username  = 'user' + str((nowpage - 1) * 3 + 2)
		self.show_picture.destroy()
		choose(self.master)
	def go_choose3(self):
		global nowpage,username
		username  = 'user' + str((nowpage - 1) * 3 + 3)
		self.show_picture.destroy()
		choose(self.master)

#選擇模式頁面
class choose():
	#視窗初始化
	def __init__(self,master):
		self.master = master
		self.choose = Frame(self.master, bg = '#97CBFF')
		self.choose.pack(fill = BOTH, expand = YES)

		global img_takephoto1, img_showpicture, img_system, img_tolike, img_upload
		img_takephoto1 = Image.open("icon/camera.png").resize((125,125),Image.ANTIALIAS)
		img_takephoto1 = ImageTk.PhotoImage(img_takephoto1)
		img_showpicture = Image.open("icon/image.png").resize((125,125),Image.ANTIALIAS)
		img_showpicture = ImageTk.PhotoImage(img_showpicture)
		img_system = Image.open("icon/system.png").resize((225,225),Image.ANTIALIAS)
		img_system = ImageTk.PhotoImage(img_system)
		img_tolike = Image.open("icon/tolike.png").resize((225,225),Image.ANTIALIAS)
		img_tolike = ImageTk.PhotoImage(img_tolike)
		img_upload = Image.open("icon/upload.png").resize((225,225),Image.ANTIALIAS)
		img_upload = ImageTk.PhotoImage(img_upload)

		self.text()
		self.button()
	#顯示文字
	def text(self):
		l_choosepmode = Label(self.choose, text = '請選擇模式',bg = '#0080FF', font=('Arial', 40),fg = "black") 
		l_choosepmode.place(x = 60,y = 60)
		l_system = Label(self.choose, text = '系統的服飾',bg = '#E6E6F2', font=('Arial', 30),fg = "black") 
		l_system.place(x = 87,y = 210)
		l_like = Label(self.choose, text = '收藏的服飾',bg = '#E6E6F2', font=('Arial', 30),fg = "black") 
		l_like.place(x = 405,y = 210)
		l_upload = Label(self.choose, text = '上傳至雲端的服飾',bg = '#E6E6F2', font=('Arial', 30),fg = "black") 
		l_upload.place(x = 675,y = 210)
	#顯示按鈕
	def button(self):
		b_takephoto = Button(self.choose,image = img_takephoto1, bg = '#FCFCFC', command = self.backto_takephoto)
		b_takephoto.place(x = 650,y = 38)
		b_showpicture = Button(self.choose, image = img_showpicture, bg = '#FCFCFC',command = self.back_picture)
		b_showpicture.place(x = 825,y = 38)
		b_system = Button(self.choose,image = img_system, bg = '#FCFCFC', command = self.go_system)
		b_system.place(x = 75,y = 285)
		b_tolike = Button(self.choose,image = img_tolike, bg = '#FCFCFC', command = self.go_like)
		b_tolike.place(x = 395 ,y = 285)
		b_upload = Button(self.choose,image = img_upload, bg = '#FCFCFC', command = self.go_upload)
		b_upload.place(x = 715,y = 285)
	
	#切換至拍照頁面
	def backto_takephoto(self):
		self.choose.destroy()
		takephoto(self.master)
	#切換至選擇登入頁面
	def back_picture(self):
		self.choose.destroy()
		show_picture(self.master)
	#切換至系統服飾頁面
	def go_system(self):
		self.choose.destroy()
		system(self.master)
	#切換至收藏服飾頁面
	def go_like(self):
		self.choose.destroy()
		like(self.master)
	#切換至上傳服飾頁面
	def go_upload(self):
		self.choose.destroy()
		upload(self.master)

#系統服飾
class system():
	#視窗初始化
	def __init__(self,master):
		self.master = master
		self.system = Frame(self.master, bg = '#97CBFF')
		self.system.pack(fill = BOTH , expand = YES)

		global img_person
		img_person = Image.open(path + "/alluser/" + str(username)+ ".png")
		
		global face,up,low
		person_img = cv2.imread(path + "/alluser/" + str(username)+ ".png")
		imgray = cv2.cvtColor(person_img, cv2.COLOR_BGR2GRAY)
		ret, thresh = cv2.threshold(imgray, 100, 255,cv2.THRESH_BINARY)
		face, up, low = findPos(thresh,imgray)

		global sex, clothcount ,pantcount
		sex = 1
		clothcount = 1
		pantcount = 1
		self.upsize = 1
		self.lowsize = 1
		self.show_person()
		self.info()
		self.showlike()
		self.button()
		self.buttonleft()
		self.Uscale()
		self.Lscale()

	#顯示人物並貼上衣服
	def show_person(self):
		picturewindow = Label(self.system)
		global sex , clothcount , pantcount
		if sex == 1:
			cloth = Image.open(path + '/m_cloth/m_c'+str(clothcount)+'.png')
			pant = Image.open(path + '/m_pant/m_p'+str(pantcount)+'.png')
		else:
			cloth = Image.open(path + '/w_cloth/w_c'+str(clothcount)+'.png')
			pant = Image.open(path + '/w_pant/w_p'+str(pantcount)+'.png')

		#衣服等比例縮放
		(cloth_row,cloth_cols) = clothResize(cloth,up[2],self.upsize)
		cloth = cloth.resize((cloth_row,cloth_cols))

		#褲子等比例縮放
		(pant_row,pant_cols) = clothResize(pant,low[2],self.lowsize)
		pant = pant.resize((pant_row,pant_cols))

		#找到身體部位
		cloth_pos = (int(face[0]+face[2]/2-cloth_row/2),(face[1]+face[3]))
		pant_pos = (int(face[0]+face[2]/2-pant_row/2),(low[1]))

		#貼上褲子
		image = wear(pant_pos,pant,img_person)
		#貼上衣服
		image = wear(cloth_pos,cloth,image)
		#顯示貼上結果
		imgtk = ImageTk.PhotoImage(image = image)
		picturewindow .imgtk = imgtk
		picturewindow .configure(image = imgtk)
		picturewindow .place(x = 200,y = 30)

	#顯示衣服褲子資訊
	def info(self):
		global clothcount, pantcount

		cloth = str(clothdata(clothcount))
		cloth = cloth.replace("'",'').replace('(','').replace(')','').replace(',','\n').replace(" ",'')
		l_infocloth = Label(self.system, text = cloth,bg = '#FFCCCC', font = ('Arial', 12))
		l_infocloth.place(x = 655,y = 1,width = 375,height = 270)

		pant = str(pantdata(pantcount))
		pant = pant.replace("'",'').replace('(','').replace(')','').replace(',','\n').replace(" ",'') 
		l_infopant = Label(self.system, text = pant,bg = '#CCEEFF', font=('Arial', 12))
		l_infopant.place(x = 655,y = 271, width = 375, height = 270)
	
	#檢查是否收藏
	def showlike(self):
		global clothiflike , pantiflike
		clothiflike = 2
		pantiflike = 2
		file_cloth = open(path + "/alluser/"+str(username)+"/"+str(username)+"_cloth.txt",'r')
		file_pant = open(path + "/alluser/"+str(username)+"/"+str(username)+"_pant.txt",'r')
		lines_cloth = []
		lines_pant = []
		for i in file_cloth:
			lines_cloth.append(i)
		for i in file_pant:
			lines_pant.append(i)
		if sex == 1:
			for i in lines_cloth:
				if i == (path + '/m_cloth/m_c'+str(clothcount)+'.png\n'):
					clothiflike = 1
					break
			for i in lines_pant:
				if i == (path + '/m_pant/m_p'+str(pantcount)+'.png\n'):
					pantiflike = 1
					break
		else:
			for i in lines_cloth:
				if i == (path + '/w_cloth/w_c'+str(clothcount)+'.png\n'):
					clothiflike = 1
					break
			for i in lines_pant:
				if i == (path + '/w_pant/w_p'+str(pantcount)+'.png\n'):
					pantiflike = 1
					break
		if clothiflike == 1:
			b_clothlike = Button(self.system, image = img_like, bg = '#FCFCFC' ,command = self.clothlike)
			b_clothlike.place(x = 950, y = 185)
		else:
			b_clothnolike = Button(self.system, image=img_nolike, bg = '#FCFCFC' ,command = self.clothnolike)
			b_clothnolike.place(x = 950, y = 185)
		if pantiflike == 1:
			b_pantlike = Button(self.system, image=img_like, bg = '#FCFCFC' ,command = self.pantlike)
			b_pantlike.place(x = 950, y = 455)
		else:
			b_pantnolike = Button(self.system, image = img_nolike, bg = '#FCFCFC' ,command = self.pantnolike)
			b_pantnolike.place(x = 950, y = 455)

	#衣服拉桿軸
	def Uscale(self):
		scale = Scale(self.system,from_ = 1 , to = 100, length = 150, width = 20 ,bg = '#FCFCFC' ,orient = 'horizontal' , command = self.set_upsize)
		scale.place(x = 655 , y = 1)
	#褲子拉桿軸
	def Lscale(self):
		lscale = Scale(self.system,from_ = 1 , to = 100, length = 150, width = 20 ,bg = '#FCFCFC' ,orient = 'horizontal' , command = self.set_lowsize)
		lscale.place(x = 655 , y = 271)
	#調整衣服大小
	def set_upsize(self,val):
		self.upsize = int(val) / 50
		self.show_person()
		self.button()
	#調整褲子大小
	def set_lowsize(self,val):
		self.lowsize = int(val) / 50
		self.show_person()
		self.button()

	#顯示按鈕
	def button(self):
		b_upleft = Button(self.system,image = img_left, bg = '#FCFCFC',command = self.clothprevious)
		b_upleft.place(x = 220, y = 150)
		b_upright = Button(self.system, image = img_right, bg = '#FCFCFC' ,command = self.clothnext)
		b_upright.place(x = 555, y = 150)
		b_downleft = Button(self.system, image = img_left, bg = '#FCFCFC',command = self.pantprevious)
		b_downleft.place(x = 220, y = 360)
		b_downright = Button(self.system, image = img_right, bg = '#FCFCFC' ,command = self.pantnext)
		b_downright.place(x = 555, y = 360)
	def buttonleft(self):
		b_back = Button(self.system, image = img_back ,bg = '#FCFCFC', command = self.back)
		b_back.place(x = 50,y = 70)
		b_boy = Button(self.system,image = img_boy, bg = '#FCFCFC', command = self.boy)
		b_boy.place(x = 50, y = 230)
		b_girl = Button(self.system,image = img_girl,bg = '#FCFCFC',command = self.girl)
		b_girl.place(x = 50, y = 380)

	#上一件衣服
	def clothprevious(self):
		global clothcount
		if clothcount > 1:
			clothcount = clothcount - 1
		self.show_person()
		self.info()
		self.showlike()
		self.button()
		self.Uscale()
		self.Lscale()
	#下一件衣服
	def clothnext(self):
		global clothcount,cm,cw
		if sex == 1:
			if clothcount < cm:
				clothcount = clothcount + 1
		else:
			if clothcount < cw:
				clothcount = clothcount + 1
		self.show_person()
		self.info()
		self.showlike()
		self.button()
		self.Uscale()
		self.Lscale()
	#上一件褲子
	def pantprevious(self):
		global pantcount
		if pantcount > 1:
			pantcount = pantcount - 1
		self.show_person()
		self.info()
		self.showlike()
		self.button()
		self.Uscale()
		self.Lscale()
	#下一件褲子
	def pantnext(self):
		global pantcount,pm,pw
		if sex == 1 :
			if pantcount < pm:
				pantcount = pantcount + 1
		else:
			if pantcount < pw:
				pantcount = pantcount + 1
		self.show_person()
		self.info()
		self.showlike()
		self.button()
		self.Uscale()
		self.Lscale()
	
	#取消衣服收藏
	def clothlike(self):
		global clothiflike
		clothiflike = 2 #2是不喜歡
		file_cloth = open(path + "/alluser/"+str(username)+"/"+str(username)+"_cloth.txt",'r')
		lines = file_cloth.readlines()
		file_clothDel = open(path + "/alluser/"+str(username)+"/"+str(username)+"_cloth.txt",'w')
		if sex == 1:
			d = path + '/m_cloth/m_c'+str(clothcount)+'.png\n'
			for line in lines:
				if d in line:
					continue
				file_clothDel.write(line)
			file_clothDel.close()
			d = path + '/m_cloth/m_c'+str(clothcount)+'.png\n'
			file_clike = open(path +"/alluser/"+str(username)+"/"+str(username)+"_infocloth.txt",'r' )
			lines = file_clike.readlines()
			file_clikeDel = open(path + "/alluser/"+str(username)+"/"+str(username)+"_infocloth.txt",'w')
			for line in lines:
				if line.find(d) > -1:
					continue
				file_clikeDel.write(line)
		else:
			d = path + '/w_cloth/w_c'+str(clothcount)+'.png\n'
			for line in lines:
				if d in line:
					continue
				file_clothDel.write(line)
			file_clothDel.close()
			d = path + '/w_cloth/w_c'+str(clothcount)+'.png\n'
			file_clike = open(path +"/alluser/"+str(username)+"/"+str(username)+"_infocloth.txt",'r' )
			lines = file_clike.readlines()
			file_clikeDel = open(path + "/alluser/"+str(username)+"/"+str(username)+"_infocloth.txt",'w')
			for line in lines:
				if line.find(d) > -1:
					continue
				file_clikeDel.write(line)
		self.showlike()

	#將衣服加入收藏
	def clothnolike(self):
		global clothiflike
		clothiflike = 1 #1是喜歡
		file_cloth = open(path + "/alluser/"+str(username)+"/"+str(username)+"_cloth.txt",'a')
		if sex == 1:
			file_cloth.write(path + '/m_cloth/m_c'+str(clothcount)+'.png\n')
			file_cloth.close()
			stri = path + '/m_cloth/m_c'+str(clothcount)+'.png\n'
			file_c = open(path +'/cloth_men.txt','r')
			lines = file_c.readlines()
			d = lines[clothcount]
			file_clike = open(path +"/alluser/"+str(username)+"/"+str(username)+"_infocloth.txt",'a' )
			string = d.strip('\n') + path + '/m_cloth/m_c'+str(clothcount)+'.png\n'
			file_clike.write(string)
			file_clike.close()
		else:
			file_cloth.write(path + '/w_cloth/w_c'+str(clothcount)+'.png\n')
			file_cloth.close()
			stri = path + '/w_cloth/w_c'+str(clothcount)+'.png\n'
			file_c = open(path +'/cloth_women.txt','r')
			lines = file_c.readlines()
			d = lines[clothcount]
			file_clike = open(path +"/alluser/"+str(username)+"/"+str(username)+"_infocloth.txt",'a' )
			string = d.strip('\n') + path + '/w_cloth/w_c'+str(clothcount)+'.png\n'
			file_clike.write(string)
			file_clike.close()
		self.showlike()
		
	#取消褲子收藏
	def pantlike(self):
		global pantiflike
		pantiflike = 2 #2是不喜歡
		file_pant = open(path + "/alluser/"+str(username)+"/"+str(username)+"_pant.txt",'r')
		lines = file_pant.readlines()
		file_pantDel = open(path + "/alluser/"+str(username)+"/"+str(username)+"_pant.txt",'w')
		if sex == 1:
			d = path + '/m_pant/m_p'+str(pantcount)+'.png\n'
			for line in lines:
				if d in line:
					continue
				file_pantDel.write(line)
			file_pantDel.close()
			d = path + '/m_pant/m_p'+str(pantcount)+'.png\n'
			file_clike = open(path +"/alluser/"+str(username)+"/"+str(username)+"_infopant.txt",'r' )
			lines = file_clike.readlines()
			file_clikeDel = open(path + "/alluser/"+str(username)+"/"+str(username)+"_infopant.txt",'w')
			for line in lines:
				if line.find(d) > -1:
					continue
				file_clikeDel.write(line)
		else:
			d = path + '/w_pant/w_p'+str(pantcount)+'.png\n'
			for line in lines:
				if d in line:
					continue
				file_pantDel.write(line)
			file_pantDel.close()
			d = path + '/w_pant/w_p'+str(pantcount)+'.png\n'
			file_clike = open(path +"/alluser/"+str(username)+"/"+str(username)+"_infopant.txt",'r' )
			lines = file_clike.readlines()
			file_clikeDel = open(path + "/alluser/"+str(username)+"/"+str(username)+"_infopant.txt",'w')
			for line in lines:
				if line.find(d) > -1:
					continue
				file_clikeDel.write(line)
		self.showlike()

	#將褲子加入收藏
	def pantnolike(self):
		global pantiflike
		pantiflike = 1 #1是喜歡
		file_pant = open(path + "/alluser/"+str(username)+"/"+str(username)+"_pant.txt",'a')
		if sex == 1:
			file_pant.write(path + '/m_pant/m_p'+str(pantcount)+'.png\n')
			file_pant.close()
			stri = path + '/m_pant/m_p'+str(clothcount)+'.png\n'
			file_c = open(path +'/pant_men.txt','r')
			lines = file_c.readlines()
			d = lines[pantcount]
			file_clike = open(path +"/alluser/"+str(username)+"/"+str(username)+"_infopant.txt",'a' )
			string = d.strip('\n') + path + '/m_pant/m_p'+str(pantcount)+'.png\n'
			file_clike.write(string)
			file_clike.close()
			file_pant.close()
		else:
			file_pant.write(path + '/w_pant/w_p'+str(pantcount)+'.png\n')
			file_pant.close()
			stri = path + '/w_pant/w_p'+str(clothcount)+'.png\n'
			file_c = open(path +'/pant_women.txt','r')
			lines = file_c.readlines()
			d = lines[pantcount]
			file_clike = open(path +"/alluser/"+str(username)+"/"+str(username)+"_infopant.txt",'a' )
			string = d.strip('\n') + path + '/w_pant/w_p'+str(pantcount)+'.png\n'
			file_clike.write(string)
			file_clike.close()
			file_pant.close()
		self.showlike()

	#切回至選擇模式頁面
	def back(self):
		self.system.destroy()
		choose(self.master)
		
	#切換男女服飾
	def boy(self):
		global sex, clothcount ,pantcount
		sex = 1
		clothcount = 1
		pantcount = 1
		self.show_person()
		self.info()
		self.showlike()
		self.button()
		self.Uscale()
		self.Lscale()
	def girl(self):
		global sex,clothcount ,pantcount
		sex = 2
		clothcount = 1
		pantcount = 1
		self.show_person()
		self.info()
		self.showlike()
		self.button()
		self.Uscale()
		self.Lscale()

#收藏服飾
class like():
	#視窗初始化
	def __init__(self,master):
		self.master = master
		self.like = Frame(self.master, bg = '#97CBFF')
		self.like.pack(fill = BOTH , expand = YES)
		
		global img_person
		img_person = Image.open(path + "/alluser/" + str(username)+ ".png")
		global face,up,low
		person_img = cv2.imread(path + "/alluser/" + str(username)+ ".png")
		imgray = cv2.cvtColor(person_img, cv2.COLOR_BGR2GRAY)
		ret, thresh = cv2.threshold(imgray, 100, 255,cv2.THRESH_BINARY)

		face, up, low = findPos(thresh,imgray)
		file_cloth = open(path + "/alluser/"+str(username)+"/"+str(username)+"_cloth.txt",'r')
		file_pant = open(path + "/alluser/"+str(username)+"/"+str(username)+"_pant.txt",'r')
		lines_cloth = []
		lines_pant = []
		for i in file_cloth:
			lines_cloth.append(i)
		for i in file_pant:
			lines_pant.append(i)
		self.len_cloth = len(lines_cloth)
		self.len_pant = len(lines_pant)
		self.countC = 0
		self.countP = 0
		self.upsize = 1
		self.lowsize = 1
		self.show()

	#若衣服和褲子收藏不大於零則切至錯誤頁面
	def show(self):
		global username
		if self.len_cloth == 0: 
			self.like.destroy()
			wrong(self.master)
		elif self.len_pant == 0:
			self.like.destroy()
			wrong(self.master)
		else:
			self.show_person()
			self.info()
			self.button()
			self.button1()
			self.Uscale()
			self.Lscale()

	#顯示人物並貼上衣服
	def show_person(self):
		picturewindow = Label(self.like)
		
		file_cloth = open(path + "/alluser/"+str(username)+"/"+str(username)+"_cloth.txt",'r')
		file_pant = open(path + "/alluser/"+str(username)+"/"+str(username)+"_pant.txt",'r')
		lines_cloth = []
		lines_pant = []
		for i in file_cloth:
			lines_cloth.append(i)
		for i in file_pant:
			lines_pant.append(i)
			
		self.len_cloth = len(lines_cloth)
		self.len_pant = len(lines_pant)
		
		self.nowC = lines_cloth[self.countC]
		self.nowP = lines_pant[self.countP]

		lines_cloth[self.countC] = lines_cloth[self.countC].replace('\'','/').strip('\n')
		lines_pant[self.countP] = lines_pant[self.countP].replace('\'','/').strip('\n')
		cloth = Image.open(lines_cloth[self.countC])
		pant = Image.open(lines_pant[self.countP])
	
		#衣服等比例縮放
		(cloth_row,cloth_cols) = clothResize(cloth,up[2],self.upsize)
		cloth = cloth.resize((cloth_row,cloth_cols))

		#褲子等比例縮放
		(pant_row,pant_cols) = clothResize(pant,low[2],self.lowsize)
		pant = pant.resize((pant_row,pant_cols))

		#找到身體部位
		cloth_pos = (int(face[0]+face[2]/2-cloth_row/2),(face[1]+face[3]))
		pant_pos = (int(face[0]+face[2]/2-pant_row/2),(low[1]))

		#貼上褲子
		image = wear(pant_pos,pant,img_person)
		#貼上衣服
		image = wear(cloth_pos,cloth,image)
		#顯示貼上結果
		imgtk = ImageTk.PhotoImage(image = image)
		picturewindow.imgtk = imgtk
		picturewindow.configure(image = imgtk)
		picturewindow.place(x = 200,y = 30)

	#顯示衣服褲子資訊
	def info(self):
		#上衣資訊
		file_clothinfo = open(path + "/alluser/"+str(username)+"/"+str(username)+"_infocloth.txt",'r')
		lines_clothinfo = file_clothinfo.readlines()
		for line in lines_clothinfo:
			if line.find(self.nowC) > -1:
				k = line.replace(self.nowC,'')
				l_infocloth = Label(self.like,text = k.replace(',', '\n\n'),bg = '#FFCCCC', font = ('Arial', 12))
				l_infocloth.place(x = 655,y = 1,width = 375,height = 270)
				break
		#褲子資訊
		file_pantinfo = open(path + "/alluser/"+str(username)+"/"+str(username)+"_infopant.txt",'r')
		lines_pantinfo = file_pantinfo.readlines()
		for line in lines_pantinfo:
			if line.find(self.nowP) > -1:
				t = line.replace(self.nowP,'')
				l_infopant = Label(self.like,text = t.replace(',', '\n\n'),bg = '#CCEEFF', font=('Arial', 12))
				l_infopant.place(x = 655,y = 271, width = 375, height = 270)
				break

	#衣服拉桿軸
	def Uscale(self):
		scale = Scale(self.like,from_ = 1 , to = 100, length = 150, width = 20 ,bg = '#FCFCFC',orient = 'horizontal' , command = self.set_upsize)
		scale.place(x = 655 , y = 1)
	#褲子拉桿軸
	def Lscale(self):
		lscale = Scale(self.like,from_ = 1 , to = 100, length = 150, width = 20 ,bg = '#FCFCFC',orient = 'horizontal' , command = self.set_lowsize)
		lscale.place(x = 655 , y = 271)
	#調整衣服大小
	def set_upsize(self,val):
		self.upsize = int(val) / 50
		self.show_person()
		self.button()
	#調整褲子大小
	def set_lowsize(self,val):
		self.lowsize = int(val) / 50
		self.show_person()
		self.button()
	
	#顯示按鈕
	def button(self):
		b_upleft = Button(self.like,image = img_left, bg = '#FCFCFC' ,command = self.clothprevious)
		b_upleft.place(x = 220, y = 150)
		b_upright = Button(self.like, image = img_right, bg = '#FCFCFC' ,command = self.clothnext)
		b_upright.place(x = 555, y = 150)
		b_downleft = Button(self.like, image = img_left, bg = '#FCFCFC',command = self.pantprevious)
		b_downleft.place(x = 220, y = 360)
		b_downright = Button(self.like, image = img_right, bg = '#FCFCFC' ,command = self.pantnext)
		b_downright.place(x = 555, y = 360)
	def button1(self):
		b_back = Button(self.like, image = img_back ,bg = '#FCFCFC', command = self.back_choose)
		b_back.place(x = 50,y = 70)
		b_clothlike = Button(self.like, image=img_like, bg = '#FCFCFC' ,command = self.clothlike)
		b_clothlike.place(x = 950, y = 185)
		b_pantlike = Button(self.like, image=img_like, bg = '#FCFCFC' ,command = self.pantlike)
		b_pantlike.place(x = 950, y = 455)

	#切回至選擇模式頁面
	def back_choose(self):
		self.like.destroy()
		choose(self.master)

	#上一件衣服
	def clothprevious(self):
		if self.countC > 0:
			self.countC = self.countC - 1
		self.show()
	#下一件衣服
	def clothnext(self):
		if self.countC < self.len_cloth - 1: 
			self.countC = self.countC + 1
		self.show()
	#上一件褲子
	def pantprevious(self):
		if self.countP > 0:
			self.countP = self.countP - 1
		self.show()
	#下一件褲子
	def pantnext(self):
		if self.countP < self.len_pant - 1:
			self.countP = self.countP + 1
		self.show()

	#取消衣服收藏
	def clothlike(self):
		file_cloth = open(path + "/alluser/"+str(username)+"/"+str(username)+"_cloth.txt",'r')
		lines = file_cloth.readlines()
		file_clothDel = open(path + "/alluser/"+str(username)+"/"+str(username)+"_cloth.txt",'w')
		d = lines[self.countC]
		for line in lines:
			if d in line:
				continue
			file_clothDel.write(line)
		file_clothDel.close()
		file_clike = open(path +"/alluser/"+str(username)+"/"+str(username)+"_infocloth.txt",'r' )
		lines = file_clike.readlines()
		file_clikeDel = open(path + "/alluser/"+str(username)+"/"+str(username)+"_infocloth.txt",'w')
		for line in lines:
			if line.find(d) > -1:
				continue
			file_clikeDel.write(line)
		file_clikeDel.close()
		self.len_cloth = self.len_cloth - 1
		if self.countC == self.len_cloth:
			self.countC = self.countC - 1
		self.show()
	#取消褲子收藏
	def pantlike(self):
		file_pant = open(path + "/alluser/"+str(username)+"/"+str(username)+"_pant.txt",'r')
		lines = file_pant.readlines()
		file_pantDel = open(path + "/alluser/"+str(username)+"/"+str(username)+"_pant.txt",'w')
		d = lines[self.countP]
		for line in lines:
			if d in line:
				continue
			file_pantDel.write(line)
		file_pantDel.close()
		file_plike = open(path +"/alluser/"+str(username)+"/"+str(username)+"_infopant.txt",'r' )
		lines = file_plike.readlines()
		file_plikeDel = open(path + "/alluser/"+str(username)+"/"+str(username)+"_infopant.txt",'w')
		for line in lines:
			if line.find(d) > -1:
				continue
			file_plikeDel.write(line)
		file_plikeDel.close()
		self.len_pant = self.len_pant - 1
		if self.countP == self.len_pant:
			self.countP = self.countP - 1
		self.show()

#收藏服飾錯誤頁面
class wrong():
	#視窗初始化
	def __init__(self,master):
		self.master = master
		self.wrong = Frame(self.master, bg = '#97CBFF')
		self.wrong.pack(fill = BOTH, expand = YES)
		self.text()
		self.button()
	#顯示文字
	def text(self):
		l_wrongmessage = Label(self.wrong, text = "請至少收藏各一件衣服及褲子", bg = '#FF2D2D', font = ('Arial', 40),fg = 'black')
		l_wrongmessage.place(x = 175, y = 140)
	#顯示按鈕
	def button(self):
		b_backchoose = Button(self.wrong, text = "OK" , bg = '#FCFCFC', font = ('Arial', 50), command = self.know)
		b_backchoose.place(x = 375, y = 250, width = 250, height = 250)
	#切回至選擇模式頁面
	def know(self):
		self.wrong.destroy()
		choose(self.master)

class upload():
	#視窗初始化
	def __init__(self,master):
		self.master = master
		self.upload = Frame(self.master, bg = '#97CBFF')
		self.upload.pack(fill = BOTH , expand = YES)

		global img_person, img_previouspage,img_nextpage
		img_person = Image.open(path + "/alluser/" + str(username)+ ".png")
		img_previouspage = Image.open("icon/previouspage.png").resize((50,50),Image.ANTIALIAS)
		img_previouspage = ImageTk.PhotoImage(img_previouspage)
		img_nextpage = Image.open("icon/nextpage.png").resize((50,50),Image.ANTIALIAS)
		img_nextpage = ImageTk.PhotoImage(img_nextpage)
		
		global face,up,low
		person_img = cv2.imread(path + "/alluser/" + str(username)+ ".png")
		imgray = cv2.cvtColor(person_img, cv2.COLOR_BGR2GRAY)
		ret, thresh = cv2.threshold(imgray, 100, 255,cv2.THRESH_BINARY)
		face, up, low = findPos(thresh,imgray)

		backgroundR= Label(self.upload, text = "",bg = '#FFCCCC', font = ('Arial', 12))
		backgroundR.place(x = 655,y = 1,width = 375,height = 270)
		backgroundB = Label(self.upload, text = "",bg = '#CCEEFF', font=('Arial', 12))
		backgroundB.place(x = 655,y = 271, width = 375, height = 270)
		
		#計算多少件衣服褲子
		global number_c, number_p
		number_c = []
		number_p = []
		path_up_cloth = path + '/up_cloth'
		path_up_pant = path + '/up_pant'

		for root, subFolders, files in os.walk(path_up_cloth):
			for file in files:
				f = os.path.join(root,file)
				number_c .append(f)
				
		for root, subFolders, files in os.walk(path_up_pant):
			for file in files:
				f = os.path.join(root,file)
				number_p.append(f)

		#讀取衣服褲子圖片
		global img_cloth, img_pant
		img_cloth = [0]
		for i in range (1,len(number_c) + 1):
			img_cloth.append('img_cloth' + str(i))
			img_cloth[i] = Image.open(path + "/up_cloth/c" + str(i)+ ".png").resize((75,100),Image.ANTIALIAS)
			img_cloth[i] = ImageTk.PhotoImage(img_cloth[i])
		img_pant = [0]
		for i in range (1,len(number_p) + 1):
			img_pant.append('img_pant' + str(i))
			img_pant[i] = Image.open(path + "/up_pant/p" + str(i)+ ".png").resize((75,100),Image.ANTIALIAS)
			img_pant[i] = ImageTk.PhotoImage(img_pant[i])
			
		global time_clothcount, last_clothcount,time_pantcount, last_pantcount
		time_clothcount = int(len(number_c) / 4) 
		last_clothcount = len(number_c) % 4 
		if last_clothcount != 0:
			time_clothcount = time_clothcount + 1 
			
		time_pantcount = int(len(number_p) / 4) 
		last_pantcount = len(number_p) % 4 
		if last_pantcount != 0:
			time_pantcount = time_pantcount + 1 

		self.upsize = 1
		self.lowsize = 1
		self.show_person()
		self.button()
		self.Uscale()
		self.Lscale()
		
	#顯示人物並貼上衣服
	def show_person(self):
		picturewindow = Label(self.upload)

		global upcountC, upcountP
		cloth = Image.open(path + '/up_cloth/c'+str(upcountC)+'.png')
		pant = Image.open(path + '/up_pant/p'+str(upcountP)+'.png')

		#衣服等比例縮放
		(cloth_row,cloth_cols) = clothResize(cloth,up[2],self.upsize)
		cloth = cloth.resize((cloth_row,cloth_cols))

		#褲子等比例縮放
		(pant_row,pant_cols) = clothResize(pant,low[2],self.lowsize)
		pant = pant.resize((pant_row,pant_cols))

		#找到身體部位
		cloth_pos = (int(face[0]+face[2]/2-cloth_row/2),(face[1]+face[3]))
		pant_pos = (int(face[0]+face[2]/2-pant_row/2),(low[1]))

		#貼上褲子
		image = wear(pant_pos,pant,img_person)
		#貼上衣服
		image = wear(cloth_pos,cloth,image)
		#顯示貼上結果
		imgtk = ImageTk.PhotoImage(image = image)
		picturewindow .imgtk = imgtk
		picturewindow .configure(image = imgtk)
		picturewindow .place(x = 200,y = 30)

	#衣服拉桿軸
	def Uscale(self):
		scale = Scale(self.upload,from_ = 1 , to = 100, length = 150, width = 20 ,bg = '#FCFCFC',orient = 'horizontal' , command = self.set_size)
		scale.place(x = 660 , y = 180)
	#褲子拉桿軸
	def Lscale(self):
		lscale = Scale(self.upload,from_ = 1 , to = 100, length = 150, width = 20 ,bg = '#FCFCFC',orient = 'horizontal' , command = self.set_lowsize)
		lscale.place(x = 660 , y = 450)
	#調整衣服大小
	def set_size(self,val):
		self.upsize = int(val) / 50
		self.show_person()
	#調整褲子大小
	def set_lowsize(self,val):
		self.lowsize = int(val) / 50
		self.show_person()

	#顯示按鈕
	def button(self):
		b_back = Button(self.upload, image = img_back ,bg = '#FCFCFC', command = self.back)
		b_back.place(x = 50,y = 70)
		b_previouspage_c = Button(self.upload,image = img_previouspage, bg = '#FCFCFC', command = self.previouspage_c)
		b_previouspage_c.place(x = 875,y = 180)
		b_nextpage_c = Button(self.upload,image = img_nextpage, bg = '#FCFCFC', command = self.nextpage_c)
		b_nextpage_c.place(x = 950,y = 180)
		b_previouspage_p = Button(self.upload,image = img_previouspage, bg = '#FCFCFC', command = self.previouspage_p)
		b_previouspage_p.place(x = 875,y = 450)
		b_nextpage_p = Button(self.upload,image = img_nextpage, bg = '#FCFCFC', command = self.nextpage_p)
		b_nextpage_p.place(x = 950,y = 450)

		#顯示衣服圖片
		global time_clothcount, last_clothcount,time_pantcount, last_pantcount
		global nowpage_c, nowpage_p
		if nowpage_c <= time_clothcount:
			if nowpage_c == time_clothcount and last_clothcount == 1:
				b_cloth1 = Button(self.upload,image = img_cloth[(nowpage_c - 1) * 4 + 1],command = lambda:self.trycloth((nowpage_c - 1) * 4 + 1))
				b_cloth1.place(x = 660, y = 30)
			elif nowpage_c == time_clothcount and last_clothcount == 2:
				b_cloth1 = Button(self.upload,image = img_cloth[(nowpage_c - 1) * 4 + 1],command = lambda:self.trycloth((nowpage_c - 1) * 4 + 1))
				b_cloth1.place(x = 660, y = 30)
				b_cloth2 = Button(self.upload,image = img_cloth[(nowpage_c - 1) * 4 + 2],command = lambda:self.trycloth((nowpage_c - 1) * 4 + 2))
				b_cloth2.place(x = 750, y = 30)
			elif nowpage_c == time_clothcount and last_clothcount == 3:
				b_cloth1 = Button(self.upload,image = img_cloth[(nowpage_c - 1) * 4 + 1],command = lambda:self.trycloth((nowpage_c - 1) * 4 + 1))
				b_cloth1.place(x = 660, y = 30)
				b_cloth2 = Button(self.upload,image = img_cloth[(nowpage_c - 1) * 4 + 2],command = lambda:self.trycloth((nowpage_c - 1) * 4 + 2))
				b_cloth2.place(x = 750, y = 30)
				b_cloth3 = Button(self.upload,image = img_cloth[(nowpage_c - 1) * 4 + 3],command = lambda:self.trycloth((nowpage_c - 1) * 4 + 3))
				b_cloth3.place(x = 840, y = 30)
			else:
				b_cloth1 = Button(self.upload,image = img_cloth[(nowpage_c - 1) * 4 + 1],command = lambda:self.trycloth((nowpage_c - 1) * 4 + 1))
				b_cloth1.place(x = 660, y = 30)
				b_cloth2 = Button(self.upload,image = img_cloth[(nowpage_c - 1) * 4 + 2],command = lambda:self.trycloth((nowpage_c - 1) * 4 + 2))
				b_cloth2.place(x = 750, y = 30)
				b_cloth3 = Button(self.upload,image = img_cloth[(nowpage_c - 1) * 4 + 3],command = lambda:self.trycloth((nowpage_c - 1) * 4 + 3))
				b_cloth3.place(x = 840, y = 30)
				b_cloth4 = Button(self.upload,image = img_cloth[(nowpage_c - 1) * 4 + 4],command = lambda:self.trycloth((nowpage_c - 1) * 4 + 4))
				b_cloth4.place(x = 930, y = 30)
		#顯示褲子圖片
		if nowpage_p <= time_pantcount:
			if nowpage_p == time_pantcount and last_pantcount == 1:
				b_pant1 = Button(self.upload,image = img_pant[(nowpage_p - 1) * 4 + 1],command = lambda:self.trypant((nowpage_p - 1) * 4 + 1))
				b_pant1.place(x = 660, y = 300)
			elif nowpage_p == time_pantcount and last_pantcount == 2:
				b_pant1 = Button(self.upload,image = img_pant[(nowpage_p - 1) * 4 + 1],command = lambda:self.trypant((nowpage_p - 1) * 4 + 1))
				b_pant1.place(x = 660, y = 300)
				b_pant2 = Button(self.upload,image = img_pant[(nowpage_p - 1) * 4 + 2],command = lambda:self.trypant((nowpage_p - 1) * 4 + 2))
				b_pant2.place(x = 750, y = 300)
			elif nowpage_p == time_pantcount and last_pantcount == 3:
				b_pant1 = Button(self.upload,image = img_pant[(nowpage_p - 1) * 4 + 1],command = lambda:self.trypant((nowpage_p - 1) * 4 + 1))
				b_pant1.place(x = 660, y = 300)
				b_pant2 = Button(self.upload,image = img_pant[(nowpage_p - 1) * 4 + 2],command = lambda:self.trypant((nowpage_p - 1) * 4 + 2))
				b_pant2.place(x = 750, y = 300)
				b_pant3 = Button(self.upload,image = img_pant[(nowpage_p - 1) * 4 + 3],command = lambda:self.trypant((nowpage_p - 1) * 4 + 3))
				b_pant3.place(x = 840, y = 300)
			else:
				b_pant1 = Button(self.upload,image = img_pant[(nowpage_p - 1) * 4 + 1],command = lambda:self.trypant((nowpage_p - 1) * 4 + 1))
				b_pant1.place(x = 660, y = 300)
				b_pant2 = Button(self.upload,image = img_pant[(nowpage_p - 1) * 4 + 2],command = lambda:self.trypant((nowpage_p - 1) * 4 + 2))
				b_pant2.place(x = 750, y = 300)
				b_pant3 = Button(self.upload,image = img_pant[(nowpage_p - 1) * 4 + 3],command = lambda:self.trypant((nowpage_p - 1) * 4 + 3))
				b_pant3.place(x = 840, y = 300)
				b_pant4 = Button(self.upload,image = img_pant[(nowpage_p - 1) * 4 + 4],command = lambda:self.trypant((nowpage_p - 1) * 4 + 4))
				b_pant4.place(x = 930, y = 300)

	#衣服下一頁
	def nextpage_c(self):
		global nowpage_c
		if nowpage_c < time_clothcount:
			nowpage_c = nowpage_c + 1
		self.upload.destroy()
		upload(self.master)
	#衣服上一頁
	def previouspage_c(self):
		global nowpage_c
		if nowpage_c > 1:
			nowpage_c = nowpage_c - 1
		self.upload.destroy()
		upload(self.master)
	#褲子下一頁
	def nextpage_p(self):
		global nowpage_p
		if nowpage_p < time_pantcount:
			nowpage_p = nowpage_p + 1
		self.upload.destroy()
		upload(self.master)
	#褲子上一頁
	def previouspage_p(self):
		global nowpage_p
		if nowpage_p > 1:
			nowpage_p = nowpage_p - 1
		self.upload.destroy()
		upload(self.master)

	#切回至選擇模式頁面
	def back(self):
		self.upload.destroy()
		choose(self.master)

	#判斷衣服格式是否正確
	def trycloth(self,n):
		global upcountC
		try:
			upcountC = n
			self.show_person()
		except:
			upcountC = 1
			self.upload.destroy()
			wrongUP(self.master)
	#判斷褲子格式是否正確
	def trypant(self,n):
		global upcountP
		try:
			upcountP = n
			self.show_person()
		except:
			upcountP = 1
			self.upload.destroy()
			wrongUP(self.master)

#上傳服飾錯誤頁面
class wrongUP():
	#視窗初始化
	def __init__(self,master):
		self.master = master
		self.wrongUP = Frame(self.master, bg = '#97CBFF')
		self.wrongUP.pack(fill = BOTH, expand = YES)
		self.text()
		self.button()
	#顯示文字
	def text(self):
		l_wrongmessage = Label(self.wrongUP, text = "該服飾不符合標準", bg = '#FF2D2D', font = ('Arial', 40),fg = 'black')
		l_wrongmessage.place(x = 300, y = 140)
	#顯示按鈕
	def button(self):
		b_backchoose = Button(self.wrongUP, text = "OK" , bg = '#FCFCFC', font = ('Arial', 50), command = self.know)
		b_backchoose.place(x = 375, y = 250, width = 250, height = 250)
	#切回至選擇模式頁面
	def know(self):
		self.wrongUP.destroy()
		choose(self.master)

#主程式
if __name__ == '__main__':
	#資料庫連接
	dbconnect()
	datacount()
	#觸發閃光燈
	GPIO.setmode(GPIO.BCM)
	GPIO.setwarnings(False)
	GPIO.setup(21,GPIO.OUT)
	#建立頁面
	root = tk.Tk()
	#讀取照片
	img_left = Image.open("icon/left.png").resize((75,75),Image.ANTIALIAS)
	img_left = ImageTk.PhotoImage(img_left)
	img_right = Image.open("icon/right.png").resize((75,75),Image.ANTIALIAS)
	img_right = ImageTk.PhotoImage(img_right)
	img_back = Image.open("icon/back.png").resize((100,100),Image.ANTIALIAS)
	img_back = ImageTk.PhotoImage(img_back)
	img_boy = Image.open("icon/boy.png").resize((100,100),Image.ANTIALIAS)
	img_boy = ImageTk.PhotoImage(img_boy)
	img_girl = Image.open("icon/girl.png").resize((100,100),Image.ANTIALIAS)
	img_girl = ImageTk.PhotoImage(img_girl)
	img_like = Image.open("icon/like.png").resize((50,50),Image.ANTIALIAS)
	img_like = ImageTk.PhotoImage(img_like)
	img_nolike = Image.open("icon/nolike.png").resize((50,50),Image.ANTIALIAS)
	img_nolike = ImageTk.PhotoImage(img_nolike)

	global path
	path = os.getcwd()

	global usercount_file
	usercount_file = open(path + "/alluser/usercount.txt",'a')
	with open(path + "/alluser/usercount.txt",'r') as f:
		data = f.read()
	usercount_file.close()

	global usercount
	if data == '\n' or data == '':
		usercount = 0
	else:
		usercount = int(data)

	global nowpage
	nowpage = 1

	global username
	username = ''

	global nowpage_c,nowpage_p
	nowpage_c = 1
	nowpage_p = 1
	
	global upcountC, upcountP
	upcountC = 1
	upcountP = 1

	basedesk(root)
	cap = cv2.VideoCapture(0)
	root.mainloop()