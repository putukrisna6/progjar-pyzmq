#!/usr/bin/env python3

import random, threading, zmq, time, sqlite3
B = 32

#region Helper

def ones_and_zeroes(digits):
    return bin(random.getrandbits(digits)).lstrip('0b').zfill(digits)

#endregion

#region Routine

def generator(zcontext, url):
    zsock = zcontext.socket(zmq.PUB)
    zsock.bind(url)
    while True:
        num = str(random.randint(0,2))
        zsock.send_string(num)
        time.sleep(0.01)

def executor(zcontext, in_url, out_url):
    isock = zcontext.socket(zmq.SUB)
    isock.connect(in_url)
    
    for opts in '0', '1', '2':
        isock.setsockopt_string(zmq.SUBSCRIBE, opts)

    osock = zcontext.socket(zmq.PUSH)
    osock.connect(out_url)

    while True:
        bits = isock.recv_string()
        osock.send_string('hai ' + bits)

def logger(zcontext, url):
    zsock = zcontext.socket(zmq.PULL)
    zsock.bind(url)
    while True:
        result = zsock.recv_string()
        print('logger: ' + result)

#endregion

def start_thread(function, *args):
    thread = threading.Thread(target=function, args=args)
    thread.daemon = True
    thread.start()

def main(zcontext):
    pubsub = 'tcp://127.0.0.1:6700'
    pushpull = 'tcp://127.0.0.1:6702'
    start_thread(generator, zcontext, pubsub)
    start_thread(executor, zcontext, pubsub, pushpull)
    start_thread(logger, zcontext, pushpull)

    time.sleep(5)

if __name__ == '__main__':
    main(zmq.Context())