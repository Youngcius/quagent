"""In this example we look at methods that provide information on the Time Tagger(s) in your lab."""

import sys
import TimeTagger

available_taggers = TimeTagger.scanTimeTagger()
if available_taggers:
    print("\nTime Taggers available via TimeTagger.scanTimeTagger():")
    print(available_taggers)
else:
    print("There are no Time Taggers available. Connect one and retry.")
    exit()

tagger = TimeTagger.createTimeTagger()

print("\nYour Time Tagger model via tagger.getModel():")
print(tagger.getModel())

print("\nYour Time Tagger serial number via tagger.getSerial():")
print(tagger.getSerial())

print("\nAcquiring internal sensor data of your Time Tagger via tagger.getSensorData().")
if tagger.getModel() == "Time Tagger Ultra":
    print("\nSensor data:")
    print(tagger.getSensorData())
else:
    print("\nThe {}s do not support sensor readout.".format(tagger.getModel()))

print("\nFull Time Tagger Configuration via tagger.getConfiguration():")
print(tagger.getConfiguration())
