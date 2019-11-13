import sys
import os
import time
import matplotlib.pyplot as mpl
import traceback
from Phidget22.Devices.VoltageRatioInput import *
from Phidget22.PhidgetException import *
from Phidget22.Phidget import *
from Phidget22.Net import *
from datetime import datetime
from textwrap import wrap
import matplotlib.dates as mdates
from tkinter import * 
import threading


try:
    from PhidgetHelperFunctions import *
except ImportError:
    sys.stderr.write("\nCould not find PhidgetHelperFunctions. Either add PhdiegtHelperFunctions.py to your project folder "
                      "or remove the import from your project.")
    sys.stderr.write("\nPress ENTER to end program.")
    readin = sys.stdin.readline()
    sys.exit()

data= [0,0,0,0,0,0,0,0,0,0,0,0]
dvs = {'513063':0,'514065':1,'514022':2} #l ordre des capteurs 
nomfich='fic.txt'
ok =False

def proj_grav (n,b,c,d):     #Méthode qui permet de calculer la projection du centre du gravité avec en entrée les valeurs lues sur les 4 capteurs verticaux
	proj_grav.x= (((((b*1000)-0.0242)/(3*10**-5))*1)+((((c*1000)-0.024)/(3*10**-5))*1))/((((n*1000)-0.0133)/(3*10**-5))+(((b*1000)-0.0242)/(3*10**-5))+(((c*1000)-0.024)/(3*10**-5))+(((d*1000)-0.0295)/(3*10**-5)))
	proj_grav.y= (((((d*1000)-0.024)/(3*10**-5))*1)+((((c*1000)-0.0295)/(3*10**-5))*1))/((((n*1000)-0.0133)/(3*10**-5))+(((b*1000)-0.0242)/(3*10**-5))+(((c*1000)-0.024)/(3*10**-5))+(((d*1000)-0.0295)/(3*10**-5)))
def moment_grav(x,y,b0,b1,b2,b3,r0,r1,r2,r3):
    
	r00=(-((((r0*1000)+(0.0359))/(-0.00002))*9.81*0.001))
	r11=(((((r1*1000)-(0.0265))/(-0.00005))*9.81*0.001))
	r22=(((((r2*1000)+(0.0044))/(-0.00002))*9.81*0.001))
	r33=(-((((r3*1000)-(0.0432))/(0.0002))*9.81*0.001))
    
	b00=(((((b0*1000)-(0.0415))/(0.0002))*9.81*0.001))
	b11=(-((((b1*1000)-(0.0801))/(0.00009))*9.81*0.001))
	b22=(-((((b2*1000)-(0.1075))/(0.0002))*9.81*0.001))
	b33=(((((b3*1000)+(0.0629))/(0.0002))*9.81*0.001))
    
    
	moment_0b=np.cross([317-x,57-y,0],[0,b00,0])
	moment_1b=np.cross([83-x,57-y,0],[0,b11,0])
	moment_2b=np.cross([83-x,343-y,0],[0,b22,0])
	moment_3b=np.cross([317-x,343-y,0],[0,b33,0])

	moment_0r=np.cross([57-x,317-y,0],[r00,0,0])
	moment_1r=np.cross([57-x,83-y,0],[r11,0,0])
	moment_2r=np.cross([347-x,83-y,0],[r22,0,0])
	moment_3r=np.cross([347-x,317-y,0],[r33,0,0])
    
    #print(moment_0b)
    #print(moment_0r)
    
    #print(moment_1b)
    #print(moment_1r)
    
    #print(moment_2b)
    #print(moment_2r)
    
    #print(moment_3b)
    #print(str(moment_3r)+'\n')
    
	moment_grav.t=moment_0b+moment_1b+moment_2b+moment_3b+moment_0r+moment_1r+moment_2r+moment_3r
	

