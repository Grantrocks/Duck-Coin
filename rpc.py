# import socket programming library
import socket

# import thread module
from _thread import *
import threading

print_lock = threading.Lock()

# thread function
def threaded(c):
	while True:
		data = c.recv(1024)
		if not data:
			print('Closed Connection')
			print_lock.release()
			break
		data=data.decode().split(",")
		# Handle Messages from client
		if data=="PING":
			c.send("PONG".encode())

	c.close()


def Main():
	host = ""
	port = 20000 # Specify which port to open
	s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	s.bind((host, port))
	print("socket binded to port", port)

	s.listen(5)
	print("socket is listening")

	while True:

		c, addr = s.accept()

		print_lock.acquire()
		print('Connected to :', addr[0], ':', addr[1])

		start_new_thread(threaded, (c,))
	s.close()


if __name__ == '__main__':
	Main()
