from roboplot.core.encoders import AxisEncoder

#Create a new object of axis encoder type
EncX = AxisEncoder(pins=[22,23],positions_per_revolution=96,distance_per_revolution=8)

#run the second thread
EncX.start()

i = 0
while(i < 10000):
    print("{0:06}".format(EncX.GetPosition()), end='\r')
    i = i + 1

EncX.ExitThread()
print("Program Ended")
