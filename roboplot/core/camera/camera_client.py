import io
import socket
import struct
import sys

import cv2
import numpy as np


def take_remote_photo():
    # On robo_plot
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    except socket.error as msg:
        print('Failed to create socket. Error code: ' + str(msg[0]) + ' , Error message : ' + msg[1])
        sys.exit()

    print('Socket Created')

    HOST = 'HH_RPi_01'
    PORT = 8888

    try:
        remote_ip = socket.gethostbyname(HOST)
    except socket.oserror():
        print
        'Hostname could not be resolved. Exiting'
        sys.exit()

    # Connect to remote server (other pi)
    s.connect((remote_ip, PORT))

    print
    'Socket connected to ' + HOST + ' on ip ' + remote_ip

    # Send request to remote pi
    message = 'Take_Photo'

    try:
        s.sendall(bytes(message, 'UTF-8'))
    except socket.error:
        # Send failed
        print('Send Failed')
        sys.exit()

    print('message sent successfully')

    # Make a file-like object out of the connection
    connection = s.makefile('rwb')

    # Now receive data
    while True:
        # Read the length of the image as a 32-bit unsigned int. If the
        # length is zero, quit the loop

        image_len = struct.unpack('<L', connection.read(struct.calcsize('<L')))[0]
        if not image_len:
            break

        # Construct a stream to hold the image data and read the image
        # data from the connection
        image_stream = io.BytesIO()
        image_stream.write(connection.read(image_len))


        # Rewind the stream, open it as an image with open cv and do some
        # processing on it
        image_stream.seek(0)

        # convert image into numpy array
        data = np.fromstring(image_stream.getvalue(), dtype=np.uint8)
        # turn the array into a cv2 image
        image = cv2.imdecode(data, 1)

        return image
        s.close()
