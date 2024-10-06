#include <Servo.h>

Servo myservo;  // create Servo object to control a servo
// twelve Servo objects can be created on most boards

  // variable to store the servo position
char data;
bool exitt= false;
int current_pos1=0;
int current_pos2=0;
int buzzer=2;
void setup() {
  
  Serial.begin(9600);
  myservo.attach(9,600,2400);  // attaches the servo on pin 9 to the Servo object
  pinMode(buzzer,OUTPUT);
  digitalWrite(buzzer, LOW);

  }

void loop() {

      if(!exitt && current_pos2==0){
        
        for (int p=current_pos1; p <= 180; p += 5) { // goes from p degrees to 180 degrees
        // in steps of 5 degrees
          if (Serial.available() > 0) {
            data=Serial.read();
            if(data=='1') { exitt=true; current_pos1=p;  break; }}
            if(p==180) {current_pos1=180;current_pos2=180;}
          myservo.write(p) ;              // tell servo to go to position in variable 'p'
          delay(1000);                       // waits x ms for the servo to reach the position
          
        }}
        
      if(!exitt && current_pos1==180){
          for (int p=current_pos2; p >= 0; p -= 5) { // goes from p degrees to 0 degrees
           if (Serial.available() > 0) {
            data=Serial.read();
            if(data =='1') { exitt=true; current_pos2=p; break;}}
            if(p==0) {current_pos2=0;current_pos1=0;}
           myservo.write(p)  ;                   // tell servo to go to position in variable 'pos'
           delay(1000);   // waits 15 ms for the servo to reach the position
         // p/180*1960+20
          }}
     if(exitt)
     { 
      digitalWrite(buzzer, HIGH);
      delay(15);
    // here we work
      if (Serial.available() > 0) {
            data = Serial.read();
            if(data == '5')
            {
              digitalWrite(buzzer, LOW);
              exitt=false;
            }}
  
     }
     }
