from Tkinter import *
from tkFileDialog import *
from PIL import Image
from PIL import ImageTk
import Desktop_Head_Arm_Serial
import Desktop_Head_Arm_OpenCV
import math
import time


YELLOWOBJECTS = [15,90,90,40,255,255]



class Application(Frame):
    def __init__(self, master=None):
        Frame.__init__(self, master)
        self.grid()
        self.createWidgets()
        self.UpdateHandSwitch()
        self.Updateservopositions()

      

    def createWidgets(self):

        self.CamImage = Canvas(self, width=384, height=288,bg = "black")
        self.CamImage.grid(row = 1, column = 0, rowspan = 3)

        self.CamImage2 = Canvas(self, width=384, height=288,bg = "black")
        self.CamImage2.grid(row = 4, column = 0, rowspan = 3)

        self.Capturebutton = Button(self, text="Capture", command = self.CaptureImage)
        self.Capturebutton.grid(row = 7, column = 0)

        self.commandEntry= Entry(self)
        self.commandEntry.grid(row = 8, column = 0)
        self.commandEntry.bind('<Return>', self.sendCommand)

        self.send = Button(self, text="Send")
        self.send.bind('<Button-1>', self.sendCommand)
        self.send.grid(row = 8, column = 1)

        self.servocheckstatus = IntVar()
        self.ServoCheck = Checkbutton(self, text="Servos enabled",variable=self.servocheckstatus,command=self.servopower)
        self.ServoCheck.grid(row = 0, column = 0)

        self.livedatastatus = IntVar()
        self.LiveDataCheck = Checkbutton(self, text="Live Data",variable=self.livedatastatus,command=self.LiveData)
        self.LiveDataCheck.grid(row = 0, column = 1)

        self.RunSeq = Button(self, text="Run")
        self.RunSeq.bind('<Button-1>', self.RunSequence)
        self.RunSeq.grid(row = 0, column = 2)

        self.Facedetectionstatus = IntVar()
        self.Facedetectioncheck = Checkbutton(self, text="Face Detection",variable=self.Facedetectionstatus,command=self.FaceDetection)
        self.Facedetectioncheck.grid(row = 0, column = 3)
  
        self.HSCanvas = Canvas(self, bg="white", width=100, height=100)
        self.HSCanvas.grid(row = 5, column = 3)
        self.HSCanvas.create_oval(10, 10, 90, 90, width=2, fill='green')



        self.Homebutton = Button(self, text="Home", command = self.Home)
        self.Homebutton.grid(row = 8, column = 5)

        self.QUIT = Button(self, text="QUIT", fg="red",command=root.destroy)
        self.QUIT.grid(row = 8, column = 6)




        ###################################################################
        # Sliders for Head controls                   
        ###################################################################

        self.RollSlider = Scale(self, from_=-90, to=90, orient= VERTICAL)
        self.RollSlider.grid(row = 3, column = 2)
        self.RollSlider.bind('<ButtonRelease-1>', self.sendHeadSliders)

        self.PitchSlider = Scale(self, from_=-90, to=90, orient= VERTICAL)
        self.PitchSlider.grid(row = 3, column = 3)
        self.PitchSlider.bind('<ButtonRelease-1>', self.sendHeadSliders)

        self.YawSlider = Scale(self, from_=-90, to=90, orient= VERTICAL)
        self.YawSlider.grid(row = 3, column = 4)
        self.YawSlider.bind('<ButtonRelease-1>', self.sendHeadSliders)

        ###################################################################
        # Entry boxes for Head servo positions                  
        ###################################################################

        self.RollEntry= Entry(self, width = 4)
        self.RollEntry.grid(row = 4, column = 2)

        self.PitchEntry= Entry(self, width = 4)
        self.PitchEntry.grid(row = 4, column = 3)

        self.YawEntry= Entry(self, width = 4)
        self.YawEntry.grid(row = 4, column = 4)

        ###################################################################
        # Sliders for Head controls                   
        ###################################################################

        self.RotateSlider = Scale(self, from_=-90, to=90, orient= VERTICAL)
        self.RotateSlider.grid(row = 3, column = 6)
        self.RotateSlider.bind('<ButtonRelease-1>', self.sendArmSliders)

        self.LowerSlider = Scale(self, from_=0, to=90, orient= VERTICAL)
        self.LowerSlider.grid(row = 3, column = 7)
        self.LowerSlider.bind('<ButtonRelease-1>', self.sendArmSliders)

        self.ElbowSlider = Scale(self, from_=-70, to=120, orient= VERTICAL)
        self.ElbowSlider.set(-70)
        self.ElbowSlider.grid(row = 3, column = 8)
        self.ElbowSlider.bind('<ButtonRelease-1>', self.sendArmSliders)

        ###################################################################
        # Entry boxes for Arm servo positions                  
        ###################################################################

        self.RotateEntry= Entry(self, width = 4)
        self.RotateEntry.grid(row = 4, column = 6)

        self.LowerEntry= Entry(self, width = 4)
        self.LowerEntry.grid(row = 4, column = 7)

        self.ElbowEntry= Entry(self, width = 4)
        self.ElbowEntry.grid(row = 4, column = 8)

 
    def LiveData(self):
        self.Updateservopositions()




    def servopower(self):
        print "Servo Power is", self.servocheckstatus.get()
        Desktop_Head_Arm_Serial.sendcommand('S' + str(self.servocheckstatus.get()))
            

    def sendCommand(self,event):
        print "Sending Command", self.commandEntry.get()
        Desktop_Head_Arm_Serial.sendcommand(self.commandEntry.get())

    def Home(self):
        #print "Sending Command", 'H0X0Y0Z0 A0R0L0E0'
        #Desktop_Head_Arm_Serial.sendcommand('H0X0Y0Z0 A0R0L0E0')
        self.RollSlider.set(0)
        self.PitchSlider.set(0)
        self.YawSlider.set(0)

        self.RotateSlider.set(0)
        self.LowerSlider.set(0)
        self.ElbowSlider.set(-70)

        self.sendHeadSliders(self)
        self.sendArmSliders(self)


    def sendHeadSliders(self,event):
        print "Sending Command", 'H0R'+str(self.RollSlider.get())+'P'+str(self.PitchSlider.get())+'Y'+str(self.YawSlider.get())
        Desktop_Head_Arm_Serial.sendcommand('H0R'+str(self.RollSlider.get())+'P'+str(self.PitchSlider.get())+'Y'+str(self.YawSlider.get()))
        
    def sendArmSliders(self,event):
        print "Sending Command", 'A0B'+str(self.RotateSlider.get())+'L'+str(self.LowerSlider.get())+'U'+str(self.ElbowSlider.get())
        Desktop_Head_Arm_Serial.sendcommand('A0B'+str(self.RotateSlider.get())+'L'+str(self.LowerSlider.get())+'U'+str(self.ElbowSlider.get()))       

   
    def CaptureImage(self):
        #self.OpenCVImage = Desktop_Head_Arm_OpenCV.ReturnFrameRGB()
        balldata, self.OpenCVImage, imgthreshed = Desktop_Head_Arm_OpenCV.FindBall(YELLOWOBJECTS)
        print balldata
        self.OpenCVImage = Image.fromarray(self.OpenCVImage)
        self.OpenCVImage = self.OpenCVImage.resize((384, 288), Image.ANTIALIAS)
	self.OpenCVImage = ImageTk.PhotoImage(self.OpenCVImage)
        self.CamImage.create_image(0,0, anchor=NW, image=self.OpenCVImage)

        imgthreshed = Image.fromarray(imgthreshed)
        imgthreshed = imgthreshed.resize((384, 288), Image.ANTIALIAS)
	imgthreshed = ImageTk.PhotoImage(imgthreshed)
        self.CamImage2.create_image(0,0, anchor=NW, image=imgthreshed)


    def UpdateHandSwitch(self):
        Desktop_Head_Arm_Serial.sendcommand('A4')
        Handswitchstatus = int(Desktop_Head_Arm_Serial.readserial())
        

        if Handswitchstatus == 0:
            print 'Hand triggered'
            self.HSCanvas.create_oval(10, 10, 90, 90, width=2, fill='red')
        else:
            self.HSCanvas.create_oval(10, 10, 90, 90, width=2, fill='green')
        root.update_idletasks()
        self.after(100, self.UpdateHandSwitch)
        
    def Updateservopositions(self):
        Desktop_Head_Arm_Serial.sendcommand('H1')
        Rollservopos = int(Desktop_Head_Arm_Serial.readserial())
        self.RollEntry.delete(0, END)
        self.RollEntry.insert(0, Rollservopos)

        Desktop_Head_Arm_Serial.sendcommand('H2')
        Pitchservopos = int(Desktop_Head_Arm_Serial.readserial())
        self.PitchEntry.delete(0, END)
        self.PitchEntry.insert(0, Pitchservopos)

        Desktop_Head_Arm_Serial.sendcommand('H3')
        Yawservopos = int(Desktop_Head_Arm_Serial.readserial())
        self.YawEntry.delete(0, END)
        self.YawEntry.insert(0, Yawservopos)



        Desktop_Head_Arm_Serial.sendcommand('A1')
        Rotateservopos = int(Desktop_Head_Arm_Serial.readserial())
        self.RotateEntry.delete(0, END)
        self.RotateEntry.insert(0, Rotateservopos)

        Desktop_Head_Arm_Serial.sendcommand('A2')
        Lowerservopos = int(Desktop_Head_Arm_Serial.readserial())
        self.LowerEntry.delete(0, END)
        self.LowerEntry.insert(0, Lowerservopos)

        Desktop_Head_Arm_Serial.sendcommand('A3')
        Elbowservopos = int(Desktop_Head_Arm_Serial.readserial())
        self.ElbowEntry.delete(0, END)
        self.ElbowEntry.insert(0, Elbowservopos)


        if self.livedatastatus.get() == 1:
            self.after(100, self.Updateservopositions)  


    def RunSequence(self,event):
        print "Running Sequence"
        
        """
        #Head shake
        Desktop_Head_Arm_Serial.sendcommand('F3E0')
        Desktop_Head_Arm_Serial.sendcommand('H0Y20')
        time.sleep(0.5)
        Desktop_Head_Arm_Serial.sendcommand('H0Y-20')
        time.sleep(0.5)
        Desktop_Head_Arm_Serial.sendcommand('H0Y20')
        time.sleep(0.5)
        Desktop_Head_Arm_Serial.sendcommand('H0Y-20')
        time.sleep(0.5)
        Desktop_Head_Arm_Serial.sendcommand('H0Y20')
        time.sleep(0.5)
        Desktop_Head_Arm_Serial.sendcommand('H0Y-20')
        time.sleep(0.5)
        Desktop_Head_Arm_Serial.sendcommand('H0Y20')
        
          
        #Head nod
        Desktop_Head_Arm_Serial.sendcommand('H0P20')
        time.sleep(0.5)
        Desktop_Head_Arm_Serial.sendcommand('H0P-20')
        time.sleep(0.5)
        Desktop_Head_Arm_Serial.sendcommand('H0P20')
        time.sleep(0.5)
        Desktop_Head_Arm_Serial.sendcommand('H0P-20')
        time.sleep(0.5)
        Desktop_Head_Arm_Serial.sendcommand('H0P20')
        time.sleep(0.5)
        Desktop_Head_Arm_Serial.sendcommand('H0P-20')
        time.sleep(0.5)
        Desktop_Head_Arm_Serial.sendcommand('H0P20')
        
        #Repeatability test
        Desktop_Head_Arm_Serial.sendcommand('H0R0P-19Y25')
        time.sleep(1)
        Desktop_Head_Arm_Serial.sendcommand('A0B31L62U-28')
        time.sleep(3)
        Desktop_Head_Arm_Serial.sendcommand('A0B21L54U8')
        time.sleep(3)
        Desktop_Head_Arm_Serial.sendcommand('A0B20L79U28')
        time.sleep(3)
        Desktop_Head_Arm_Serial.sendcommand('A0B-25L45U-3')
        time.sleep(3)
        Desktop_Head_Arm_Serial.sendcommand('A0B-25L77U23')
        time.sleep(3)
        Desktop_Head_Arm_Serial.sendcommand('A0B-41L24U-57')
        time.sleep(3)
        Desktop_Head_Arm_Serial.sendcommand('A0B-41L60U-33')
        time.sleep(3)
        Desktop_Head_Arm_Serial.sendcommand('A0B-2L19U-75')
        time.sleep(3)
        Desktop_Head_Arm_Serial.sendcommand('A0B-2L60U-63')
        time.sleep(3)
        Desktop_Head_Arm_Serial.sendcommand('A0B0L0U-75')
        time.sleep(3)
        """

        Desktop_Head_Arm_Serial.sendcommand('H0R0P28Y-28')
        time.sleep(1.5)
        Desktop_Head_Arm_Serial.sendcommand('F0E1')
        time.sleep(1.5)
        Desktop_Head_Arm_Serial.sendcommand('F0E2')
        time.sleep(1.5)
        Desktop_Head_Arm_Serial.sendcommand('F0E1')
        time.sleep(1.5)
        Desktop_Head_Arm_Serial.sendcommand('F0E0')
        time.sleep(1.5)
        Desktop_Head_Arm_Serial.sendcommand('H0R-26P28Y-38')
        time.sleep(1.5)
        Desktop_Head_Arm_Serial.sendcommand('F1E0')
        time.sleep(1)
        Desktop_Head_Arm_Serial.sendcommand('F0E0')
        time.sleep(1.5)
        Desktop_Head_Arm_Serial.sendcommand('F1E0')
        time.sleep(1)
        Desktop_Head_Arm_Serial.sendcommand('F0E0')
        time.sleep(1.5)
        Desktop_Head_Arm_Serial.sendcommand('H0R0P0Y0')
        time.sleep(1.5)


    def FaceDetection(self):
        print 'Face detection'
        if self.Facedetectionstatus.get() == 1:
            self.after(100, self.FaceDetection) 



root = Tk()
root.title("Desktop Head and Arm: Big Face Robotics")
app = Application(master=root)
app.mainloop()
