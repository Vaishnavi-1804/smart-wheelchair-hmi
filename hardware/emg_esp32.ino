const int emgPin = 34;

void setup() {
  Serial.begin(115200);
}

void loop() {
  int emgValue = analogRead(emgPin);

  Serial.print("EMG:");
  Serial.println(emgValue);  // Clean format for software parsing

  delay(10);
}
