#!/usr/bin/env python3

import random, threading, zmq, time, sqlite3

#region Helper

def sqlHelper(n1, n2, num):
    db = sqlite3.connect('prereq/data.db')
    mod = str(len('FirstNameMiddleNameLastName') % 3)
    sql = "select count(*) from MOCKDATA where (ID>='{0}' AND ID<='{1}') AND '{3}' % 3 = '{2}';".format(n1, n1+n2, num, mod)
    cur = db.cursor()
    cur.execute(sql)
    value = int(cur.fetchone()[0])
    return value

#endregion

#region Routine

def generator(zcontext, executor_url, out_url):
    psock = zcontext.socket(zmq.REQ)
    psock.connect(executor_url)
    osock = zcontext.socket(zmq.PUSH)
    osock.connect(out_url)

    while True:
        num = str(random.randint(0,1))
        psock.send_string(num)
        time.sleep(0.01)

        repl = psock.recv_string()
        osock.send_string(repl)

def executor(zcontext, url):
    zsock = zcontext.socket(zmq.REP)
    zsock.bind(url)

    while True:
        num = int(zsock.recv_string())
        n1 = random.randint(1, 99000)
        n2 = random.randint(1, 1000)
        value = sqlHelper(n1, n2, num)
        
        res = 'n1=' + str(n1) + ', n2=' + str(n2) + ', num=' + str(num) + ', hasil=' + str(value) 
        zsock.send_string(res)

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
    reqrep = 'tcp://127.0.0.1:6701'
    pushpull = 'tcp://127.0.0.1:6702'
    start_thread(generator, zcontext, reqrep, pushpull)
    start_thread(executor, zcontext, reqrep)
    start_thread(logger, zcontext, pushpull)

    time.sleep(5)

if __name__ == '__main__':
    main(zmq.Context())