def capture():
	global data,ok,nomfich
	date_essai=datetime.now()
	nomfich= 'Essai_réalisé_le_'+ str(date_essai.year)+ '_' + str(date_essai.month)+'_'+str(date_essai.day)+'_'+str(date_essai.hour)+'h_'+str(date_essai.minute)+'m_'+str(date_essai.second)+'s.txt' #On suvegarde le fichier avec la date de l'eesai
	start=now=time.time()
	while  ok:
		fic = open(nomfich , "a")
		f1=((((((data[11]*1000)+(0.0629))/0.0002)*9.81*0.001)-7))-(((((data[10]*1000)-(0.1075))/0.0002)*9.81*0.001)-20)+((((((data[8]*1000)-(0.0415))/(0.0002))*9.81*0.001)-17))-(((((data[9]*1000)-(0.0801))/0.00009)*9.81*0.001)-5)
		f2=((((((data[5]*1000)-(0.0265))/(-0.00005))*9.81*0.001)-25))-(((((data[4]*1000)+(0.0359))/(-0.00002))*9.81*0.001)-11)+((((((data[11]*1000)+(0.0629))/0.0002)*9.81*0.001)-7))-(((((data[10]*1000)-(0.0766))/0.0002)*9.81*0.001)-20)
		proj_grav(data[0],data[1],data[2],data[3])
		proj_sur_x=proj_grav.x
		proj_sur_y=proj_grav.y
		fic.write(str(now-start)+";"+";".join(str(k) for k in data)+";"+str(f1)+";"+str(f2)+";"+str(proj_sur_x)+";"+str(proj_sur_y)+"\n")
		time.sleep(0.01)
		now=time.time()
        
		
def onVoltageRatioChangeHandler(self, voltageRatio):
	global dvs, data
	n= dvs[str(self.getDeviceSerialNumber())]*4 +(self.getChannel())
	data[n]=voltageRatio


def dem():
    print("demarrage \n")
    global aff, ok
    aff = 1
    ok=True
    dv = [513063,514065,514022]
    #parcourt les devices, pour que chacun demarre un channel
    for k in range(0,3):
        for i in range(0,4):
            ch = VoltageRatioInput()
            ch.setDeviceSerialNumber(dv[k])
            ch.setChannel(i)
            #ch.setDataInterval(8)
            ch.setOnVoltageRatioChangeHandler(onVoltageRatioChangeHandler)
            #lorsque la valeur change,onVoltageRatioChangeHandler va changer aussi.
            ch.openWaitForAttachment(5000)
def arreter():
	print("arret \n")
	global ok
	ok=False

def demcap():
	print("capture \n")
	x=threading.Thread(target=capture)
	x.start()

def dessine():
	fl = open(nomfich,'r')
	lignes = fl.readlines()# il recupere toute les lignes
	fl.close
	llbs = []
	dtf1=[]
	dtf2=[]
	dtfxproj=[]
	dtfyproj=[]
	moment=[]
	for ligne in lignes:
		dts = ligne.split(';')#on separe par un point virgule(creer un tableau qui va creer 3 données
		llbs.append(float(dts[0]))#on formate la date
		dtf1.append(float(dts[13]))
		dtf2.append(float(dts[14]))
		dtfxproj.append(float(dts[15]))
		dtfyproj.append(float(dts[16]))
		#moment.append(float(dts[17]))
		
	fig=mpl.figure()
    
	mpl.subplot(411)
	mpl.plot(dtfxproj,dtfyproj,'r+')
	mpl.grid(True)
	mpl.title('Porj_y en fonction de proj_y')
	mpl.xlabel('Projection selon x')
	mpl.ylabel('Projection selon y')
	mpl.axis([0,1,0,1])
    
    #mpl.subplot(412)
    #mpl.plot(llbs,dtfxproj,'r+')
    #mpl.grid(True)
    #mpl.title('Proj_x en fonction du temps')
    #mpl.xlabel('Projection selon x')
    #mpl.ylabel('Temps')
    
	#mpl.subplot(413)
	#mpl.plot(llbs,dtfyproj,'r+')
	#mpl.grid(True)
	#mpl.title('Proj_y en fonction du temps')
	#mpl.xlabel('Projection selon x')
	#mpl.ylabel('Temps')
    
	mpl.subplot(412)
	mpl.plot(llbs, dtf1, 'go-', label='line 1', linewidth=2,marker='o',markersize=1)#data contient les valeurs de l'ordonnée
	mpl.plot(llbs, dtf2, 'bo-', label='line 1', linewidth=2,marker='o',markersize=1)
	mpl.grid(True)
	
	#mpl.subplot(413)
	#mpl.plot(llbs, moment)
	#mpl.grid(True)
	#mpl.title('moment')
	#mpl.xlabel('moment')
	#mpl.ylabel('Temps')
    
	mpl.show()
        
    
        

root = Tk()
#crée une fenetre

root.title('Phidget')
lb=Label(root,text="Fichier")

qa = Button(root, text='Demarrer', command=dem)
qa.grid(row=1,column=0)
qc = Button(root, text='Capturer', command=demcap)
qc.grid(row=1,column=1)
qs = Button(root, text='Arreter', command=arreter)
qs.grid(row=1,column=2)
qd = Button(root, text='Dessiner', command=dessine)
qd.grid(row=1,column=3)
qb = Button(root, text='Quitter', command=root.quit)
qb.grid(row=1,column=4)
root.mainloop()

