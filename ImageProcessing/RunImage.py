import ImageProcessing as IP


file_path = 'C:/Users/Hannah/Documents/Hackspace/CameraPic/Bend.jpg'
#file_path = 'C:/Users/Hannah/Documents/Hackspace/CameraPic/Test4.png'



a_image_processor = IP.ImageAnalyser(file_path, IP.Direction.North)
a_image_processor.AnalyseImage()

