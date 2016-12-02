import ImageProcessing as IP


file_path = 'C:/Users/Hannah/Documents/Hackspace/CameraPic/bend5cm5.jpg'
#file_path = 'C:/Users/Hannah/Documents/Hackspace/CameraPic/Test4.png'
file_path = 'C:/Users/hh139711/Desktop/HackSpace/hackspace/Test6.png'


a_image_processor = IP.ImageAnalyser(file_path)
a_image_processor.AnalyseImage(IP.Direction.North)