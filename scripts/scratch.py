import os
import re
import glob

import roboplot.config as config
import roboplot.dottodot.number_recognition as number_recognition

test_data_directory = os.path.join(config.test_data_dir, 'number_recognition')
file_glob = os.path.join(test_data_directory, '*.jpg')
files = glob.glob(file_glob)

for img_file in files:
    img = number_recognition.read_image(img_file)
    number = number_recognition.recognise_rotated_number(img)
    old_filename = os.path.basename(img_file)
    match = re.match(r'(?P<numeric_value>\d+)_(?P<fontsize>\d+)pt_(?P<angle>\d+)deg_y(?P<spot_y>\d+)_x(?P<spot_x>\d+)',
                     old_filename)

    img = number_recognition.read_image(img_file)
    number = number_recognition.recognise_rotated_number(img)

    new_filename = '{}_{}pt_{}deg_y{}_x{}.jpg'.format(match.group('fontsize'),
                                                      match.group('fontsize'),
                                                      match.group('angle'),
                                                      round(number.dot_location_yx[0]),
                                                      round(number.dot_location_yx[1]))

    print('{} -> {}'.format(old_filename, new_filename))

    new_filepath = os.path.join(os.path.dirname(img_file), new_filename)
    # print(new_filepath)
    os.rename(img_file, new_filepath)
