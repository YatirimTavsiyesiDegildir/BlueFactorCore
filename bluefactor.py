import os
import sys
import bluetooth

keyfileName = "keyfile"
addr = "80:2B:F9:1A:71:00"


def display_title():
    os.system("clear")
    print("\t**********************************************")
    print("\t***  BlueFactor - 2FA Bluetooth Encryptor  ***")
    print("\t**********************************************")


def get_user_choice():
    print("\n[1] Create encrypted folder.")
    print("[2] Decrypt folder.")
    print("[q] Quit.")

    return input("What would you like to do? ")


def encrypt_sequence():
    def get_address():
        target_name = input("Enter device name: ")
        target_adress = None

        nearby_devices = bluetooth.discover_devices()

        for bdaddr in nearby_devices:
            if target_name == bluetooth.lookup_name(bdaddr):
                target_adress = bdaddr
                break

        if target_adress is not None:
            print("Found target bluetooth device with adress", target_adress)
            message = open(keyfileName, "r").read()
            # connect(target_adress, message)
            connect_2(target_adress)
        else:
            print("Could not find target device nearby")

    def connect_2(addr):
        service_matches = bluetooth.find_service(address=addr)

        if len(service_matches) == 0:
            print("Couldn't find the SampleServer service.")
            sys.exit(0)

        first_match = service_matches[0]
        print(first_match)
        port = first_match["port"]
        name = first_match["name"]
        host = first_match["host"]

        print("Connecting to \"{}\" on {}".format(name, host))

        # Create the client socket
        sock = bluetooth.BluetoothSocket(bluetooth.RFCOMM)
        sock.connect((host, port))

        print("Connected. Type something...")
        while True:
            data = input()
            if not data:
                break
            sock.send(data)

        sock.close()

    def connect(addr, message):
        sock = bluetooth.BluetoothSocket(bluetooth.L2CAP)
        sock.connect((addr, 0x1001))
        # keyfile = open(keyfileName, "r")
        sock.send(message)

    def await_key_request():
        server_sock = bluetooth.BluetoothSocket(bluetooth.L2CAP)

        port = 0x1001

        server_sock.bind(("", port))
        server_sock.listen(1)

        #uuid = "94f39d29-7d6d-437d-973b-fba39e49d4ef"
        # bluetooth.advertise_service(server_sock, "SampleServerL2CAP",
        #                            service_id=uuid, service_classes = [uuid])

        client_sock, address = server_sock.accept()
        print("Accepted connection from", address)

        data = client_sock.recv(1024)
        print("Data received:", str(data))

        while data != "send-me-key":
            client_sock.send("Echo =>", str(data))
            data = client_sock.recv(1024)
            print("Data received:", str(data))

        client_sock.close()
        server_sock.close()
        connect(address, "hi")

    def encrypt():
        password = input("Enter password: ")
        os.system("veracrypt -t -c test")

    # await_key_request()
    # encrypt()
    get_address()
    print("Done.")


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
