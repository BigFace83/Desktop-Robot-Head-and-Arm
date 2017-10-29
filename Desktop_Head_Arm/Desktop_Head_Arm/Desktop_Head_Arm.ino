/****************************************************************************
Author: Peter Neal      Date: 17/4/17

Arduino Mega code for Social Robot.

Servo potentiometers used for closed loop control of servo position

****************************************************************************/

#include "SPI.h"
#include "Adafruit_GFX.h"
#include "Adafruit_ILI9340.h"

#include <Servo.h>


/****************************************************************************
Set-up for Adafruit 2.2" TFT screen

****************************************************************************/
// These are the pins used for the Mega
#define _sclk 52
#define _miso 50
#define _mosi 51
#define _cs 53
#define _dc 49
#define _rst 48

// Use hardware SPI
Adafruit_ILI9340 tft = Adafruit_ILI9340(_cs, _dc, _rst);


#define BUFFERSIZE 64
char databuffer[BUFFERSIZE];
int serialcounter = 0;


/****************************************************************************
Analogue input set-up for reading potentiometers

****************************************************************************/

const int RollInPin = A9;
const int PitchInPin = A8;
const int YawInPin = A7;  // Analog input pin that the potentiometer is attached to

const int ArmRotateInPin = A0;
const int ArmLowerInPin = A1;
const int ArmElbowInPin = A2;

const int HandSwitchPin = 30;     //Hand switch input pin

int HandSwitchState = 1;


int RawRollValue = 0;        // value read from the pot
int RawPitchValue = 0;        // value read from the pot
int RawYawValue = 0;        // value read from the pot

int RawArmRotateValue = 0;
int RawArmLoweBvalue = 0;
int RawArmElbowValue = 0;



/****************************************************************************
PID gains for servo movements

****************************************************************************/
#define HeadPGain 1.2
#define HeadDGain 0.8


#define ArmPGain 1.2
#define ArmDGain 0.8




/****************************************************************************
Set-up for head servos

Roll servo  - Pin 6
Pitch servo - Pin 5
Yaw servo   - Pin 4
****************************************************************************/

Servo HeadRoll;
Servo HeadPitch;
Servo HeadYaw;

Servo ArmRotate;
Servo ArmLower;
Servo ArmElbow;

unsigned long previousMillis = 0;

bool HeadServosAttached = false;
bool ArmServosAttached = false;


int HeadYawms = 1500;
int HeadPitchms = 1500;
int HeadRollms = 1500;

int ArmRotatems = 1500;
int ArmLowerms = 2350;
int ArmElbowms = 2170;




//Servo set points in degrees
volatile int RollSetpoint = 0;
volatile int PitchSetpoint = 0;
volatile int YawSetpoint = 0;

volatile int ArmRotateSetpoint = 0;
volatile int ArmLowerSetpoint = 0;
volatile int ArmElbowSetpoint = -65;



void setup() {
 
  
    Serial.begin(115200);

   
   /******************************************************************
     Initialise Servos and set to home positions                
    ******************************************************************/
    //attachservos();
  
    HeadRoll.writeMicroseconds(HeadRollms);
    HeadPitch.writeMicroseconds(HeadPitchms);
    HeadYaw.writeMicroseconds(HeadYawms);

    ArmRotate.writeMicroseconds(ArmRotatems);
    ArmLower.writeMicroseconds(ArmLowerms);
    ArmElbow.writeMicroseconds(ArmElbowms);

    
    pinMode(HandSwitchPin, INPUT);
    
    
    /******************************************************************
     Set-up TFT screen and initialise                
    ******************************************************************/
    tft.begin();
    tft.setRotation(1);
    tft.fillScreen(ILI9340_BLACK);
    DrawFace(1,0);

  
}



// ================================================================
// ===                    MAIN PROGRAM LOOP                     ===
// ================================================================

