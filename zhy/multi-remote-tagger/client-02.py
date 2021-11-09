import matplotlib.pyplot as plt
from TimeTaggerRPC import client

from utils.hardware.host import ipv4, tagger_port

with client.createProxy(host=ipv4, port=tagger_port) as TT:
    tagger = TT.createTimeTagger()
    # tagger.setTestSignal(1, True)
    # tagger.setTestSignal(2, True)
    cnt = TT.Counter(tagger, 1, binwidth=int(1e6), n_values=1000)
    # hist = TT.Correlation(tagger, 1, 2, binwidth=5, n_bins=2000)
    # hist.startFor(int(10e12), clear=True)
    cnt.startFor(int(1e12), clear=True)
    # x = hist.getIndex()
    # while hist.isRunning():
    #     plt.pause(0.1)
    #     y = hist.getData()
    #     plt.cla()
    #     plt.plot(x, y)
    #
    # TT.freeTimeTagger(tagger)
    while cnt.isRunning():
        plt.pause(0.1)
        plt.cla()  # clear axes
        plt.plot(cnt.getData())

    TT.freeTimeTagger(tagger)
