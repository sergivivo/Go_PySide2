import threading
import time

class Pene():
    def __init__(self):
        self.sem = threading.Semaphore(0)
        t = threading.Thread(target=self.prueba)
        t.daemon = True
        t.start()

    def prueba(self):
        while True:
            print("Tuputamadre")
            time.sleep(1)
            self.sem.acquire()

if __name__ == "__main__":
    Pene()
    input()
