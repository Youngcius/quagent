"""
Data acquisition
---
Auto-configure available SPD-Tagger acquisition channels.
Control Tagger to acquire data and return it to users.
Default hardware link: 8 channels of one SNSPD are separately linked to 8 input channels of one Tagger.
"""
import TimeTagger as tt
from .globvar import *

if tagger is None and len(tt.scanTimeTagger()) != 0:
    print('tagger INITIALIZED')
    tagger = tt.createTimeTagger()

    # TODO: delete the following once in real usage
    # for i in range(1, 9):
    #     tagger.setTestSignal(i, True)

print('tagger global variable initialized')
print('tagger NOW: {}'.format(tagger))
