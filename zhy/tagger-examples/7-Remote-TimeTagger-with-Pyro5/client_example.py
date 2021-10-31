"""
This is an example on how to connect and control the Time Tagger remotely using Pyro5.

See the tutorial article in the Time Tagger's Documentation:
https://www.swabianinstruments.com/static/documentation/TimeTagger/tutorials/TimeTaggerRPC.html

This example requires Pyro5 package that can be installed as:
    > pip install Pyro5

How to start this example:

    1. Start the server:
        > python server_example.py
        
    2. Run this example:
        > python client_example.py

"""
import base64
import io
import numpy as np
import matplotlib.pyplot as plt

try:
    import Pyro5.api
except ModuleNotFoundError:
    import sys
    print('Please install Pyro5 module. "python -m pip install Pyro5"')
    sys.exit()

def load_numpy_array(classname, data):
    assert classname == 'numpy.ndarray'
    buffer = io.BytesIO(base64.b64decode(data['data'].encode('ASCII')))
    return np.load(buffer, allow_pickle=False)

# Register numpy.ndarray deserializer with Pyro5
Pyro5.api.register_dict_to_class(classname='numpy.ndarray', converter=load_numpy_array)

TimeTagger = Pyro5.api.Proxy("PYRO:TimeTagger@localhost:23000")

# Create Time Tagger
tagger = TimeTagger.createTimeTagger()
tagger.setTestSignal(1, True)
tagger.setTestSignal(2, True)

print('Time Tagger serial:', tagger.getSerial())

hist = TimeTagger.Correlation(tagger, 1, 2, binwidth=2, n_bins=2000)
hist.startFor(int(10e12), clear=True)

fig, ax = plt.subplots()
# The time vector is fixed. No need to read it on every iteration.
x = hist.getIndex()
line, = ax.plot(x, x * 0)
ax.set_xlabel('Time (ps)')
ax.set_ylabel('Counts')
ax.set_title('Correlation histogram via Pyro-RPC')
while hist.isRunning():
    y = hist.getData()
    line.set_ydata(y)
    ax.set_ylim(np.min(y), np.max(y))
    plt.pause(0.1)

# Cleanup
TimeTagger.freeTimeTagger(tagger)
del hist
del tagger
del TimeTagger
