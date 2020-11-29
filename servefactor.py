import http.server
import socketserver
import io
import cgi
import os
import threading
import socket
from getpass import getpass
import logging

PORT = 8000
KEYFILE = "keyfile2"


class MyHttpRequestHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/':
            self.path = 'keyfile'
        return http.server.SimpleHTTPRequestHandler.do_GET(self)

    def do_POST(self):
        # <--- Gets the size of data
        content_length = int(self.headers['Content-Length'])
        # <--- Gets the data itself
        post_data = self.rfile.read(content_length)
        print(post_data)
        f = open(KEYFILE, "w")
        f.write(str(post_data)[2: -1])
        f.close()
        self.send_response(200)
        self.send_header("Content-type", "text/plain")
        self.end_headers()


def start_server():
    # Create an object of the above class
    handler_object = MyHttpRequestHandler

    with socketserver.TCPServer(("", PORT), handler_object) as httpd:
        # Star the server
        httpd.serve_forever()


daemon = threading.Thread(name='daemon_server',
                          target=start_server)
daemon.setDaemon(True)
daemon.start()

s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
s.connect(('8.8.8.8', 1))  # connect() for UDP doesn't send packets
ip = s.getsockname()[0] + ":" + str(PORT)


def display_title():
    os.system("clear")
    print("\t**********************************************")
    print("\t***       BlueFactor - 2FA Encryptor       ***")
    print("\t***           %s          ***" % (ip))
    print("\t**********************************************")


def get_user_choice():
    print("\n[1] Create encrypted folder.")
    print("[2] Decrypt folder.")
    print("[3] Unmount partition.")
    print("[q] Quit.")

    return input("What would you like to do? ")


def encrypt_sequence():
    folder = str.rstrip(input("Enter encrypted folder name: "))
    password = str.rstrip(getpass("Enter password: "))
    size = str.rstrip(input(" Enter size for the file: "))
    keyname = str.rstrip(input(" Enter key file name: "))
    os.system("veracrypt -t --create %s --password %s --hash sha512 --encryption AES --keyfiles %s --volume-type normal --pim 0 --filesystem FAT --size %s --force" %
              (folder, password, keyname, size))


def decrypt_sequence():
    mount = str.rstrip(input("Enter mount location: "))
    password = str.rstrip(getpass("Enter password: "))
    keyname = str.rstrip(input("Enter keyfile: "))
    os.system("veracrypt --mount %s --password %s --keyfiles %s" %
              (mount, password, keyname))


def unmount_sequence():
    os.system("veracrypt -d")


choice = ""
display_title()

while choice != "q":
    choice = get_user_choice()

    if choice == "1":
        encrypt_sequence()
    elif choice == "2":
        decrypt_sequence()
    elif choice == "3":
        unmount_sequence()
    elif choice == "q":
        print("\nThanks for using BlueFactor!")
    else:
        print("\nUnknown choice.")
