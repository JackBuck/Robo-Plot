import roboplot.core.hardware as hardware

EncX = hardware.x_axis_encoder

for i in range(10000):
    print("{0:06}".format(EncX.revolutions), end='\r')

EncX.exit_thread()
print("Program Ended")
