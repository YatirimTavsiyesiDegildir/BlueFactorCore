import http.server
import socketserver
import io
import cgi
import os
import threading

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


# Create an object of the above class
handler_object = MyHttpRequestHandler

with socketserver.TCPServer(("", PORT), handler_object) as httpd:
    # Star the server
    httpd.serve_forever()


def display_title():
    os.system("clear")
    print("\t**********************************************")
    print("\t***  BlueFactor - 2FA Bluetooth Encryptor  ***")
    print("\t***  BlueFactor - 2FA Bluetooth Encryptor  ***")
    print("\t**********************************************")


def get_user_choice():
    print("\n[1] Create encrypted folder.")
    print("[2] Decrypt folder.")
    print("[q] Quit.")

    return input("What would you like to do? ")


def encrypt_sequence():
    password = input("Enter password: ")
    size = input(" Enter size for the file")
    keyname = input(" Enter key file name")
    os.system("veracrypt --create test.vc --password %s --hash sha512 --encryption AES --create-keyfile %s --volume-type normal --pim 0 --filesystem FAT --size %s --force" % (password, keyname, size))


def decrypt_sequence():
    # to do
    return 0


choice = ""
display_title()

while choice != "q":
    choice = get_user_choice()

    if choice == "1":
        encrypt_sequence()
    elif choice == "2":
        decrypt_sequence()
    elif choice == "q":
        print("\nThanks for using BlueFactor!")
    else:
        print("\nUnknown choice.")
