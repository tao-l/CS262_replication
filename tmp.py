import threading
import queue
from time import sleep

e = threading.Event()
print("e.wait return:", e.wait(1))

e.set()
print("e.wait return", e.wait(2))

def timer_func():
    print("  timer func")

S = threading.Timer(10, timer_func)
S.start()

q = queue.Queue()

def put_to_queue(q):
    sleep(2)
    q.put("hello world")

threading.Thread(target=put_to_queue, args=(q,)).start()

a = q.get()
print(a)

good = threading.Event()

def set_good(t):
    sleep(t)
    good.set()

threading.Thread(target=set_good, args=(5,)).start()

print("th1")

threading.Thread(target=set_good, args=(4,)).start()

good.wait()
print("Good!")

