import io
import socket
import struct
import sys

def take_remote_photo():
    # On robo_plot
    try:
        socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    except socket.error as msg:
        print('Failed to create socket. Error code: ' + str(msg[0]) + ' , Error message : ' + msg[1])
        sys.exit()

    print('Socket Created')

    HOST = 'robo-plot'
    PORT = 8888

    try:
        remote_ip = socket.gethostbyname(HOST)
    except socket.gaierror():
        print
        'Hostname could not be resolved. Exiting'
        sys.exit()

    # Connect to remote server (other pi)
    socket.connect((remote_ip, PORT))

    print
    'Socket connected to ' + HOST + ' on ip ' + remote_ip

    # Send request to remote pi
    message = 'Take_Photo'

    try:
        socket.sendall(message)
    except socket.error:
        # Send failed
        print
        'Send Failed'
        sys.exit()

    print
    'message sent succesfully'

    # Now recieve data
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

        # Rewind the stream, open it as an image with PIL and do some
        # processing on it
        image_stream.seek(0)
        image = cv2.imread(image_stream)
        print('Image is %dx%d' % image.shape)
        cv2.imshow("Received Image", image)

    socket.close()