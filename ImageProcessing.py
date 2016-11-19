from PIL import Image
import numpy as np
import math

def compute_weighted_centroid(lightnesses):
    num_elements = lightnesses.shape
    x = np.arange(num_elements[0])
    is_white = lightnesses > 130
    num_white = sum(is_white)
    weighted = np.multiply(is_white,x)
    np.savetxt('weight.txt', weighted)
    if num_white == 0:
        return -1
    else:
        flt_centroid = sum(is_white * x)/num_white

    if flt_centroid == 0.0:
         return -1
    else:
        return int(flt_centroid)


img = Image.open('C:/Users/Hannah/Documents/Hackspace/CameraPic/Test4.png')
#img = Image.open('C:/Users/Hannah/Documents/Hackspace/CameraPic/greentriangle.jpg')

img = img.convert('L')
print("Size of image is:")
print(img.format, img.size, img.mode)

pixels = np.asarray(img)
width, height = img.size

average_index_rows = []
average_index_rows.append(int(width/2))
average_index_cols = []
average_index_cols.append(int(height/2))

count = 0
for cc in range(int(width/2), width):
    min_index = max(0, average_index_cols[count] - 10000)
    max_index = min(height, average_index_cols[count] + 10000)
    count += 1
    sub_array = pixels[min_index:max_index, cc]
    next_centroid = compute_weighted_centroid((sub_array))
    average_index_cols.append(next_centroid)

count = 0
for rr in range(int(height/2), height):
    min_index = max(0, average_index_rows[count]-10000)
    max_index = min(height, average_index_rows[count]+10000)
    count += 1
    sub_array = pixels[ rr, min_index:max_index]
    next_centroid = compute_weighted_centroid((sub_array))
    average_index_rows.append(next_centroid)

img = img.convert('RGB')
img_pixel = img.load()

for cc in range(1, len(average_index_cols)):
    if average_index_cols[cc] != -1:
        current_average_pixel = average_index_cols[cc]

        for pixel in range(-3,3):
            if (current_average_pixel+pixel > 0) and (current_average_pixel+pixel < width):
                img_pixel[ int(width/2)+cc-1 ,current_average_pixel+pixel] = (10,255,10)

for rr in range(1, len(average_index_rows)):
    if average_index_rows[rr] != -1:
        current_average_pixel = average_index_rows[rr]
        for pixel in range(-3,3):
            if (current_average_pixel+pixel > 0) and (current_average_pixel+pixel < height):
                index = int(height/2)+rr-1
                img_pixel[current_average_pixel+pixel, int(height/2)+rr-1] = (255,10,10)

img.show()