void loop() {
 
      
    //keep an eye out for serial data
    while(Serial.available() > 0)  // if something is available from serial port
    { 
        char c=Serial.read();      // get it
        databuffer[serialcounter] = c; //add it to the data buffer
        serialcounter++;
        if(c=='\n'){  //newline character denotes end of message
            serialcounter = 0; //reset serialcounter ready for the next message
            interpretcommand();
            break;
        }           
    }
       

    unsigned long currentMillis = millis();
        
    if((currentMillis - previousMillis > 40)) //use this to determine frequency of servo loop
    {
        // save the last time pid loop was called
        previousMillis = currentMillis;
              
        // read the potentiometer values for all joints:
        RawRollValue = analogRead(RollInPin);
        RawPitchValue = analogRead(PitchInPin);
        RawYawValue = analogRead(YawInPin);

        RawArmRotateValue = analogRead(ArmRotateInPin);
        RawArmLoweBvalue = analogRead(ArmLowerInPin);
        RawArmElbowValue = analogRead(ArmElbowInPin);
  
        // map it to the calibrated range for angles:
        int ScaledRollValue = map(RawRollValue, 515, 120, -90, 90);
        int ScaledPitchValue = map(RawPitchValue, 460, 180, 70, -65);
        int ScaledYawValue = map(RawYawValue, 515, 105, -90, 90);

        int ScaledArmRotateValue = map(RawArmRotateValue, 522, 82, -60, 60);
        int ScaledArmLoweBvalue = map(RawArmLoweBvalue, 524, 82, 0, 100);
        int ScaledArmElbowValue = map(RawArmElbowValue, 460, 85, -70, 125);

        
        /*
        // print the results to the serial monitor:
        Serial.print("Rot mz = ");
        Serial.print(ArmRotatems);
        Serial.print(", Lower ms = ");
        Serial.println(ArmLowerms);
        Serial.print(", Elbow ms = ");
        Serial.println(ArmElbowms);
        */
        

        
        if(HeadServosAttached){
            HeadPID(ScaledRollValue ,ScaledPitchValue ,ScaledYawValue);
        }
        if(ArmServosAttached){        
            ArmPID(ScaledArmRotateValue, ScaledArmLoweBvalue, ScaledArmElbowValue);
        }
      }    
        
        

}



void HeadPID(float Roll,float Pitch,float Yaw){
  
    //Serial.println("DO PID");
    
    static float RollprevError;
    static float PitchprevError;
    static float YawprevError;



    float RollError = Roll - RollSetpoint;  
    HeadRollms = int(HeadRollms + (RollError*HeadPGain) + ((RollError-RollprevError)*HeadDGain));
    HeadRoll.writeMicroseconds(HeadRollms);  
    RollprevError = RollError;

    float PitchError = Pitch - PitchSetpoint;
    HeadPitchms = int(HeadPitchms - (PitchError*HeadPGain) - ((PitchError-PitchprevError)*HeadDGain));
    HeadPitch.writeMicroseconds(HeadPitchms);   
    PitchprevError = PitchError;

    
    float YawError = Yaw - YawSetpoint;
    HeadYawms = int(HeadYawms + (YawError*HeadPGain) + ((YawError-YawprevError)*HeadDGain));
    HeadYaw.writeMicroseconds(HeadYawms);
    YawprevError = YawError;


    

    

   
}

void ArmPID(float Rotate,float Lower, float Elbow){
  
    //Serial.println("DO PID");
    
    static float RotateprevError;
    static float LowerprevError;
    static float ElbowprevError;

    
    float RotateError = Rotate - ArmRotateSetpoint;
    ArmRotatems = int(ArmRotatems + (RotateError*ArmPGain) + ((RotateError-RotateprevError)*ArmDGain));
    ArmRotate.writeMicroseconds(ArmRotatems);   
    RotateprevError = RotateError;

    float LowerError = Lower - ArmLowerSetpoint;
    ArmLowerms = int(ArmLowerms + (LowerError*ArmPGain) + ((LowerError-LowerprevError)*ArmDGain));
    ArmLower.writeMicroseconds(ArmLowerms);    
    LowerprevError = LowerError;

    float ElbowError = Elbow - ArmElbowSetpoint;
    ArmElbowms = int(ArmElbowms + (ElbowError*(ArmPGain/2)) + ((ElbowError-ElbowprevError)*(ArmDGain/2)));
    ArmElbow.writeMicroseconds(ArmElbowms);    
    ElbowprevError = ElbowError;


   
}




