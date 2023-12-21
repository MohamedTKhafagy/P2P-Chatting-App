
from socket import *
import threading
import logging
import colorama
from colorama import Fore, Back, Style

# main process of the peer
class peerMain:

    # peer initializations
    def __init__(self):
        # ip address of the server
        self.serverName = input(Fore.BLUE + Style.BRIGHT + "Enter IP address of server: ")
        # port number of the server
        self.serverPort = 15600
        # tcp socket connection to server
        self.tcpClientSocket = socket(AF_INET, SOCK_STREAM)
        self.tcpClientSocket.connect((self.serverName, self.serverPort))
        # initializes udp socket which is used to send hello messages
        self.udpClientSocket = socket(AF_INET, SOCK_DGRAM)
        # udp port of the server
        self.serverUDPPort = 15500
        # login info of the peer
        self.loginCredentials = (None, None)
        # online status of the peer
        self.isOnline = False
        # timer initialization
        self.timer = None

        choice = "0"
        print(Style.RESET_ALL)
        # log file initialization
        logging.basicConfig(filename="peer.log", level=logging.INFO)
        # as long as the user is not logged out, asks to select an option in the menu
        while choice != "3":
            # menu selection prompt
            if self.isOnline:
                print("Choose: \nCreate account: Enter 1\nLogin: Enter 2\nLogout: Enter 3\nCheck Online Users: Enter 4")
                choice = input(Fore.BLUE + Style.BRIGHT + ">")
                print(Style.RESET_ALL)
            else:
                print("Choose: \nCreate account: Enter 1\nLogin: Enter 2\nExit: Enter 3\nCheck Online Users: Enter 4")
                choice = input(Fore.BLUE + Style.BRIGHT + ">")
                print(Style.RESET_ALL)
            # if choice is 1, creates an account with the username
            # and password entered by the user
            if choice == "1":
                username = input(Fore.BLUE + Style.BRIGHT + "username: ")
                print(Fore.YELLOW + Style.BRIGHT + "Password must be 9 characters at least")
                print(Fore.YELLOW + Style.BRIGHT + "Password must have one of the following symbols: !@#$%^&*()_+\\-=[\\]{};':\"\\|,.<>/?~")
                print(Fore.YELLOW + Style.BRIGHT + "Password must have an uppercase letter")
                print(Fore.YELLOW + Style.BRIGHT + "Password must have at least one digit")
                print(Style.RESET_ALL)
                password = input(Fore.BLUE + Style.BRIGHT + "password: ")
                print(Style.RESET_ALL)
                symbols = "!@#$%^&*()_+\\-=[\\]{};':\"\\|,.<>/?~"

                # some conditions to make sure that the password is strong
                if (
                        len(password) >= 9 and
                        any(char in symbols for char in password) and
                        any(char.isupper() for char in password) and
                        any(char.isdigit() for char in password)):
                    self.createAccount(username, password)
                else:
                    print(Fore.RED + "The password entered is weak")
                    print(Style.RESET_ALL)


            # if choice is 2 and user is not logged in, asks for the username
            # and the password to login
            elif choice == "2" and not self.isOnline:
                username = input(Fore.BLUE + Style.BRIGHT + "username: ")
                password = input(Fore.BLUE + Style.BRIGHT + "password: ")
                print(Style.RESET_ALL)


                status = self.login(username, password)
                # is user logs in successfully, peer variables are set
                if status == 1:
                    self.isOnline = True
                    self.loginCredentials = (username, password)
                    # creates the server thread for this peer, and run
                    # hello message is sent to server
                    self.sendHelloMessage()
            # if choice is 3 and user is logged in, then user is logged out
            # and peer variables are set, and server and client sockets are closed
            elif choice == "3" and self.isOnline:
                self.logout(1)
                self.isOnline = False
                self.loginCredentials = (None, None)
                print(Fore.GREEN+"Logged out successfully")
                print(Fore.YELLOW + Style.BRIGHT + "Goodbye!!")
                print(Style.RESET_ALL)
            # is peer is not logged in and exits the program
            elif choice == "3":
                self.logout(2)
                print(Fore.YELLOW + Style.BRIGHT + "Goodbye!!")
                print(Style.RESET_ALL)
            elif choice == "4":
                self.checkOnline()
            # if choice is cancel timer for hello message is cancelled
        # socket of the client is closed
        self.tcpClientSocket.close()

    # account creation function
    def createAccount(self, username, password):
        # SIGNUP message to create an account is composed and sent to server
        # if response is SUCCESS then informs the user that the account is created
        # if response is USERNAME-EXISTS then informs the user to use another username
        message = "SIGNUP " + username + " " + password
        logging.info("Send to " + self.serverName + ":" + str(self.serverPort) + " -> " + message)
        self.tcpClientSocket.send(message.encode())
        response = self.tcpClientSocket.recv(1024).decode()
        logging.info("Received from " + self.serverName + " -> " + response)
        if response == "SUCCESS":
            print(Fore.GREEN + "Account created...")
            print(Style.RESET_ALL)
        elif response == "USERNAME-EXISTS":
            print(Fore.RED + "Username is taken please use another one...")
            print(Style.RESET_ALL)

    # login function
    def login(self, username, password):
        # a login message is composed and sent to server
        # an integer is returned according to each response
        message = "LOGIN " + username + " " + password
        logging.info("Send to " + self.serverName + ":" + str(self.serverPort) + " -> " + message)
        self.tcpClientSocket.send(message.encode())
        response = self.tcpClientSocket.recv(1024).decode()
        logging.info("Received from " + self.serverName + " -> " + response)
        if response == "SUCCESS":
            print(Fore.GREEN+"Logged in successfully...")
            print(Style.RESET_ALL)
            return 1
        elif response == "USER-NOT-EXIST":
            print(Fore.RED+"Account does not exist...")
            print(Style.RESET_ALL)
            return 0
        elif response == "USER-ONLINE":
            print(Fore.RED+"Account is already online...")
            print(Style.RESET_ALL)
            return 2
        elif response == "WRONG-PASSWORD":
            print(Fore.RED+"Password entered is wrong...")
            print(Style.RESET_ALL)
            return 3

    # logout function
    def logout(self, option):
        # a logout message is composed and sent to registry
        # timer is stopped
        if option == 1:
            message = "LOGOUT " + self.loginCredentials[0]
            self.timer.cancel()
        else:
            message = "LOGOUT"
        logging.info("Send to " + self.serverName + ":" + str(self.serverPort) + " -> " + message)
        self.tcpClientSocket.send(message.encode())

    #Check Online users
    def checkOnline(self):
        message = "CHECK-ONLINE"
        self.tcpClientSocket.send(message.encode())
        response = self.tcpClientSocket.recv(1024).decode().split()
        if response[0] == "NOT-ONLINE":
            print(Fore.YELLOW + Style.BRIGHT + "There are no other online users currently...")
            print(Style.RESET_ALL)
        elif response[0] == "SUCCESS":
            for p in response:
                if p != "SUCCESS":
                    print(Fore.GREEN+p)
        print(Style.RESET_ALL)

    # function for sending hello message
    # a timer thread is used to send hello messages to udp socket of server
    def sendHelloMessage(self):
        message = "HELLO " + self.loginCredentials[0]
        logging.info("Send to " + self.serverName + ":" + str(self.serverUDPPort) + " -> " + message)
        self.udpClientSocket.sendto(message.encode(), (self.serverName, self.serverUDPPort))
        self.timer = threading.Timer(1, self.sendHelloMessage)
        self.timer.start()


# peer is started
colorama.init()
print(colorama.ansi.clear_screen())
print("\033[%d;%dH" % (1, 1), end="")#Move cursor to top left
welcome_message ="""
    ╔════════════════════════╗
    ║         Welcome        ║
    ╚════════════════════════╝"""
print(Fore.BLUE + welcome_message)
print(Style.RESET_ALL)
main = peerMain()
