// I2Cdev and MPU6050 must be installed as libraries, or else the .cpp/.h files
// for both classes must be in the include path of your project
#include "I2Cdev.h"
#include "MPU6050_6Axis_MotionApps20.h"
#include "Wire.h"

#include <Servo.h>


/****************************************************************************
Set-up for MPU6050 accelerometer

NOTE: In addition to connection 3.3v, GND, SDA, and SCL, this sketch
depends on the MPU-6050's INT pin being connected to the Arduino's
external interrupt #0 pin. On the Arduino Uno and Mega 2560, this is
digital I/O pin 2.
****************************************************************************/
// class default I2C address is 0x68
MPU6050 mpu;

#define LED_PIN 13 // (Arduino is 13, Teensy is 11, Teensy++ is 6)
bool blinkState = false;

// MPU control/status vars
bool dmpReady = false;  // set true if DMP init was successful
uint8_t mpuIntStatus;   // holds actual interrupt status byte from MPU
uint8_t devStatus;      // return status after each device operation (0 = success, !0 = error)
uint16_t packetSize;    // expected DMP packet size (default is 42 bytes)
uint16_t fifoCount;     // count of all bytes currently in FIFO
uint8_t fifoBuffer[64]; // FIFO storage buffer

// orientation/motion vars
Quaternion q;           // [w, x, y, z]         quaternion container
VectorInt16 aa;         // [x, y, z]            accel sensor measurements
VectorInt16 aaReal;     // [x, y, z]            gravity-free accel sensor measurements
VectorInt16 aaWorld;    // [x, y, z]            world-frame accel sensor measurements
VectorFloat gravity;    // [x, y, z]            gravity vector
float euler[3];         // [psi, theta, phi]    Euler angle container
float ypr[3];           // [yaw, pitch, roll]   yaw/pitch/roll container and gravity vector


/****************************************************************************
Set-up for head servos

Roll servo  - Pin 6
Pitch servo - Pin 5
Yaw servo   - Pin 4
****************************************************************************/

Servo HeadRoll;
Servo HeadPitch;
Servo HeadYaw;

unsigned long previousMillis = 0;


int HeadYawms = 1500;
int HeadPitchms = 1425;
int HeadRollms = 1445;

//Servo set points in degrees
volatile int xSetpoint = 25;
volatile int ySetpoint = 35;
volatile int zSetpoint = -25;


/******************************************************************
               INTERRUPT DETECTION ROUTINE                
******************************************************************/

volatile bool mpuInterrupt = false;     // indicates whether MPU interrupt pin has gone high
void dmpDataReady() {
    mpuInterrupt = true;
}


void setup() {
 
  
    Serial.begin(115200);
  
    Wire.begin();
    TWBR = 24; // 400kHz I2C clock (200kHz if CPU is 8MHz)
   
   
    /******************************************************************
     Initialise Servos and set to home positions                
    ******************************************************************/
    HeadRoll.attach(6);
    HeadPitch.attach(5);
    HeadYaw.attach(4);
  
    HeadRoll.writeMicroseconds(HeadRollms);
    HeadPitch.writeMicroseconds(HeadPitchms);
    HeadYaw.writeMicroseconds(HeadYawms);
   
    /******************************************************************
     Initialise MPU6050                
    ******************************************************************/
    // initialize device
    Serial.println(F("Initializing I2C devices..."));
    mpu.initialize();

    // verify connection
    Serial.println(F("Testing device connections..."));
    Serial.println(mpu.testConnection() ? F("MPU6050 connection successful") : F("MPU6050 connection failed"));

    // wait for ready
    Serial.println(F("\nSend any character to begin DMP programming and demo: "));
    while (Serial.available() && Serial.read()); // empty buffer
    while (!Serial.available());                 // wait for data
    while (Serial.available() && Serial.read()); // empty buffer again

    // load and configure the DMP
    Serial.println(F("Initializing DMP..."));
    devStatus = mpu.dmpInitialize();

    // supply your own gyro offsets here, scaled for min sensitivity
    
    mpu.setXAccelOffset(-4650); //220
    mpu.setYAccelOffset(-980); //76
    mpu.setZAccelOffset(1450); //-85
    
    
    mpu.setXGyroOffset(-35); //220
    mpu.setYGyroOffset(40); //76
    mpu.setZGyroOffset(-80); //-85

    // make sure it worked (returns 0 if so)
    if (devStatus == 0) {
        // turn on the DMP, now that it's ready
        Serial.println(F("Enabling DMP..."));
        mpu.setDMPEnabled(true);

        // enable Arduino interrupt detection
        Serial.println(F("Enabling interrupt detection (Arduino external interrupt 0)..."));
        attachInterrupt(0, dmpDataReady, RISING);
        mpuIntStatus = mpu.getIntStatus();

        // set our DMP Ready flag so the main loop() function knows it's okay to use it
        Serial.println(F("DMP ready! Waiting for first interrupt..."));
        dmpReady = true;

        // get expected DMP packet size for later comparison
        packetSize = mpu.dmpGetFIFOPacketSize();
    } 
    else {
        // ERROR!
        // 1 = initial memory load failed
        // 2 = DMP configuration updates failed
        // (if it's going to break, usually the code will be 1)
        Serial.print(F("DMP Initialization failed (code "));
        Serial.print(devStatus);
        Serial.println(F(")"));
    }

    // configure LED for output
    pinMode(LED_PIN, OUTPUT);
}