void DrawFace(int Face, int Eyes){



  switch(Face){
    case 0: //Happy Face
      // Eye centres 100, 240
      tft.fillRoundRect(50, 30, 100, 100, 30, ILI9340_BLUE);
      tft.fillRoundRect(190, 30, 100, 100, 30, ILI9340_BLUE);

      //Mouth
      tft.fillRect(100, 190, 140, 50, ILI9340_BLACK);
      tft.fillRoundRect(100, 170, 140, 40, 20, ILI9340_RED);
      tft.fillRect(100, 170, 140, 20, ILI9340_BLACK);
      break;

    case 1: //Blinking Face
      // Eye centres 100, 240
      tft.fillRoundRect(50, 30, 100, 100, 30, ILI9340_BLACK);
      tft.fillRoundRect(190, 30, 100, 100, 30, ILI9340_BLACK);
      tft.fillRect(50, 75, 100, 10, ILI9340_BLUE);
      tft.fillRect(190, 75, 100, 10, ILI9340_BLUE);

      //Mouth
      tft.fillRect(100, 190, 140, 50, ILI9340_BLACK);
      tft.fillRoundRect(100, 170, 140, 40, 20, ILI9340_RED);
      tft.fillRect(100, 170, 140, 20, ILI9340_BLACK);

      Eyes = 5;
      break;

      
    case 2: //Sad Face
      tft.fillRoundRect(50, 30, 100, 100, 30, ILI9340_BLUE);
      tft.fillRoundRect(190, 30, 100, 100, 30, ILI9340_BLUE);
      tft.fillTriangle(50,30, 150,30, 50,70 , ILI9340_BLACK);
      tft.fillTriangle(190,30, 290,30, 290,70 , ILI9340_BLACK); 
      
      tft.fillRect(100, 190, 140, 50, ILI9340_BLACK);
      tft.fillRoundRect(100, 190, 140, 40, 20, ILI9340_RED);
      tft.fillRect(100, 210, 140, 20, ILI9340_BLACK);
      
      break;
      
    case 3: // Angry Face
      tft.fillRoundRect(50, 30, 100, 100, 30, ILI9340_BLUE);
      tft.fillRoundRect(190, 30, 100, 100, 30, ILI9340_BLUE);
      tft.fillTriangle(50,30, 150,30, 150,70 , ILI9340_BLACK);
      tft.fillTriangle(190,30, 190,70, 290,30 , ILI9340_BLACK); 
      
      tft.fillRect(100, 190, 140, 50, ILI9340_BLACK);
      tft.fillRoundRect(100, 190, 140, 40, 20, ILI9340_RED);
      tft.fillRect(100, 210, 140, 20, ILI9340_BLACK);
      
      break;
   
  }

  switch(Eyes){
    case 0: //Eyes front
      tft.fillCircle(100, 80, 15, ILI9340_BLACK);
      tft.fillCircle(240, 80, 15, ILI9340_BLACK);
      break;
    case 1: //Eyes Left
      tft.fillCircle(120, 80, 15, ILI9340_BLACK);
      tft.fillCircle(260, 80, 15, ILI9340_BLACK);
      break;
    case 2: //Eyes Right
      tft.fillCircle(80, 80, 15, ILI9340_BLACK);
      tft.fillCircle(220, 80, 15, ILI9340_BLACK);
      break;
    case 3: //Eyes Up
      tft.fillCircle(100, 60, 15, ILI9340_BLACK);
      tft.fillCircle(240, 60, 15, ILI9340_BLACK);
      break;
    case 4: //Eyes Down
      tft.fillCircle(100, 100, 15, ILI9340_BLACK);
      tft.fillCircle(240, 100, 15, ILI9340_BLACK);
      break;
    case 5: //No eyes
      break;
  }
  
  
}
  

