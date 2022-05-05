#!/usr/bin/env python3

import random, threading, zmq, time, sqlite3
B = 32

#region Helper

def ones_and_zeroes(digits):
    return bin(random.getrandbits(digits)).lstrip('0b').zfill(digits)

#endregion

def start_thread(function, *args):
    thread = threading.Thread(target=function, args=args)
    thread.daemon = True
    thread.start()

def main(zcontext):
    pubsub = 'tcp://127.0.0.1:6700'
    pushpull = 'tcp://127.0.0.1:6702'
    time.sleep(5)

if __name__ == '__main__':
    main(zmq.Context())