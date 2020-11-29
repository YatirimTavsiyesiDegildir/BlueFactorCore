import http.server
import socketserver
import io
import cgi
import os
import threading
import socket
from getpass import getpass
import logging
import secrets

PORT = 7002
KEYFILE = "keyfile.key"


class MyHttpRequestHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        if os.path.isfile(KEYFILE) and self.path == '/':
            self.path = KEYFILE
            return http.server.SimpleHTTPRequestHandler.do_GET(self)
        self.send_response(404)
        self.send_header("Content-type", "text/plain")
        self.end_headers()
        return False

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
    keyfileText = secrets.token_urlsafe(10000)
    f = open(KEYFILE, "w")
    f.write(keyfileText)
    f.close()

    folder = str.rstrip(input("Enter encrypted folder name: "))
    password = str.rstrip(getpass("Enter password: "))
    size = str.rstrip(input(" Enter size for the file: "))
    os.system("veracrypt -t --create %s --password %s --hash sha512 --encryption AES --keyfiles %s --volume-type normal --pim 0 --filesystem FAT --size %s --force" %
              (folder, password, KEYFILE, size))
    print("Please upload the key to the app.")
    inp = input("\n[y] Key uploaded.")
    while inp != "y":
        inp = input("\n[y] Key uploaded.")
    os.system("rm " + KEYFILE)
    print("Done!")


def decrypt_sequence():
    print("Please upload the key from the app.")
    inp = input("\n[y] Key uploaded.")
    while inp != "y":
        inp = input("\n[y] Key uploaded.")
    mount = str.rstrip(input("Enter mount name: "))
    password = str.rstrip(getpass("Enter password: "))
    os.system("veracrypt --mount %s --password %s --keyfiles %s" %
              (mount, password, KEYFILE))
    os.system("rm " + KEYFILE)


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
