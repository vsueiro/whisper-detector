# This code uses the DHT11 Python library:
# https://pypi.org/project/dht11/



# import tools for humidity sensor
import RPi.GPIO as GPIO
import dht11

# import tool for sleep delays
import time

# import some math to get median humidity from multiple readings as a baseline
import statistics

# import tool for creating timestamps for readings and CSV filename
from datetime import datetime



# initialize GPIO:
GPIO.setmode(GPIO.BCM) # use GPIO numbers instead of sequential pin numbers

# assign sensor to GPIO 21 (change this according to your setup)
instance = dht11.DHT11(pin=21)

# initialize variables:
queue = [] # create empty list to house humidity readings
previous = 0 # create previous variable to house previous humidity reading
current = 0 # create current variable and set it to 0, until first reading
baseline = 0 # create baseline variable and set it to 0, until first reading
threshold = 2 # create baseline slightly above ambient humidity (to ignore small increases)
icon = '' # create string to house whispering pause symbol for the chart



# initialize variables for CSV (spreadsheet file to store sensor readings):
timestamp = datetime.now().strftime("%Y-%m-%dT%I-%M-%S-%p") 
filename = timestamp + '.csv'
headers = [
  'datetime',
  'humidity',
  'baseline',
  'pause'
]



# create empty CSV file (with header):
with open(filename, 'a') as csv:
  
  # write comma-separated column names
  csv.write( ",".join(headers) )
  
  # append a new line
  csv.write("\n")



# creates legend for our emoji chart
print("""

How to read the chart?

○○○○○○○ ← Circles mean more humidity
○○○○○○○●●●● ← Filled circles mean humidity is slightly above ambient baseline
○○○○○○○●●●● 75% ← Number represents humidity percentage
○○○○○○○●●● 70% ★ ← Star appears on the beginning of whispering pause*

*After crossing ambient baseline, first decrease in humidity is considered a whispering pause.

""")



# loop forever
while True:

  # read values from sensor
  result = instance.read()
  
  # check if reading was succesful
  if result.is_valid():
  
    # if it’s the first reading
    if baseline <= 0:
  
      # remove decimal places from humidity reading
      current = round(result.humidity)
  
    # if there is a previous reading (to set baseline humidity)
    if baseline > 0:
  
      # if there is a previous reading, store it on the previous variable
      if current > 0:
        previous = current
  
      # remove decimal places from humidity reading
      current = round(result.humidity)



      # if humidity is decreasing ↘ (and is above baseline)
      if previous > current and previous > baseline: 
  
        # prevent sequential whispering pauses to be triggered
        if has_just_triggered:
  
          # do not trigger
          pass
          
        # trigger pause
        else:
  
          # add symbol to represent a whispering pause was triggered
          icon = '★'
  
          # prevent it to trigger again
          has_just_triggered = True



      # if humidity is increasing ↗ (and is above baseline)
      if previous < current and previous > baseline: 

        # allow it to trigger pause again, once humidity drops
        has_just_triggered = False
  


      # draw “bar chart” (one circle per % point) with baseline:
      if current >= baseline:
        bar = '○' * baseline + '●' * (current - baseline)
      else:
        bar = '○' * current

      label = str(current) + '%'

      # print a new bar on the “chart”
      print(bar, label, icon)




      # write new entry on CSV file
      with open(filename, 'a') as csv:
      
        row = [
          datetime.now().isoformat(), # ISO format for currrent date and time
          str( current ), # turns current humidity from integer into text
          str( baseline ), # turns current baseline (ambient humidity + threshold) into text
          'pause' if icon else '' # if icon is set to indicate a whispering pause, write 'pause' 
        ]
 
        # write comma-separated row values
        csv.write( ",".join(row) )
  
        # append a new line
        csv.write("\n")  



      # remove icon after whispering pause was triggered
      icon = ''



    # calculate baseline humidity:
    queue.append(current) # add one more reading from the sensor to queue
    queue = queue[-50:] # limit queue to the last 50 readings
    baseline = statistics.median(queue) # get median reading (to remove outliers)
    baseline = baseline + threshold # increases baseline to avoid flunctiations on ambient humidity
    baseline = round(baseline) # makes sure baseline is an integer



  # give it a short break between loops
  time.sleep(1)