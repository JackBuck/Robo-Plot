from PIL import Image
import numpy



img = Image.open('C:/Users/Hannah/Documents/Hackspace/CameraPic/Test1.png')
#img = Image.open('C:/Users/Hannah/Documents/Hackspace/CameraPic/greentriangle.jpg')

img = img.convert('L')
print("Size of image is:")
size = img.size
print(img.format, img.size, img.mode)
#img.show()

pixels = numpy.asarray(img)
width, height = img.size

average_index =[]

for x_index in range(0, width):

    #Initialise counts.
    total_white_pixels = 0
    total_white_index = 0

    for y_index in range(0, height):

        #Check whether pixel qualifies as 'white'
        current_pixel = pixels[y_index][x_index]

        if current_pixel > 130:
            total_white_pixels +=  1
            total_white_index += y_index

    if total_white_pixels != 0:
        current_average_index = total_white_index/total_white_pixels
    else:
        current_average_index = -1
    average_index.append(current_average_index)


img = img.convert('RGB')
img_pixel = img.load()

for index in range(0, width):
    if average_index[index] != -1:
        current_average_pixel = average_index[index]

        for pixel in range(-3,3):
            if (current_average_pixel+pixel > 0) and (current_average_index+pixel < height):
                img_pixel[index, current_average_pixel+pixel] = (255,10,10)


img.show()