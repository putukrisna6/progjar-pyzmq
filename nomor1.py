#!/usr/bin/env python3

import random, threading, zmq, time, sqlite3

#region Helper

def sqlHelper(n1, n2, num):
    db = sqlite3.connect('prereq/data.db')
    mod = str(len('FirstNameLastName') % 3)
    sql = "select count(*) from MOCKDATA where (ID>='{0}' AND ID<='{1}') AND '{3}' = '{2}';".format(n1, n1+n2, num, mod)
    cur = db.cursor()
    cur.execute(sql)
    value = int(cur.fetchone()[0])
    return value

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
        num = int(isock.recv_string())
        n1 = random.randint(1, 99000)
        n2 = random.randint(1, 1000)
        value = sqlHelper(n1, n2, num)

        res = 'n1=' + str(n1) + ', n2=' + str(n2) + ', num=' + str(num) + ', hasil=' + str(value) 
        osock.send_string(res)

def logger(zcontext, url):
    zsock = zcontext.socket(zmq.PULL)
    zsock.bind(url)
    while True:
        result = zsock.recv_string()
        print(result)

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
