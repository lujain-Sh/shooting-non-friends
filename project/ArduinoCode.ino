#include <Servo.h>

Servo myservo;  // create Servo object to control a servo
// twelve Servo objects can be created on most boards
Servo myservo2;
  // variable to store the servo position
char data;
bool exitt= false;
int current_pos1=0;
int current_pos2=0;
int buzzer=3;
int sq=0;
bool tm=true;
unsigned long previousMillis = 0;  // will store last time LED was updated

// constants won't change:
const long interval = 10000;  // interval at which to blink (milliseconds)

void setup() {
  
  Serial.begin(9600);
  myservo.attach(9,600,2400);  // attaches the servo on pin 9 to the Servo object
  myservo2.attach(11);
  myservo2.write(0);
  pinMode(buzzer,OUTPUT);
  digitalWrite(buzzer, LOW);

  }

void loop() {
  

      if(!exitt && current_pos2==0){
        
        for (int p=current_pos1; p <= 180; p += 5) { // goes from p degrees to 180 degrees
        // in steps of 5 degrees
          if (Serial.available() > 0) {
            data=Serial.read();
            if(data=='2'){
              myservo.write(max(p-28,0));
              exitt=true;
              current_pos1=max(p-28,0);
              
              break;
            }
             if(data=='7'){
              myservo.write(min(p+28,180));
              exitt=true;
              current_pos1=min(p+28,180);
              
              break;
            }
            if(data=='1') { exitt=true; current_pos1=p;  break; }}
            if(p==180) {current_pos1=180;current_pos2=180;}
          myservo.write(p) ;              // tell servo to go to position in variable 'p'
          delay(1000);                       // waits x ms for the servo to reach the position
          
        }}
        
      if(!exitt && current_pos1==180){
          for (int p=current_pos2; p >= 0; p -= 5) { // goes from p degrees to 0 degrees
           if (Serial.available() > 0) {
            data=Serial.read();
            if(data=='2'){
              myservo.write(max(p-28,0));
              exitt=true;
              current_pos2=max(p-28,0);
              break;
            }
             if(data=='7'){
              myservo.write(min(p+28,180));
              exitt=true;
              current_pos2=min(p+28,180);
              break;
            }
            if(data =='1') { exitt=true; current_pos2=p; break;}}
            if(p==0) {current_pos2=0;current_pos1=0;}
           myservo.write(p)  ;                   // tell servo to go to position in variable 'pos'
           delay(1000);   // waits 15 ms for the servo to reach the position
         // p/180*1960+20
          }}
     if(exitt )
     { 
      digitalWrite(buzzer, HIGH);
      delay(15);
      for (sq = 0; sq <= 180; sq += 10) { // goes from 0 degrees to 180 degrees
       // in steps of 1 degree
           myservo2.write(sq);              // tell servo to go to position in variable 'pos'
             delay(60);                       // waits 15 ms for the servo to reach the position
           }
         for (sq = 180; sq >= 0; sq -= 10) { // goes from 180 degrees to 0 degrees
           myservo2.write(sq);              // tell servo to go to position in variable 'pos'
           delay(60);                       // waits 15 ms for the servo to reach the position
          }
    // here we work
       
       exitt=false;
       digitalWrite(buzzer, LOW);

      if (Serial.available() > 0) {
            data = Serial.read();
            if(data == '5')
            {
              digitalWrite(buzzer, LOW);
              exitt=false;
            }}
     }
     
     unsigned long currentMillis = millis();

  if (currentMillis - previousMillis >= interval) {
    // save the last time you blinked the LED
    previousMillis = currentMillis;
    // digitalWrite(buzzer, ;
    tm=true;
     }
}
