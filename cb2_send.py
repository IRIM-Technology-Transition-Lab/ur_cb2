import socket


def Deg2Rad(x):
    return 3.14 * x / 180

def Rad2Deg(x):
    return (x / 3.14) * 180

def drange(start, stop, step):
    r = start
    while r < stop:
        yield r
        r += step