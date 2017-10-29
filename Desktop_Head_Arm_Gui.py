from Tkinter import *
from tkFileDialog import *
from PIL import Image
from PIL import ImageTk
import Desktop_Head_Arm_Serial
import Desktop_Head_Arm_OpenCV
import math
import time


########################################################################################
#
# Opencv threshold values
#
########################################################################################

YELLOWOBJECTS = [16,60,150,40,255,255]
BLUEOBJECTS = [100,145,130,130,255,255]
ORANGEOBJECTS = [5,170,170,15,255,255]
GREENOBJECTS = [55,70,80,90,150,255]


CamCentreX = 320
CamCentreY = 240






class Application(Frame):
    def __init__(self, master=None):
        Frame.__init__(self, master)
        self.grid()
        self.createWidgets()




        self.UpdateHandSwitch()
        self.Updateservopositions()
        self.FaceDetected = False
        self.EyeStatus = 0

      

    def createWidgets(self):

        VisionFrame = LabelFrame(self, bg="royal blue", text = "Vision")
        VisionFrame.grid(row = 0, column = 0, rowspan = 2, sticky = 'NESW') 

        ManualFrame = LabelFrame(self, bg="royal blue", text = "Manual")
        ManualFrame.grid(row = 0, column = 1, sticky = 'NESW') 

        PowerFrame = LabelFrame(self, bg="royal blue", text = "Power")
        PowerFrame.grid(row = 2, column = 0, sticky = 'NESW')

        SequenceFrame = LabelFrame(self, bg="royal blue", text = "Sequences")
        SequenceFrame.grid(row = 1, column = 1, rowspan = 2,sticky = 'NESW')  

        VisualisationFrame = LabelFrame(self, bg="royal blue", text = "Visualisation")
        VisualisationFrame.grid(row = 0, column = 2, rowspan = 3, sticky = 'NESW')       
     





        self.CamImage = Canvas(VisionFrame, width=480, height=360,bg = "black")
        self.CamImage.grid(row = 0, column = 0, columnspan = 4)

        self.CamImage2 = Canvas(VisionFrame, width=480, height=360,bg = "black")
        self.CamImage2.grid(row = 1, column = 0, columnspan = 4)

        self.Capturebutton = Button(VisionFrame, text="Capture", bg="royal blue", activebackground = "royal blue", highlightthickness = 0, command = self.CaptureImage)
        self.Capturebutton.grid(row = 2, column = 0)

        self.Facedetectionstatus = IntVar()
        self.Facedetectioncheck = Checkbutton(VisionFrame, text="Face Detection",variable=self.Facedetectionstatus, bg="royal blue", activebackground = "royal blue", highlightthickness = 0, command=self.FaceDetection)
        self.Facedetectioncheck.grid(row = 2, column = 1)
  
        self.Colourdetectionstatus = IntVar()
        self.Colourdetectioncheck = Checkbutton(VisionFrame, text="Colour Detection",variable=self.Colourdetectionstatus, bg="royal blue", activebackground = "royal blue", highlightthickness = 0, command=self.ColourDetection)
        self.Colourdetectioncheck.grid(row = 2, column = 2)

        self.Colourtrackingstatus = IntVar()
        self.Colourtrackingcheck = Checkbutton(VisionFrame, text="Colour Tracking", bg="royal blue", activebackground = "royal blue", highlightthickness = 0, variable=self.Colourtrackingstatus)
        self.Colourtrackingcheck.grid(row = 2, column = 3)






        self.commandEntry= Entry(ManualFrame)
        self.commandEntry.grid(row = 2, column = 0, columnspan = 3)
        self.commandEntry.bind('<Return>', self.sendCommand)

        self.send = Button(ManualFrame, text="Send", bg="royal blue", activebackground = "royal blue", highlightthickness = 0)
        self.send.bind('<Button-1>', self.sendCommand)
        self.send.grid(row = 2, column = 4)

        self.livedatastatus = IntVar()
        self.LiveDataCheck = Checkbutton(ManualFrame, text="Live Data", bg="royal blue", activebackground = "royal blue", highlightthickness = 0, variable=self.livedatastatus,command=self.LiveData)
        self.LiveDataCheck.grid(row = 3, column = 0, columnspan = 2)

        self.HSCanvas = Canvas(ManualFrame, bg="royal blue",  highlightthickness = 0, width=100, height=100)
        self.HSCanvas.grid(row = 4, column = 0, columnspan = 3)
        self.HSCanvas.create_oval(10, 10, 90, 90, width=2, fill='green')

        self.Homebutton = Button(ManualFrame, text="Home", bg="royal blue", activebackground = "royal blue", highlightthickness = 0, command = self.Home)
        self.Homebutton.grid(row = 3, column = 4)



        ###################################################################
        # Sliders for Head controls                   
        ###################################################################

        self.RollSlider = Scale(ManualFrame, from_=-90, to=90, bg="royal blue", activebackground = "royal blue", highlightthickness = 0, orient= VERTICAL)
        self.RollSlider.grid(row = 0, column = 0)
        self.RollSlider.bind('<ButtonRelease-1>', self.sendHeadSliders)

        self.PitchSlider = Scale(ManualFrame, from_=-90, to=90, bg="royal blue", activebackground = "royal blue", highlightthickness = 0, orient= VERTICAL)
        self.PitchSlider.grid(row = 0, column = 1)
        self.PitchSlider.bind('<ButtonRelease-1>', self.sendHeadSliders)

        self.YawSlider = Scale(ManualFrame, from_=-90, to=90, bg="royal blue", activebackground = "royal blue", highlightthickness = 0, orient= VERTICAL)
        self.YawSlider.grid(row = 0, column = 2)
        self.YawSlider.bind('<ButtonRelease-1>', self.sendHeadSliders)

        ###################################################################
        # Entry boxes for Head servo positions                  
        ###################################################################

        self.RollEntry= Entry(ManualFrame, bg="royal blue", highlightthickness = 0, width = 4)
        self.RollEntry.grid(row = 1, column = 0)

        self.PitchEntry= Entry(ManualFrame, bg="royal blue", highlightthickness = 0, width = 4)
        self.PitchEntry.grid(row = 1, column = 1)

        self.YawEntry= Entry(ManualFrame, bg="royal blue", highlightthickness = 0, width = 4)
        self.YawEntry.grid(row = 1, column = 2)

        ###################################################################
        # Sliders for Head controls                   
        ###################################################################

        self.RotateSlider = Scale(ManualFrame, from_=-90, to=90, bg="royal blue", activebackground = "royal blue", highlightthickness = 0, orient= VERTICAL)
        self.RotateSlider.grid(row = 0, column = 3)
        self.RotateSlider.bind('<ButtonRelease-1>', self.sendArmSliders)

        self.LowerSlider = Scale(ManualFrame, from_=0, to=90, bg="royal blue", activebackground = "royal blue", highlightthickness = 0, orient= VERTICAL)
        self.LowerSlider.grid(row = 0, column = 4)
        self.LowerSlider.bind('<ButtonRelease-1>', self.sendArmSliders)

        self.ElbowSlider = Scale(ManualFrame, from_=-70, to=120, bg="royal blue", activebackground = "royal blue", highlightthickness = 0, orient= VERTICAL)
        self.ElbowSlider.set(-70)
        self.ElbowSlider.grid(row = 0, column = 5)
        self.ElbowSlider.bind('<ButtonRelease-1>', self.sendArmSliders)

        ###################################################################
        # Entry boxes for Arm servo positions                  
        ###################################################################

        self.RotateEntry= Entry(ManualFrame, bg="royal blue", highlightthickness = 0, width = 4)
        self.RotateEntry.grid(row = 1, column = 3)

        self.LowerEntry= Entry(ManualFrame, bg="royal blue", highlightthickness = 0, width = 4)
        self.LowerEntry.grid(row = 1, column = 4)

        self.ElbowEntry= Entry(ManualFrame, bg="royal blue", highlightthickness = 0, width = 4)
        self.ElbowEntry.grid(row = 1, column = 5)







        self.headservocheckstatus = IntVar()
        self.headServoCheck = Checkbutton(PowerFrame, text="Head Servos enabled", bg="royal blue", activebackground = "royal blue", highlightthickness = 0, variable=self.headservocheckstatus, command=self.headservopower)
        self.headServoCheck.grid(row = 0, column = 0)

        self.armservocheckstatus = IntVar()
        self.armServoCheck = Checkbutton(PowerFrame, text="Arm Servos enabled", bg="royal blue", activebackground = "royal blue", highlightthickness = 0, variable=self.armservocheckstatus, command=self.armservopower)
        self.armServoCheck.grid(row = 0, column = 1)





        self.SeqVar = StringVar()
        self.SeqVar.set("None") # initial value
        self.SeqOption = OptionMenu(SequenceFrame, self.SeqVar, "None", "Shake Head", "Nod Head")
        self.SeqOption.grid(row = 0, column = 0)

        self.RunSeq = Button(SequenceFrame, bg="royal blue", activebackground = "royal blue", highlightthickness = 0, text="Run Sequence")
        self.RunSeq.bind('<Button-1>', self.RunSequence)
        self.RunSeq.grid(row = 0, column = 1)

        


        self.NNCanvas1 = Canvas(VisualisationFrame, bg="black",  highlightthickness = 0, width=300, height=300)
        self.NNCanvas1.grid(row = 0, column = 0)

        self.NNCanvas2 = Canvas(VisualisationFrame, bg="black",  highlightthickness = 0, width=300, height=300)
        self.NNCanvas2.grid(row = 1, column = 0)


  

 
    def LiveData(self):
        self.Updateservopositions()




    def headservopower(self):
        print "Head Servo Power is", self.headservocheckstatus.get()
        if self.headservocheckstatus.get() is 0:
            Desktop_Head_Arm_Serial.sendcommand('S2')
        else:
            Desktop_Head_Arm_Serial.sendcommand('S0')

    def armservopower(self):
        print "Arm Servo Power is", self.armservocheckstatus.get()
        if self.armservocheckstatus.get() is 0:
            Desktop_Head_Arm_Serial.sendcommand('S3')
        else:
            Desktop_Head_Arm_Serial.sendcommand('S1')




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
        self.OpenCVImage = self.OpenCVImage.resize((480, 360), Image.ANTIALIAS)
	self.OpenCVImage = ImageTk.PhotoImage(self.OpenCVImage)
        self.CamImage.create_image(0,0, anchor=NW, image=self.OpenCVImage)

        imgthreshed = Image.fromarray(imgthreshed)
        imgthreshed = imgthreshed.resize((480, 360), Image.ANTIALIAS)
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
        if self.SeqVar.get() == 'Shake Head':
            print 'Shake Head'
            self.HeadShake()
        elif self.SeqVar.get() == 'Nod Head':
            print 'Nod Head'
            self.HeadNod()
        
    def HeadShake(self):
        #Head shake
        Desktop_Head_Arm_Serial.sendcommand('F3E0')
        Desktop_Head_Arm_Serial.sendcommand('H0R0P0Y20')
        time.sleep(0.5)
        Desktop_Head_Arm_Serial.sendcommand('H0R0P0Y-20')
        time.sleep(0.5)
        Desktop_Head_Arm_Serial.sendcommand('H0R0P0Y20')
        time.sleep(0.5)
        Desktop_Head_Arm_Serial.sendcommand('H0R0P0Y-20')
        time.sleep(0.5)
        Desktop_Head_Arm_Serial.sendcommand('H0R0P0Y20')
        time.sleep(0.5)
        Desktop_Head_Arm_Serial.sendcommand('H0R0P0Y-20')
        time.sleep(0.5)
        Desktop_Head_Arm_Serial.sendcommand('H0R0P0Y20')
        
    def HeadNod(self):         
        #Head nod
        Desktop_Head_Arm_Serial.sendcommand('F0E0')
        Desktop_Head_Arm_Serial.sendcommand('H0R0P20Y0')
        time.sleep(0.5)
        Desktop_Head_Arm_Serial.sendcommand('H0R0P-20')
        time.sleep(0.5)
        Desktop_Head_Arm_Serial.sendcommand('H0R0P20')
        time.sleep(0.5)
        Desktop_Head_Arm_Serial.sendcommand('H0R0P-20')
        time.sleep(0.5)
        Desktop_Head_Arm_Serial.sendcommand('H0R0P20')
        time.sleep(0.5)
        Desktop_Head_Arm_Serial.sendcommand('H0R0P-20')
        time.sleep(0.5)
        Desktop_Head_Arm_Serial.sendcommand('H0R0P20')
       


    def FaceDetection(self):
        print 'Face detection'
        if self.Facedetectionstatus.get() == 1:
            self.Facecoordinates, self.OpenCVImage = Desktop_Head_Arm_OpenCV.FindFaces()
            print self.Facecoordinates
            self.ImagetoGUI1(self.OpenCVImage)
            self.ImagetoGUI2(self.OpenCVImage)

            print len(self.Facecoordinates)
            if len(self.Facecoordinates) is 1: #No Face detected
                if self.FaceDetected is False: 
                    self.FaceDetected = True
                    Desktop_Head_Arm_Serial.sendcommand('F2E0') #Sad face

            elif len(self.Facecoordinates) is 2: #Face detected
                if self.FaceDetected is True: 
                    self.FaceDetected = False
                    Desktop_Head_Arm_Serial.sendcommand('F0E0') #Happy face

                errorX = CamCentreX - self.Facecoordinates[1][0]
                print errorX
                self.YawSlider.set(self.YawSlider.get() - (errorX*0.04))


                #Eye tracking for x direction

                if errorX > 80 and self.EyeStatus is not 1:
                    Desktop_Head_Arm_Serial.sendcommand('F0E1') #Happy face eyes left
                    self.EyeStatus = 1
                elif errorX < -80 and self.EyeStatus is not 2:
                    Desktop_Head_Arm_Serial.sendcommand('F0E2') #Happy face eyes right
                    self.EyeStatus = 2
                elif errorX < 80 and errorX > -80 and self.EyeStatus is not 0:
                    Desktop_Head_Arm_Serial.sendcommand('F0E0') #Happy face
                    self.EyeStatus = 0

                errorY = CamCentreY - self.Facecoordinates[1][1]
                print errorY
                self.PitchSlider.set(self.PitchSlider.get() + (errorY*0.04))
                self.sendHeadSliders(self)               

           

            self.after(50, self.FaceDetection) 

        else: #If face detection is disabled, send a happy face command to arduino
            Desktop_Head_Arm_Serial.sendcommand('F0E0') #Happy face



            
    def ColourDetection(self):
        print 'Colour detection'
        if self.Colourdetectionstatus.get() == 1:
            balldata, img, imgthreshed = Desktop_Head_Arm_OpenCV.FindBall(GREENOBJECTS)
            self.ImagetoGUI1(img)
            self.ImagetoGUI2(imgthreshed)

            if self.Colourtrackingstatus.get() == 1 and balldata is not -1: #tracking selected and object detected
                print "Colour Tracking"
                errorX = CamCentreX - balldata[0]
                print errorX
                self.YawSlider.set(self.YawSlider.get() - (errorX*0.04))


                #Eye tracking for x direction

                if errorX > 80 and self.EyeStatus is not 1:
                    Desktop_Head_Arm_Serial.sendcommand('F0E1') #Happy face eyes left
                    self.EyeStatus = 1
                elif errorX < -80 and self.EyeStatus is not 2:
                    Desktop_Head_Arm_Serial.sendcommand('F0E2') #Happy face eyes right
                    self.EyeStatus = 2
                elif errorX < 80 and errorX > -80 and self.EyeStatus is not 0:
                    Desktop_Head_Arm_Serial.sendcommand('F0E0') #Happy face
                    self.EyeStatus = 0

                errorY = CamCentreY - balldata[1]
                print errorY
                self.PitchSlider.set(self.PitchSlider.get() + (errorY*0.04))
                self.sendHeadSliders(self)


            self.after(50, self.ColourDetection) 




    def ImagetoGUI1(self,OpenCVImage):
            self.OpenCVGUIImage = Image.fromarray(OpenCVImage)
            self.OpenCVGUIImage = self.OpenCVGUIImage.resize((480, 360), Image.ANTIALIAS)
	    self.OpenCVGUIImage = ImageTk.PhotoImage(self.OpenCVGUIImage)
            self.CamImage.create_image(0,0, anchor=NW, image=self.OpenCVGUIImage)

    def ImagetoGUI2(self,OpenCVImage):
            self.OpenCVGUI2Image = Image.fromarray(OpenCVImage)
            self.OpenCVGUI2Image = self.OpenCVGUI2Image.resize((480, 360), Image.ANTIALIAS)
	    self.OpenCVGUI2Image = ImageTk.PhotoImage(self.OpenCVGUI2Image)
            self.CamImage2.create_image(0,0, anchor=NW, image=self.OpenCVGUI2Image)

root = Tk()
root.configure(bg = 'black')
root.title("Desktop Head and Arm: Big Face Robotics")
app = Application(master=root)
app.configure(bg = 'black')
app.mainloop()