void interpretcommand()
{
   int Fvalue; //Face Command
   int Evalue; //Eyes Command
   int Hvalue; //Head command
   int Avalue; //Arm command
   int Bvalue; //Base rotate arm value
   int Lvalue; //Lower arm value
   int Uvalue; //Upper arm value
   int Svalue; //Servo Command
   int Rvalue; //Roll setpoint
   int Pvalue; //Pitch setpoint
   int Yvalue; //Yaw setpoint
   boolean validcommand = false;
   
   //Check for any head move commands first
   
   Hvalue = findchar('H');
   switch(Hvalue){
   case(0):{
        Rvalue = findchar('R');
        if (Rvalue != -1){
          RollSetpoint = Rvalue;
        }
        Pvalue = findchar('P');
        if (Pvalue != -1){
          PitchSetpoint = Pvalue;
        }
        Yvalue = findchar('Y');
        if (Yvalue != -1){
          YawSetpoint = Yvalue;
        }
        break;    
     }
   case(1):{
        Serial.println(map(RawRollValue, 515, 120, -90, 90));
        break;
    }
   case(2):{
        Serial.println(map(RawPitchValue, 460, 180, 70, -65));
        break;
    }
   case(3):{
        Serial.println(map(RawYawValue, 515, 105, -90, 90));
        break;
    }     
   }

   Avalue = findchar('A');
   switch(Avalue){
   case(0):{
        Bvalue = findchar('B');
        if (Bvalue != -1){
          ArmRotateSetpoint = Bvalue;
        }
        Lvalue = findchar('L');
        if (Lvalue != -1){
          ArmLowerSetpoint = Lvalue;
        }
        Uvalue = findchar('U');
        if (Uvalue != -1){
          ArmElbowSetpoint = Uvalue;
        }
        break;    
     }
   case(1):{
        Serial.println(map(RawArmRotateValue, 522, 82, -60, 60));
        break;
    }
   case(2):{
        Serial.println(map(RawArmLoweBvalue, 524, 82, 0, 100));
        break;
    }
   case(3):{
        Serial.println(map(RawArmElbowValue, 460, 85, -70, 125));
        break;
    }        
   case(4):{
        HandSwitchState = digitalRead(HandSwitchPin);
        Serial.println(HandSwitchState);
        break;
    }
   }
   
   
   Fvalue = findchar('F');
   switch(Fvalue){
   case(0):
       Evalue = findchar('E');
       if (Evalue != -1){
           DrawFace(0,Evalue);
       }
       break;
        
   case(1):
       Evalue = findchar('E');
       if (Evalue != -1){
           DrawFace(1,Evalue);
       }
       break; 
   case(2):
       Evalue = findchar('E');
       if (Evalue != -1){
           DrawFace(2,Evalue);
       }
       break;  
   case(3):
       Evalue = findchar('E');
       if (Evalue != -1){
           DrawFace(3,Evalue);
       }
       break;    
     }


   Svalue = findchar('S');
   switch(Svalue){
   case(0):{
       attachheadservos();
       break;}  
   case(1):{
       attacharmservos();
       break;} 
   case(2):{
       detachheadservos();
       break;}
   case(3):{
       detacharmservos();
       break;}
      
     }    
    
     
}   




int findchar(char a)
{
  int charindex;
  String value;
  //Find the index of the character being looked for
  for(int i = 0; i<BUFFERSIZE; i++)
  {
    if(databuffer[i] == '\n')
    {
      return -1; //no character found so return -1
    }   
    if(databuffer[i] == a)
    {
      charindex = i;
      break;
    }
  }
  
  //extract characters following character of interest as a string and convert to a value
  for(int i = charindex+1; i<BUFFERSIZE; i++)
  {
    value += (databuffer[i]);
  }
  int data = value.toInt();
  return data;
  
}



void attachheadservos()
{
    HeadRoll.attach(6);
    HeadPitch.attach(5);
    HeadYaw.attach(4);

    DrawFace(0,0);

    HeadServosAttached = true;
}

void attacharmservos()
{

    ArmRotate.attach(7);
    ArmLower.attach(8);
    ArmElbow.attach(9);

    ArmServosAttached = true;
}
  
void detachheadservos()
{
    HeadRoll.detach();
    HeadPitch.detach();
    HeadYaw.detach();

    DrawFace(1,0);

    HeadServosAttached = false;
}

void detacharmservos()
{
    ArmRotate.detach();
    ArmLower.detach();
    ArmElbow.detach();

    ArmServosAttached = false;
    
}

