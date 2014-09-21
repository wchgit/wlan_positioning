#!/usr/bin/env python
import socket, fcntl, struct

def get_ip(ifname):
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    return socket.inet_ntoa(fcntl.ioctl(
            s.fileno(), 
            0x8915, 
            struct.pack('256s',ifname[:15])
            )[20:24])


def get_dir(angle):
    '''
    1 -> est
    2 -> south
    3 -> west
    4 -> north
    '''
    if angle>=45 and angle<135:
        return 1
    elif angle>=135 and angle<225:
        return 2
    elif angle>=225 and angle<315:
        return 3
    elif angle>=315 and angle<360:
        return 4
    elif angle>=0 and angle<45:
        return 4
    else:
        return -1
