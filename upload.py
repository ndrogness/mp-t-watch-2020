import os
import time
import serial

PORT = '/dev/ttyUSB0'
BAUD = 115200
CONNECT_WITH_AFTER_XFER = 'miniterm.py /dev/ttyUSB0 115200'

if not os.path.exists('manifest.txt'):
    print('Missing manifest.txt file, no files to upload')
    exit(-1)

if os.path.exists('upload-last.txt'):
    with open('upload-last.txt', 'r') as f:
        ut = f.read()
        upload_last_run = float(ut.rstrip())
else:
    upload_last_run = 0.0

transfer_error = False
did_transfer = False
with open('manifest.txt', 'r') as f:

    for ufile in f:
        ufile = ufile.rstrip()
        src_file, dst_file = ufile.split(',')
        if not os.path.exists(src_file):
            print('Upload file not found, cant upload:', src_file)
            continue
        # print(os.path.getmtime(src_file),'>',upload_last_run)
        if os.path.getmtime(src_file) > upload_last_run:
            cmd = 'ampy -p {} -b {} put {} {}'.format(PORT, BAUD, src_file, dst_file)
            print('Uploading:', src_file, '->', cmd)
            ecode = os.system(cmd)
            if ecode != 0:
                print('Transfer error')
                transfer_error = True
            else:
                did_transfer = True
        else:
            print('Skipping:', src_file)

if transfer_error is False:
    with open('upload-last.txt', 'w') as f:
        f.write('{}'.format(time.time()))

    if did_transfer is True:
        print('Resetting...')
        try:
            # cmd = 'ampy -p {} -b {} reset'.format(PORT, BAUD)
            # os.system(cmd)
            ecom = serial.Serial(port=PORT, baudrate=BAUD, timeout=2)
            ecom.write(b'\x03\x04')
            ecom.close()
        except:
            CONNECT_WITH_AFTER_XFER = ''

    if CONNECT_WITH_AFTER_XFER != '':
        os.system(CONNECT_WITH_AFTER_XFER)

