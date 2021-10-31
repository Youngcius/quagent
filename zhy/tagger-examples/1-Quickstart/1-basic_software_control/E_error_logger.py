"""If errors occur during the operation of the Time Tagger, for example, the loss of the USB connection,
the Time Tagger will notify you. You can register a callback function to handle errors in the way
you like."""


import TimeTagger
from time import sleep

# In general, we can register any callable object as logger callback, so a simple function like
#
# def log_handler(level, msg):
#     print(msg)
#
# would suffice. Here, however, we define a callable class instance to keep track of the number
# of messages that have been sent.


class LogHandler:
    """A callable class that also keeps a state."""

    def __init__(self):
        # We want to count the number of messages to stop the program after two messages
        self.number_of_messages = 0

    def __call__(self, level, msg):
        # The __call__ method will make our class instance callable

        print("")
        # level represents different types of messages
        if level == TimeTagger.LOGGER_ERROR:
            print("An error occurred:")
        elif level == TimeTagger.LOGGER_WARNING:
            print("This is a Time Tagger warning:")
        elif level == TimeTagger.LOGGER_INFO:
            print("Just for your information:")
        else:
            print("This should not have happened...")
        print(msg)
        self.number_of_messages += 1


# Now we create an instance of the LogHandler class and register it as the logger callback
log_handler = LogHandler()
TimeTagger.setLogger(callback=log_handler)

# Create a TimeTagger instance to control your hardware
tagger = TimeTagger.createTimeTagger()

# To test our logger, we create an error by disconnecting the Time Tagger from the PC.
# If you re-plug it, the Time Tagger will send an info notification.
print("\n-> Please unplug the USB of your Time Tagger and reconnect it afterward.")
while log_handler.number_of_messages < 2:
    sleep(.1)
print("\nMission accomplished!")
