import http.server
import socketserver
import io
import cgi
import os
import threading
import socket
from getpass import getpass

PORT = 8008


class MyHttpRequestHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/':
            self.path = 'keyfile'
        return http.server.SimpleHTTPRequestHandler.do_GET(self)

    def do_POST(self):
        r, info = self.deal_post_data()
        print(r, info, "by: ", self.client_address)
        f = io.BytesIO()
        if r:
            f.write(b"Success\n")
        else:
            f.write(b"Failed\n")
        length = f.tell()
        f.seek(0)
        self.send_response(200)
        self.send_header("Content-type", "text/plain")
        self.send_header("Content-Length", str(length))
        self.end_headers()
        if f:
            self.copyfile(f, self.wfile)
            f.close()

    def deal_post_data(self):
        ctype, pdict = cgi.parse_header(self.headers['Content-Type'])
        pdict['boundary'] = bytes(pdict['boundary'], "utf-8")
        pdict['CONTENT-LENGTH'] = int(self.headers['Content-Length'])
        if ctype == 'multipart/form-data':
            form = cgi.FieldStorage(fp=self.rfile, headers=self.headers, environ={
                                    'REQUEST_METHOD': 'POST', 'CONTENT_TYPE': self.headers['Content-Type'], })
            print(type(form))
            try:
                if isinstance(form["file"], list):
                    for record in form["file"]:
                        open("./%s" % record.filename,
                             "wb").write(record.file.read())
                else:
                    open("./%s" % form["file"].filename,
                         "wb").write(form["file"].file.read())
            except IOError:
                return (False, "Can't create file to write, do you have permission to write?")
        return (True, "Files uploaded")


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
