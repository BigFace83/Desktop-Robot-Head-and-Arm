from Tkinter import *
from tkFileDialog import *
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2TkAgg
from matplotlib.figure import Figure
from PIL import Image
from PIL import ImageTk
import Desktop_Head_Arm_Serial
import Desktop_Head_Arm_OpenCV
import Desktop_Head_Arm_Model
import numpy as np
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

Camimagewidth = 480
Camimageheight = 320






class Application(Frame):
    def __init__(self, master=None):
        Frame.__init__(self, master)
        self.grid()
        self.createWidgets()


        self.UpdateSonar()
        self.Updateservopositions()
        self.FaceDetected = False
        self.EyeStatus = 0

        self.WorldArray = []

      

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
     




        # Vision Frame contents
        self.CamImage = Canvas(VisionFrame, width=Camimagewidth, height=Camimageheight, bg = "black")
        self.CamImage.grid(row = 0, column = 0, columnspan = 4, pady = 5)

        self.CamImage2 = Canvas(VisionFrame, width=Camimagewidth, height=Camimageheight, bg = "black")
        self.CamImage2.grid(row = 1, column = 0, columnspan = 4, pady = 5)

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





        # Manual Frame contents
        self.commandEntry= Entry(ManualFrame)
        self.commandEntry.grid(row = 2, column = 0, columnspan = 3)
        self.commandEntry.bind('<Return>', self.sendCommand)

        self.send = Button(ManualFrame, text="Send", bg="royal blue", activebackground = "royal blue", highlightthickness = 0)
        self.send.bind('<Button-1>', self.sendCommand)
        self.send.grid(row = 2, column = 4, pady = 10)

        self.livedatastatus = IntVar()
        self.LiveDataCheck = Checkbutton(ManualFrame, text="Live Data", bg="royal blue", activebackground = "royal blue", highlightthickness = 0, variable=self.livedatastatus,command=self.LiveData)
        self.LiveDataCheck.grid(row = 3, column = 0, columnspan = 2)

        self.SonarCanvas = Canvas(ManualFrame, bg="black",  highlightthickness = 0, width=200, height=50)
        self.SonarCanvas.grid(row = 4, column = 0, columnspan = 3)

        self.SonarEntry= Entry(ManualFrame, bg="royal blue", highlightthickness = 0, width = 4)
        self.SonarEntry.grid(row = 4, column = 4)
        self.SonarEntry.insert(0, 0)


        self.Homebutton = Button(ManualFrame, text="Home", bg="royal blue", activebackground = "royal blue", highlightthickness = 0, command = self.Home)
        self.Homebutton.grid(row = 3, column = 4, pady = 10)



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
        # Sliders for Arm controls                   
        ###################################################################

        self.RotateSlider = Scale(ManualFrame, from_=-60, to=60, bg="royal blue", activebackground = "royal blue", highlightthickness = 0, orient= VERTICAL)
        self.RotateSlider.grid(row = 0, column = 3)
        self.RotateSlider.bind('<ButtonRelease-1>', self.sendArmSliders)

        self.LowerSlider = Scale(ManualFrame, from_=0, to=120, bg="royal blue", activebackground = "royal blue", highlightthickness = 0, orient= VERTICAL)
        self.LowerSlider.set(120)
        self.LowerSlider.grid(row = 0, column = 4)
        self.LowerSlider.bind('<ButtonRelease-1>', self.sendArmSliders)

        self.ElbowSlider = Scale(ManualFrame, from_=-140, to=20, bg="royal blue", activebackground = "royal blue", highlightthickness = 0, orient= VERTICAL)
        self.ElbowSlider.set(-140)
        self.ElbowSlider.grid(row = 0, column = 5)
        self.ElbowSlider.bind('<ButtonRelease-1>', self.sendArmSliders)

        self.GripperSlider = Scale(ManualFrame, from_=-90, to=90, bg="royal blue", activebackground = "royal blue", highlightthickness = 0, orient= VERTICAL)
        self.GripperSlider.set(30)
        self.GripperSlider.grid(row = 0, column = 6)
        self.GripperSlider.bind('<ButtonRelease-1>', self.sendArmSliders)

        ###################################################################
        # Entry boxes for Arm servo positions                  
        ###################################################################

        self.RotateEntry= Entry(ManualFrame, bg="royal blue", highlightthickness = 0, width = 4)
        self.RotateEntry.grid(row = 1, column = 3)

        self.LowerEntry= Entry(ManualFrame, bg="royal blue", highlightthickness = 0, width = 4)
        self.LowerEntry.grid(row = 1, column = 4)

        self.ElbowEntry= Entry(ManualFrame, bg="royal blue", highlightthickness = 0, width = 4)
        self.ElbowEntry.grid(row = 1, column = 5)

        self.GripperEntry= Entry(ManualFrame, bg="royal blue", highlightthickness = 0, width = 4)
        self.GripperEntry.grid(row = 1, column = 6)







        self.headservocheckstatus = IntVar()
        self.headServoCheck = Checkbutton(PowerFrame, text="Head Servos enabled", bg="royal blue", activebackground = "royal blue", highlightthickness = 0, variable=self.headservocheckstatus, command=self.headservopower)
        self.headServoCheck.grid(row = 0, column = 0)

        self.armservocheckstatus = IntVar()
        self.armServoCheck = Checkbutton(PowerFrame, text="Arm Servos enabled", bg="royal blue", activebackground = "royal blue", highlightthickness = 0, variable=self.armservocheckstatus, command=self.armservopower)
        self.armServoCheck.grid(row = 0, column = 1)





        self.SeqVar = StringVar()
        self.SeqVar.set("None") # initial value
        self.SeqOption = OptionMenu(SequenceFrame, self.SeqVar, "None", "Shake Head", "Nod Head", "Arm Test")
        self.SeqOption.grid(row = 0, column = 0)

        self.RunSeq = Button(SequenceFrame, bg="royal blue", activebackground = "royal blue", highlightthickness = 0, text="Run Sequence")
        self.RunSeq.bind('<Button-1>', self.RunSequence)
        self.RunSeq.grid(row = 0, column = 1)


        # Visualisation Frame contents

        ###################################################################
        # Robot Arm Model Window - MatPlotLib chart                
        ###################################################################

        self.ArmModelFig = Figure(figsize=(3,3), dpi=100)

        self.ArmModelCanvas = FigureCanvasTkAgg(self.ArmModelFig, VisualisationFrame)
        self.ArmModelCanvas.show()
        self.ArmModelCanvas.get_tk_widget().grid(row = 0, column = 0, pady = 5, columnspan = 2)


        self.showsonarstatus = IntVar()
        self.ShowSonarCheck = Checkbutton(VisualisationFrame, text="Show Sonar", bg="royal blue", activebackground = "royal blue", highlightthickness = 0, variable=self.showsonarstatus)
        self.ShowSonarCheck.grid(row = 1, column = 0)

        self.a = self.ArmModelFig.add_subplot(111, projection='3d')
        self.PlotRobotArm([self.RotateSlider.get(),self.LowerSlider.get(),self.ElbowSlider.get(),self.GripperSlider.get()])


        ###################################################################
        # Environment Model Window - MatPlotLib chart                
        ###################################################################

        self.WorldModelFig = Figure(figsize=(6,6), dpi=100)
        self.WorldModelCanvas = FigureCanvasTkAgg(self.WorldModelFig, VisualisationFrame)
        self.WorldModelCanvas.show()
        self.WorldModelCanvas.get_tk_widget().grid(row = 2, column = 0, pady = 5, columnspan = 4)

        self.Plotworldstatus = IntVar()
        self.PlotworldCheck = Checkbutton(VisualisationFrame, text="Start World Plot", bg="royal blue", activebackground = "royal blue", highlightthickness = 0, variable=self.Plotworldstatus)
        self.PlotworldCheck.grid(row = 3, column = 0)

        self.DatapointEntry= Entry(VisualisationFrame, bg="royal blue", highlightthickness = 0, width = 5)
        self.DatapointEntry.grid(row = 3, column = 1)

        self.Clearworld = Button(VisualisationFrame, text="Clear Plot", bg="royal blue", activebackground = "royal blue", highlightthickness = 0)
        self.Clearworld.bind('<Button-1>', self.ClearWorldPlot)
        self.Clearworld.grid(row = 3, column = 2)

        self.PlotworldButton = Button(VisualisationFrame, text="Plot", bg="royal blue", activebackground = "royal blue", highlightthickness = 0)
        self.PlotworldButton.bind('<Button-1>', self.PlotWorld)
        self.PlotworldButton.grid(row = 3, column = 3)



        self.b = self.WorldModelFig.add_subplot(111, projection='3d')
        self.WorldModelFig.tight_layout()
        self.b.set_facecolor('black') #Set background and all gridlines to black
        self.b.w_xaxis.set_pane_color((0, 0, 0, 1.0))
        self.b.w_yaxis.set_pane_color((0, 0, 0, 1.0))
        self.b.w_zaxis.set_pane_color((0, 0, 0, 1.0))
        self.b.xaxis._axinfo["grid"]['color'] = "black"
        self.b.yaxis._axinfo["grid"]['color'] = "black"
        self.b.zaxis._axinfo["grid"]['color'] = "black"
        self.b.set_xlim3d(-50, 2000) #Set plot limits
        self.b.set_ylim3d(-2000,2000)
        self.b.set_zlim3d(-2000,2000)

        self.b.plot([0,0],[0,0],[0,20], color="blue", linewidth=10)

    def PlotRobotArm(self,JointAngles):

        ReturnArray, XYZSonar = Desktop_Head_Arm_Model.DHGetJointPositions(JointAngles[0], JointAngles[1], JointAngles[2], JointAngles[3], int(self.SonarEntry.get())*10)

        X =  ReturnArray[:,0]
        Y = ReturnArray[:,1]
        Z = ReturnArray[:,2]

        self.a.clear()
 

        self.a.set_xlim3d(-50, 300)
        self.a.set_ylim3d(-200,200)
        self.a.set_zlim3d(0,300)
        self.a.set_autoscale_on(False)
        self.ArmModelFig.tight_layout()

        self.a.plot(X,Y,Z, color="blue", linewidth=8)

        if self.showsonarstatus.get() == 1:
            self.a.plot((ReturnArray.item(4,0), XYZSonar.item(0)),(ReturnArray.item(4,1), XYZSonar.item(1)),(ReturnArray.item(4,2), XYZSonar.item(2)), color="red", linewidth=1)

        self.ArmModelCanvas.draw()

        return XYZSonar
        
    def PlotWorld(self, event):

        worldnparray = np.asarray(self.WorldArray)
        X =  worldnparray[:,0]
        Y = worldnparray[:,1]
        Z = worldnparray[:,2]
        self.b.scatter(X,Y,Z, s = 20,  depthshade = True)
        self.WorldModelCanvas.draw()

    def ClearWorldPlot(self,event):
        self.b.clear()
        self.b.set_xlim3d(-50, 2000)
        self.b.set_ylim3d(-2000,2000)
        self.b.set_zlim3d(-2000,2000)

        self.b.plot([0,0],[0,0],[0,20], color="blue", linewidth=10)
        self.WorldModelCanvas.draw()

        self.WorldArray = []

 
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
 
        self.RollSlider.set(0)
        self.PitchSlider.set(0)
        self.YawSlider.set(0)

        self.RotateSlider.set(0)
        self.LowerSlider.set(120)
        self.ElbowSlider.set(-135)
        self.GripperSlider.set(30)

        self.sendHeadSliders(self)
        self.sendArmSliders(self)


    def sendHeadSliders(self,event):
        print "Sending Command", 'H0R'+str(self.RollSlider.get())+'P'+str(self.PitchSlider.get())+'Y'+str(self.YawSlider.get())
        Desktop_Head_Arm_Serial.sendcommand('H0R'+str(self.RollSlider.get())+'P'+str(self.PitchSlider.get())+'Y'+str(self.YawSlider.get()))
        
    def sendArmSliders(self,event):
        print "Sending Command", 'A0B'+str(self.RotateSlider.get())+'L'+str(self.LowerSlider.get())+'U'+str(self.ElbowSlider.get())
        Desktop_Head_Arm_Serial.sendcommand('A0B'+str(self.RotateSlider.get())+'L'+str(self.LowerSlider.get())+'U'+str(self.ElbowSlider.get())+'G'+str(self.GripperSlider.get()))       

        if self.livedatastatus.get() == 0:
            self.PlotRobotArm([self.RotateSlider.get(),self.LowerSlider.get(),self.ElbowSlider.get(),self.GripperSlider.get()])
        
   
    def CaptureImage(self):
        #self.OpenCVImage = Desktop_Head_Arm_OpenCV.ReturnFrameRGB()
        balldata, self.OpenCVImage, imgthreshed = Desktop_Head_Arm_OpenCV.FindBall(YELLOWOBJECTS)
        self.ImagetoGUI1(self.OpenCVImage)



    def UpdateSonar(self):
        Desktop_Head_Arm_Serial.sendcommand('A5')
        SonarDistance = int(Desktop_Head_Arm_Serial.readserial())
        
        self.SonarCanvas.create_rectangle(0, 0, 200, 50, fill="black")
        self.SonarCanvas.create_line(0, 25, SonarDistance/2, 25, fill="green", width=20)

        self.SonarEntry.delete(0, END)
        self.SonarEntry.insert(0, SonarDistance)

        self.after(100, self.UpdateSonar)


        
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

        Desktop_Head_Arm_Serial.sendcommand('A4')
        Gripperservopos = int(Desktop_Head_Arm_Serial.readserial())
        self.GripperEntry.delete(0, END)
        self.GripperEntry.insert(0, Gripperservopos)


        if self.livedatastatus.get() == 1:
            XYZSonar = self.PlotRobotArm([Rotateservopos,Lowerservopos,Elbowservopos,Gripperservopos])
            if self.Plotworldstatus.get() == 1: #if we want to log sonar end positions
                    self.WorldArray.append([XYZSonar.item(0),XYZSonar.item(1),XYZSonar.item(2)])
                    self.DatapointEntry.delete(0, END)
                    self.DatapointEntry.insert(0, len(self.WorldArray))

            self.after(100, self.Updateservopositions)  


    def RunSequence(self,event):
        if self.SeqVar.get() == 'Shake Head':
            print 'Shake Head'
            self.HeadShake()
        elif self.SeqVar.get() == 'Nod Head':
            print 'Nod Head'
            self.HeadNod()
        elif self.SeqVar.get() == 'Arm Test':
            print 'Arm Test'
            self.ArmTest()
        
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

    def ArmTest(self):
        Desktop_Head_Arm_Serial.sendcommand('A0 B0L0U-70G0')
        time.sleep(1)
        Desktop_Head_Arm_Serial.sendcommand('A0 B-36L89U-43G0')
        time.sleep(1)
        Desktop_Head_Arm_Serial.sendcommand('A0 B-36L99U-35G10')
        time.sleep(1)
        Desktop_Head_Arm_Serial.sendcommand('A0 B6L10U46G-45')
        time.sleep(1)


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
            self.OpenCVGUIImage = self.OpenCVGUIImage.resize((Camimagewidth, Camimageheight), Image.ANTIALIAS)
	    self.OpenCVGUIImage = ImageTk.PhotoImage(self.OpenCVGUIImage)
            self.CamImage.create_image(0,0, anchor=NW, image=self.OpenCVGUIImage)

    def ImagetoGUI2(self,OpenCVImage):
            self.OpenCVGUI2Image = Image.fromarray(OpenCVImage)
            self.OpenCVGUI2Image = self.OpenCVGUI2Image.resize((Camimagewidth, Camimageheight), Image.ANTIALIAS)
	    self.OpenCVGUI2Image = ImageTk.PhotoImage(self.OpenCVGUI2Image)
            self.CamImage2.create_image(0,0, anchor=NW, image=self.OpenCVGUI2Image)

root = Tk()
root.configure(bg = 'black')
root.title("Desktop Head and Arm: Big Face Robotics")
app = Application(master=root)
app.configure(bg = 'black')
app.mainloop()
