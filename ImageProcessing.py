from PIL import Image
import numpy

img = Image.open('C:/Users/Hannah/Documents/Hackspace/CameraPic/Test2.png')
#img = Image.open('C:/Users/Hannah/Documents/Hackspace/CameraPic/greentriangle.jpg')

img = img.convert('L')
print("Size of image is:")
size = img.size
print(img.format, img.size, img.mode)
#img.show()

pixels = numpy.asarray(img)
width, height = img.size

average_index_rows = []
average_index_cols = []



for cc in range(0, width):
    indices = numpy.where(pixels[:,cc] > 130)
    total_white_index = indices[0].sum()
    total_white_pixels = len(indices[0])
    if total_white_pixels !=0:
        average_index_cols.append(total_white_index/total_white_pixels)
    else:
        average_index_cols.append(-1)


for rr in range(0, height):
    indices = numpy.where(pixels[rr] > 130)
    total_white_index = indices[0].sum()
    total_white_pixels = len(indices[0])
    if total_white_pixels !=0:
        average_index_rows.append(total_white_index/total_white_pixels)
    else:
        average_index_rows.append(-1)



img = img.convert('RGB')
img_pixel = img.load()

for rr in range(0, height):
    if average_index_rows[rr] != -1:
        current_average_pixel = average_index_rows[rr]

        for pixel in range(-3,3):
            if (current_average_pixel+pixel > 0) and (current_average_pixel+pixel < height):
                img_pixel[current_average_pixel+pixel, rr] = (255,10,10)
    else:
        x=0


#for cc in range(0, width):
#    if average_index_cols[cc] != -1:
#        current_average_pixel = average_index_cols[cc]
#
#        for pixel in range(-3,3):
#            if (current_average_pixel+pixel > 0) and (current_average_pixel+pixel < width):
#                img_pixel[cc, current_average_pixel+pixel ] = (10,255,10)

img.show()