// ================================================================
// ===                    MAIN PROGRAM LOOP                     ===
// ================================================================

void loop() {
    // if programming failed, don't try to do anything
    if (!dmpReady) return;
   
    // wait for MPU interrupt or extra packet(s) available
    while (!mpuInterrupt && fifoCount < packetSize) {
        // other program behavior stuff here
       
    }

    
    // reset interrupt flag and get INT_STATUS byte
    mpuInterrupt = false;
    mpuIntStatus = mpu.getIntStatus();

    // get current FIFO count
    fifoCount = mpu.getFIFOCount();

    // check for overflow (this should never happen unless our code is too inefficient)
    if ((mpuIntStatus & 0x10) || fifoCount == 1024) {
        // reset so we can continue cleanly
        mpu.resetFIFO();
        Serial.println(F("FIFO overflow!"));

    // otherwise, check for DMP data ready interrupt (this should happen frequently)
    } 
    else if (mpuIntStatus & 0x02) {
        // wait for correct available data length, should be a VERY short wait
        while (fifoCount < packetSize) fifoCount = mpu.getFIFOCount();

        // read a packet from FIFO
        mpu.getFIFOBytes(fifoBuffer, packetSize);
        
        // track FIFO count here in case there is > 1 packet available
        // (this lets us immediately read more without waiting for an interrupt)
        fifoCount -= packetSize;


        // display Euler angles in degrees
        mpu.dmpGetQuaternion(&q, fifoBuffer);
        mpu.dmpGetGravity(&gravity, &q);
        mpu.dmpGetYawPitchRoll(ypr, &q, &gravity);
        
        
        unsigned long currentMillis = millis();
        
        if(currentMillis - previousMillis > 50) //use this to determine frequency of servo loop
        {
            // save the last time pid loop was called
            previousMillis = currentMillis;
            ServoPID(ypr[0] * 180/M_PI,ypr[1] * 180/M_PI,ypr[2] * 180/M_PI);
        }    
        
        

    }
}



void ServoPID(float x,float y,float z){
  
    Serial.println("DO PID LOOP");
    Serial.print("ypr\t");
    Serial.print(x);
    Serial.print("\t");
    Serial.print(y);
    Serial.print("\t");
    Serial.println(z);
    
    float xError = x - xSetpoint;
    HeadYawms = HeadYawms + int(xError*1);
    HeadYaw.writeMicroseconds(HeadYawms);
    
    float yError = y - ySetpoint;
    HeadPitchms = HeadPitchms - int(yError*1);
    HeadPitch.writeMicroseconds(HeadPitchms);
    
    float zError = z - zSetpoint;
    HeadRollms = HeadRollms - int(zError*1);
    HeadRoll.writeMicroseconds(HeadRollms);
    
    Serial.print("Servo ms\t");
    Serial.print(HeadYawms);
    Serial.print("\t");
    Serial.print(HeadPitchms);
    Serial.print("\t");
    Serial.println(HeadRollms);
    
 
}
  
  
  
  
  
