// www.elegoo.com
// 2018.10.24
/*
  LED1 should be lit, showing power. LED2 indicates sound input, and the sensitivity is adjusted by potentiometer.
  There is a tiny screw on the blue potentiometer block that you can use for adjustment. Turning that
  clockwise lowers the potentiometer value, while counter-clockwise raises the potentiometer value.
  Use the potentiometer to adjust the Sound Sensor sensitivity. Turn the potentiometer
  several rotations until you see the LED2 extinguish (or just faintly blink). This might be slightly greater than
  500, if you are also watching Serial Monitor (inital adjustment), or, Serial Plotter (the latter is prefererd for observation).
  Special thanks to user CRomer, for his input and hard work!
*/

int  sensorAnalogPin = A0;    // Select the Arduino input pin to accept the Sound Sensor's analog output 
int  sensorDigitalPin = 3;    // Select the Arduino input pin to accept the Sound Sensor's digital output
int  analogValue = 0;         // Define variable to store the analog value coming from the Sound Sensor
int  digitalValue;            // Define variable to store the digital value coming from the Sound Sensor
int  Led13 = 13;              // Define LED port; this is the LED built in to the Arduino (labled L)
                              // When D0 from the Sound Sensor (connnected to pin 3 on the
                              // Arduino) sends High (voltage present), L will light. In practice, you
                              // should see LED13 on the Arduino blink when LED2 on the Sensor is 100% lit.
                              

void setup()
{
  Serial.begin(9600);               // The IDE settings for Serial Monitor/Plotter (preferred) must match this speed
  pinMode(sensorDigitalPin,INPUT);  // Define pin 3 as an input port, to accept digital input
  pinMode(Led13,OUTPUT);            // Define LED13 as an output port, to indicate digital trigger reached
}

void loop(){
  analogValue = analogRead(sensorAnalogPin); // Read the value of the analog interface A0 assigned to digitalValue 
  digitalValue=digitalRead(sensorDigitalPin); // Read the value of the digital interface 3 assigned to digitalValue 
  Serial.println(analogValue); // Send the analog value to the serial transmit interface
  
  if(digitalValue==HIGH)      // When the Sound Sensor sends signla, via voltage present, light LED13 (L)
  {
    digitalWrite(Led13,HIGH);
  }
  else
  {
    digitalWrite(Led13,LOW);
  }
  
  delay(50);                  // Slight pause so that we don't overwhelm the serial interface
}


/*
  Arduino Sound Sensor Reader - V2 (Amplitude)
 
  This sketch measures the peak-to-peak (P-P) amplitude of the
  analog signal, which is a much more reliable way to measure
  sound "spikes" than a single reading.

  It finds the min and max value over a short sampling window
  and sends the difference (P-P amplitude).
*/
/*
// Elegoo Big Sound Sensor - Analog Read + Software Threshold + LED
const int AO_PIN = A0;     // Analog output from module
const int LED_PIN = 6;     // Optional: indicator LED
int baseline = 0;

void setup() {
  Serial.begin(115200);
  pinMode(LED_PIN, OUTPUT);

  // Quick baseline calibration (quiet room)
  long sum = 0;
  const int samples = 200;
  for (int i = 0; i < samples; i++) {
    sum += analogRead(AO_PIN);
    delay(2);
  }
  baseline = sum / samples;
  Serial.print("Baseline: ");
  Serial.println(baseline);
}

void loop() {
  // Read several samples to smooth noise (simple moving average)
  const int N = 16;
  long acc = 0;
  for (int i = 0; i < N; i++) {
    acc += analogRead(AO_PIN);
    delayMicroseconds(500);
  }
  int value = acc / N;

  // Compute absolute deviation from baseline
  int deviation = abs(value - baseline);

  // Software threshold (tune to your room)
  const int THRESH = 30;  // raise if too sensitive, lower if not sensitive enough

  // Light LED if noise exceeds threshold
  digitalWrite(LED_PIN, deviation > THRESH ? HIGH : LOW);

  // Great for Tools → Serial Plotter (plot value & threshold line)
  Serial.print(value);
  Serial.print(",");
  Serial.print(baseline + THRESH);
  Serial.print(",");
  Serial.println(baseline - THRESH);

  delay(5);
}*/