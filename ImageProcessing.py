from PIL import Image
import numpy as np
import math

def compute_weighted_centroid(lightnesses):
    num_elements = lightnesses.shape
    x = np.arange(num_elements[0])
    y=lightnesses.sum()

    flt_centroid = np.mean(lightnesses * x)

    if flt_centroid != flt_centroid:
        return flt_centroid
    else:
        return int(flt_centroid)



img = Image.open('C:/Users/Hannah/Documents/Hackspace/CameraPic/Test2.png')
#img = Image.open('C:/Users/Hannah/Documents/Hackspace/CameraPic/greentriangle.jpg')

img = img.convert('L')
#img.show()
print("Size of image is:")
size = img.size
print(img.format, img.size, img.mode)

pixels = np.array(img.getdata())

np.savetxt('test.txt', pixels)
width, height = img.size

average_index_rows = []
average_index_rows.append(int(width/2))
average_index_cols = []
average_index_cols.append(int(height/2))
tol = 20

for cc in range(0, width):
    min_index = max(0, average_index_cols[cc] - 20)
    max_index = min(height, average_index_cols[cc] + 20)
    sub_array = np.asarray(pixels[cc, min_index:max_index])
    y = sub_array.sum()
    next_centroid = compute_weighted_centroid((sub_array))
    if next_centroid!= next_centroid:
        break
    else:
        average_index_cols.append(next_centroid)


for rr in range(0, height):
    min_index = max(0, average_index_rows[rr]-20)
    max_index = min(height, average_index_rows[rr]+20)
    sub_array = pixels[min_index:max_index, rr]
    next_centroid = compute_weighted_centroid((sub_array))
    if next_centroid!= next_centroid:
        break
    else:
        average_index_rows.append(next_centroid)



img = img.convert('RGB')
img_pixel = img.load()

for rr in range(1, len(average_index_rows)):
    if average_index_rows[rr] != -1:
        current_average_pixel = average_index_rows[rr]

        for pixel in range(-3,3):
            if (current_average_pixel+pixel > 0) and (current_average_pixel+pixel < height):
                img_pixel[rr-1, current_average_pixel+pixel ] = (255,10,10)

for cc in range(1, len(average_index_cols)):
    if average_index_cols[cc] != -1:
        current_average_pixel = average_index_cols[cc]

        for pixel in range(-3,3):
            if (current_average_pixel+pixel > 0) and (current_average_pixel+pixel < width):
                img_pixel[current_average_pixel+pixel, cc-1 ] = (10,255,10)

img.show()