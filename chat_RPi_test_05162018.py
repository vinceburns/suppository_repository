import threading
import Queue
import socket
#INITIALIZATION FOR ALL GPIO SHITTTT
import RPi.GPIO as GPIO
gpioPin = 4
GPIO.setmode(GPIO.BCM)
GPIO.setup(gpioPin, GPIO.OUT, initial = GPIO.LOW)
#JUST THOSE 3 LINEZZZ
our_queue = Queue.Queue()
addr = ("10.0.0.193",7105)
class KeyboardThread(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
        self.name = 'KeyboardThread'

    def run(self):
        while True:
            try:
                input = raw_input()
                if input:
                    self.parse_input(input)
            except EOFError:
                return
    def parse_input(self,input):
        our_queue.put(input)
        
        
class ListeningThread(threading.Thread):
    def __init__(self, our_socket):
        threading.Thread.__init__(self)
        self.name = 'ListeningThread'
        self.s = our_socket
    def run(self):
        while True:
            data,recv_addr = self.s.recvfrom(1024)
            #Limitation. only 1024 byte buffer. Wonder if we could do more? Never tried it
            """Sudo code for later?
            if addr !in self.future_dick:
                add it
            """
            print "[%s]:%s" % (str(recv_addr),data)
            if data == 'setHIGH':
                GPIO.output(gpioPin, GPIO.HIGH)
            if data == 'setLOW':
                GPIO.output(gpioPin, GPIO.LOW)
		
		
class SendingThread(threading.Thread):
    def __init__(self, our_socket):
        threading.Thread.__init__(self)
        self.name = 'SendingThread'
        self.s = our_socket
    def run(self):
        while True:
            job = our_queue.get()
            self.s.sendto(job,addr)
            our_queue.task_done()
            
		
        
def main():
    UDP_PORT = int(raw_input("Please enter port that you have forwarding set up on: "))
    try:
        our_sock = socket.socket(socket.AF_INET,
                         socket.SOCK_DGRAM)
        #taking it as raw should implement as an argument.
        
        our_sock.bind(("",UDP_PORT))
        #sock.bind takes a Tuple of (Host,Port), "" takes all available hosts (for us i think its just Internal/external IP.)
        print "Socket open! Listening..."
    except:
        print "Couldn't open socket. Probably have a different server running on that port. Program Exit."
        return 0
    #we finna pass this socket around to send and receive data on. We should eventually pass a log file around/ Dictionary of addresses joining our chat???
    thread_pool =[KeyboardThread(),SendingThread(our_sock),ListeningThread(our_sock)]    
    for t in thread_pool:
        t.start()
    while True:
        for t in thread_pool:
            if not t.is_alive():
                print "%s Thread has died ending" % (t.name)
                return 0
main()
            
