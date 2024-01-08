from socket import *
import threading
import logging
import colorama
import select
from colorama import Fore, Back, Style
import re

# CLI modifications

def link(uri, label=None):
    # If label is not provided, use the URI itself as the label
    if label is None:
        label = uri
    parameters = ''
    blue_text = '\033[34m'
    reset_color = '\033[0m'
    # Escape mask format for creating a clickable link with blue text
    escape_mask = '{}{}' + blue_text + reset_color
    return escape_mask.format(parameters, uri, label)

def convert_urls_to_hyperlinks(text):
    # Regular expression pattern for matching URLs in the text
    url_pattern = r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+'

    def replace_with_hyperlink(match):
        url = match.group(0)
        # Replace the URL with a hyperlink using the link function
        return link(url)

    return re.sub(url_pattern, replace_with_hyperlink, text)

def format(message):

    # Replace hyperlinks with styled text (clickable representation)
    formatted_message = convert_urls_to_hyperlinks(message)
    formatted_message = re.sub(r'\*(.*?)\*', lambda match: f'\033[1m{match.group(1)}\033[0m \033[34m', formatted_message)
    # Add italic formatting for text between -
    formatted_message = re.sub(r'-(.*?)-', lambda match: f'\033[3m{match.group(1)}\033[0m \033[34m', formatted_message)
    return formatted_message

# main process of the peer
class PeerServer(threading.Thread):

    # Peer server initialization
    def __init__(self, username, peerServerPort, roomServerPort):
        threading.Thread.__init__(self)
        # keeps the username of the peer
        self.username = username
        # tcp socket for peer server
        self.tcpServerSocket = socket(AF_INET, SOCK_STREAM)
        self.udpServerSocket = socket(AF_INET, SOCK_DGRAM)
        # port number of the peer server
        self.peerServerPort = peerServerPort
        self.roomServerPort = roomServerPort
        # if 1, then user is already chatting with someone
        # if 0, then user is not chatting with anyone
        self.isChatRequested = 0
        # keeps the socket for the peer that is connected to this peer
        self.connectedPeerSocket = None
        # keeps the ip of the peer that is connected to this peer's server
        self.connectedPeerIP = None
        # keeps the port number of the peer that is connected to this peer's server
        self.connectedPeerPorts = None
        # online status of the peer
        self.isOnline = True
        # keeps the username of the peer that this peer is chatting with
        self.chattingClientName = None
        self.chattingClientName = None
        self.chat = 0
        self.room = 0

        # main method of the peer server thread

    def run(self):

        print(Fore.YELLOW + "Peer server started...")
        print(Style.RESET_ALL)

        # gets the ip address of this peer
        # first checks to get it for windows devices
        # if the device that runs this application is not windows
        # it checks to get it for macos devices
        hostname = gethostname()
        try:
            self.peerServerHostname = gethostbyname(hostname)  # Get IP address
        except gaierror:  # gaierror means host name couldn't be resolved
            import netifaces as ni
            self.peerServerHostname = ni.ifaddresses('en0')[ni.AF_INET][0]['addr']  # Get IP adderess using the en0 interface of IPV4

        # ip address of this peer
        self.peerServerHostname = gethostbyname(gethostname())

        self.udpServerSocket.bind((self.peerServerHostname, int(self.roomServerPort)))
        # self.peerServerHostname = 'localhost'
        # socket initializations for chatting
        self.tcpServerSocket.bind((self.peerServerHostname, int(self.peerServerPort)))
        self.tcpServerSocket.listen(10)  # max connections
        # inputs sockets that should be listened
        inputs = [self.tcpServerSocket, self.udpServerSocket]
        # server listens as long as there is a socket to listen in the inputs list and the user is online
        while inputs and self.isOnline:
            # monitors for the incoming connections
            try:
                readable, writable, exceptional = select.select(inputs, [], [])
                # If a server waits to be connected enters here
                for s in readable:
                    # if the socket that is receiving the connection is
                    # the tcp socket of the peer's server, enters here
                    if s is self.tcpServerSocket and self.room == 0:
                        # accepts the connection, and adds its connection socket to the inputs list
                        # so that we can monitor that socket as well
                        connected, addr = s.accept()
                        connected.setblocking(0)
                        inputs.append(connected)
                        # if the user is not chatting, then the ip and the socket of
                        # this peer is assigned to server variables
                        if self.isChatRequested == 0:
                            print(Fore.YELLOW + self.username + " is connected from " + str(addr))
                            print(Style.RESET_ALL)
                            self.connectedPeerSocket = connected
                            self.connectedPeerIP = addr[0]
                    # if the socket that receives the data is the one that
                    # is used to communicate with a connected peer, then enters here"""
                    if s is self.udpServerSocket and self.room == 1:
                        #while (1):
                        data, address = self.udpServerSocket.recvfrom(1024)
                        messageReceived = data.decode()
                        print(Fore.BLUE+format(messageReceived))
                        print(Style.RESET_ALL)
                            #if (self.room == 0):
                            #    break
                    # if the socket that receives the data is the one that
                    # is used to communicate with a connected peer, then enters here
                    if s is self.udpServerSocket and self.room == 0:
                        #while (1):
                        data, address = self.udpServerSocket.recvfrom(1024)
                        messageReceived = data.decode()
                        print(Fore.YELLOW+messageReceived)
                        print(Style.RESET_ALL)
                            #if (self.room == 0):
                                #break
                    # if the socket that receives the data is the one that
                    # is used to communicate with a connected peer, then enters here
                    elif self.room == 0:
                        # message is received from connected peer
                        messageReceived = s.recv(1024).decode()
                        # logs the received message
                        logging.info("Received from " + str(self.connectedPeerIP) + " -> " + str(messageReceived))
                        # if message is a request message it means that this is the receiver side peer server
                        # so evaluate the chat request
                        if len(messageReceived) > 11 and messageReceived[:12] == "CHAT-REQUEST" and self.room == 0:
                            # text for proper input choices is printed however OK or REJECT is taken as input in main process of the peer
                            # if the socket that we received the data belongs to the peer that we are chatting with,
                            # enters here
                            if s is self.connectedPeerSocket:
                                # parses the message
                                messageReceived = messageReceived.split()
                                # gets the port of the peer that sends the chat request message
                                self.connectedPeerPort = int(messageReceived[1])
                                # gets the username of the peer sends the chat request message
                                self.chattingClientName = messageReceived[2]
                                # prints prompt for the incoming chat request
                                print(Fore.YELLOW + "Incoming chat request from " + self.chattingClientName + " >> ")
                                print(Fore.BLUE + "Enter OK to accept or REJECT to reject:  ")
                                print(Style.RESET_ALL)
                                # makes isChatRequested = 1 which means that peer is chatting with someone
                                self.isChatRequested = 1
                            # if the socket that we received the data does not belong to the peer that we are chatting with
                            # and if the user is already chatting with someone else(isChatRequested = 1), then enters here
                            elif s is not self.connectedPeerSocket and self.isChatRequested == 1:
                                # sends a busy message to the peer that sends a chat request when this peer is
                                # already chatting with someone else
                                message = "BUSY"
                                s.send(message.encode())
                                # remove the peer from the inputs list so that it will not monitor this socket
                                inputs.remove(s)
                        # if an OK message is received then ischatrequested is made 1 and then next messages will be shown to the peer of this server
                        elif messageReceived == "OK":
                            self.isChatRequested = 1
                            # if an REJECT message is received then ischatrequested is made 0 so that it can receive any other chat requests
                        elif messageReceived == "REJECT":
                            self.isChatRequested = 0
                            inputs.remove(s)
                            # if a message is received, and if this is not a quit message ':q' and
                            # if it is not an empty message, show this message to the user
                        elif messageReceived[:2] != ":q" and len(messageReceived) != 0:
                            print(Fore.BLUE + self.chattingClientName + ": " + format(messageReceived))
                            # if the message received is a quit message ':q',
                            # makes ischatrequested 1 to receive new incoming request messages
                            # removes the socket of the connected peer from the inputs list
                        elif messageReceived[:2] == ":q":
                            if (self.room == 1):
                                self.room = 0
                                # leave_room()
                            else:
                                self.isChatRequested = 0
                                inputs.clear()
                                inputs.append(self.tcpServerSocket)
                                inputs.append(self.udpServerSocket)
                                # connected peer ended the chat
                                if len(messageReceived) == 2:
                                    print(Fore.RED + "User you're chatting with ended the chat")
                                    print(Style.RESET_ALL)
                                    print(Fore.BLUE + "Press enter to quit the chat: ")
                                    print(Style.RESET_ALL)
                            # if the message is an empty one, then it means that the
                            # connected user suddenly ended the chat(an error occurred)
                        elif len(messageReceived) == 0:
                            self.isChatRequested = 0
                            inputs.clear()
                            inputs.append(self.tcpServerSocket)
                            inputs.append(self.udpServerSocket)
                            print(Fore.RED + "User you're chatting with suddenly ended the chat")
                            print(Style.RESET_ALL)
                            print(Fore.BLUE + "Press enter to quit the chat: ")
                            print(Style.RESET_ALL)


            # handles the exceptions, and logs them
            except OSError as oErr:
                logging.error("OSError: {0}".format(oErr))
            except ValueError as vErr:
                logging.error("ValueError: {0}".format(vErr))


# Client side of peer
class PeerClient(threading.Thread):
    # variable initializations for the client side of the peer
    def __init__(self, ipToConnect, portToConnect, username, peerServer, responseReceived, flag, room_name,
                 room_peers: list, registry_name):
        threading.Thread.__init__(self)
        self.registryName = registry_name
        # self.registryName = 'localhost'
        # port number of the registry
        self.registryPort = 15600
        # keeps the ip address of the peer that this will connect
        self.ipToConnect = ipToConnect
        # keeps the username of the peer
        self.username = username
        # keeps the port number that this client should connect
        self.portToConnect = portToConnect
        # client side tcp socket initialization
        self.tcpClientSocket = socket(AF_INET, SOCK_STREAM)
        self.udpClientSocket = socket(AF_INET, SOCK_DGRAM)
        # keeps the server of this client
        self.peerServer = peerServer
        # keeps the phrase that is used when creating the client
        # if the client is created with a phrase, it means this one received the request
        # this phrase should be none if this is the client of the requester peer
        self.responseReceived = responseReceived
        # keeps if this client is ending the chat or not
        self.isEndingChat = False
        # flag  to indicate room or normal chat
        self.flag = flag
        # room name
        self.room_name = room_name
        self.room_peers = room_peers
        self.isRoomEmpty = False

    def update_peers(self):
        message = "GET-ROOM-PEERS " + str(self.room_name)
        self.tcpClientSocket.send(message.encode())
        logging.info("Send to " + self.registryName + ":" + str(self.registryPort) + " -> " + message)
        response = self.tcpClientSocket.recv(1024).decode().split()
        list_all_usernames_peerside = []
        if response[0] == "SENDING-USERNAMES":
            for i in response:  # retreiving
                if i != "SENDING-USERNAMES" and i != self.username:  # here to ignore first response only.
                    peer_usernames = i
                    message = "IP-PORT-NEEDED " + peer_usernames
                    self.tcpClientSocket.send(message.encode())
                    response = self.tcpClientSocket.recv(1024).decode().split()
                    list_all_usernames_peerside.append((response[0], response[1]))
        self.room_peers = list_all_usernames_peerside

    def exit(self):
        # Then go to registry and remove him
        request = "DISCONNECT " + str(self.room_name) + " " + str(self.username)
        self.tcpClientSocket.send(request.encode())
        response = self.tcpClientSocket.recv(1024).decode()
        if response[0] == "ROOM-NOT-EXIST":
            print(Fore.RED + "Room You Entered does not exist")
            print(Style.RESET_ALL)
        elif response[0] == "NOT-IN-ROOM":
            print(Fore.RED + "User Not in Room ")
            print(Style.RESET_ALL)
        elif response[0] == "NOT-IN-ROOM-CURRENTLY":
            print(Fore.RED + "User Not connected to room currently")
            print(Style.RESET_ALL)
        elif response[0] == "SUCCESS":
            print(Fore.GREEN + "Room was Left Successfully")
        print(Style.RESET_ALL)
        # Display Message ("USERNAME Disconected")
        return response

    def notify(self):
        request = "GET-PEERS-OUT-OF-ROOM " + str(self.room_name)
        self.tcpClientSocket.send(request.encode())
        response = self.tcpClientSocket.recv(1024).decode().split()
        ip_port = []
        if response[0] == "NONE":
            return
        elif response[0] == "SENDING-USERNAMES":
            for i in response:  # retreiving
                if i != "SENDING-USERNAMES" and i != self.username:  # here to ignore first response only.
                    peer_usernames = i
                    message = "IP-PORT-NEEDED " + peer_usernames
                    self.tcpClientSocket.send(message.encode())
                    response = self.tcpClientSocket.recv(1024).decode().split()
                    ip_port.append((response[0], response[1]))
            message = "Messages are being sent from " + self.username + " to the following room: " + self.room_name
            for peer in ip_port:
                self.udpClientSocket.sendto(message.encode(), (peer[0], int(peer[1])))


    def handleChatRoomMessage(self, content, sender_username, room_name):
        # Handle incoming chat room messages
        print(f"\n{Fore.CYAN}{sender_username} (in {room_name}): {content}{Style.RESET_ALL}")

    # main method of the peer client thread
    def run(self):

        if self.flag == '1':
            self.tcpClientSocket = socket(AF_INET, SOCK_STREAM)
            print("Peer client started...")
            # connects to the server of other peer
            print("Connecting to " + self.ipToConnect + ":" + str(self.portToConnect) + "...")
            self.tcpClientSocket.connect((self.ipToConnect, self.portToConnect))
            # if the server of this peer is not connected by someone else and if this is the requester side peer client then enters here
            if self.peerServer.isChatRequested == 0 and self.responseReceived is None:
                # composes a request message and this is sent to server and then this waits a response message from the server this client connects
                requestMessage = "CHAT-REQUEST " + str(self.peerServer.peerServerPort)+ " " + self.username
                # logs the chat request sent to other peer
                logging.info("Send to " + self.ipToConnect + ":" + str(self.portToConnect) + " -> " + requestMessage)
                # sends the chat request
                self.tcpClientSocket.send(requestMessage.encode())
                print(Fore.YELLOW + "Request message " + requestMessage + " is sent...")
                # received a response from the peer which the request message is sent to
                self.responseReceived = self.tcpClientSocket.recv(1024).decode()
                # logs the received message
                logging.info("Received from " + self.ipToConnect + ":" + str(self.portToConnect) + " -> " + self.responseReceived)
                print(Fore.YELLOW + "Response is " + self.responseReceived)
                # parses the response for the chat request
                self.responseReceived = self.responseReceived.split()
                # if response is ok then incoming messages will be evaluated as client messages and will be sent to the connected server
                if self.responseReceived[0] == "OK":
                    # changes the status of this client's server to chatting
                    self.peerServer.isChatRequested = 1
                    # sets the server variable with the username of the peer that this one is chatting
                    self.peerServer.chattingClientName = self.responseReceived[1]
                    # as long as the server status is chatting, this client can send messages
                    while self.peerServer.isChatRequested == 1:
                        # message input prompt
                        messageSent = input()
                        # sends the message to the connected peer, and logs it
                        self.tcpClientSocket.send(messageSent.encode())
                        logging.info("Send to " + self.ipToConnect + ":" + str(self.portToConnect) + " -> " + messageSent)
                        # if the quit message is sent, then the server status is changed to not chatting
                        # and this is the side that is ending the chat
                        if messageSent == ":q":
                            self.peerServer.isChatRequested = 0
                            self.isEndingChat = True
                            break
                    # if peer is not chatting, checks if this is not the ending side
                    if self.peerServer.isChatRequested == 0:
                        if not self.isEndingChat:
                            # tries to send a quit message to the connected peer
                            # logs the message and handles the exception
                            try:
                                self.tcpClientSocket.send(":q ending-side".encode())
                                logging.info("Send to " + self.ipToConnect + ":" + str(self.portToConnect) + " -> :q")
                            except BrokenPipeError as bpErr:
                                logging.error("BrokenPipeError: {0}".format(bpErr))
                        # closes the socket
                        self.responseReceived = None
                        self.tcpClientSocket.close()
                # if the request is rejected, then changes the server status, sends a reject message to the connected peer's server
                # logs the message and then the socket is closed
                elif self.responseReceived[0] == "REJECT":
                    self.peerServer.isChatRequested = 0
                    print(Fore.RED + "client of requester is closing...")
                    print(Style.RESET_ALL)
                    self.tcpClientSocket.send("REJECT".encode())
                    logging.info("Send to " + self.ipToConnect + ":" + str(self.portToConnect) + " -> REJECT")
                    self.tcpClientSocket.close()
                # if a busy response is received, closes the socket
                elif self.responseReceived[0] == "BUSY":
                    print(Fore.RED + "Receiver peer is busy")
                    print(Style.RESET_ALL)
                    self.tcpClientSocket.close()
            # if the client is created with OK message it means that this is the client of receiver side peer
            # so it sends an OK message to the requesting side peer server that it connects and then waits for the user inputs.
            elif self.responseReceived == "OK":
                # server status is changed
                self.peerServer.isChatRequested = 1
                # ok response is sent to the requester side
                okMessage = "OK"
                self.tcpClientSocket.send(okMessage.encode())
                logging.info("Send to " + self.ipToConnect + ":" + str(self.portToConnect) + " -> " + okMessage)
                print(Fore.GREEN + "Client with OK message is created... and sending messages")
                print(Style.RESET_ALL)
                # client can send messsages as long as the server status is chatting
                while self.peerServer.isChatRequested == 1:
                    # input prompt for user to enter message
                    messageSent = input()
                    self.tcpClientSocket.send(messageSent.encode())
                    logging.info("Send to " + self.ipToConnect + ":" + str(self.portToConnect) + " -> " + messageSent)
                    # if a quit message is sent, server status is changed
                    if messageSent == ":q":
                        self.peerServer.isChatRequested = 0
                        self.isEndingChat = True
                        break
                # if server is not chatting, and if this is not the ending side
                # sends a quitting message to the server of the other peer
                # then closes the socket
                if self.peerServer.isChatRequested == 0:
                    if not self.isEndingChat:
                        self.tcpClientSocket.send(":q ending-side".encode())
                        logging.info("Send to " + self.ipToConnect + ":" + str(self.portToConnect) + " -> :q")
                    self.responseReceived = None
                    self.tcpClientSocket.close()


        elif self.flag == '2':
            self.tcpClientSocket = socket(AF_INET, SOCK_STREAM)
            self.tcpClientSocket.connect((self.registryName, self.registryPort))

            print(Fore.GREEN + "Joined Room Successfully ...")
            print(Style.RESET_ALL)
            self.update_peers()
            message = f"\n{self.username} Connected !"
            for peer in self.room_peers:
                if int(peer[1]) != self.peerServer.roomServerPort:
                    self.udpClientSocket.sendto(message.encode(), (peer[0], int(peer[1])))

            while True:

                self.update_peers()

                message = input()

                message = f"\n{self.username}: {message}"

                self.update_peers()
                if (len(message) != 0 and message.split()[1] == ":q"):

                    if self.exit() == "SUCCESS":

                        message = f"{self.username} Disconnected !"

                        for peer in self.room_peers:
                            self.udpClientSocket.sendto(message.encode(), (peer[0], int(peer[1])))
                        break


                else:
                    self.notify()
                    for peer in self.room_peers:

                        if int(peer[1]) != self.peerServer.peerServerPort:
                            self.udpClientSocket.sendto(message.encode(), (peer[0], int(peer[1])))

            print(Fore.YELLOW+"Chat Ended!")
            print(Style.RESET_ALL)
            self.flag = None


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
        # server port number of this peer
        self.peerServerPort = None
        # server of this peer
        self.peerServer = None
        # client of this peer
        self.peerClient = None
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
                choice = input(
                    "Choose: \nCreate account: Enter 1\nLogin: Enter 2\nLogout: Enter 3\nCheck Online Users: Enter 4\nCreate Chat Room: Enter 5\nJoin Chat Room : Enter 6\nList all Chat Rooms: Enter 7\nConnect to a Chat Room: Enter 8\nLeave Chat Room: Enter 9\nChat with a user: Enter 10\n>")
            else:
                choice = input(
                    "Choose: \nCreate account: Enter 1\nLogin: Enter 2\nExit: Enter 3\n")
            # if choice is 1, creates an account with the username
            # and password entered by the user
            if choice == "1":
                username = input(Fore.BLUE + Style.BRIGHT + "username: ")
                print(Fore.YELLOW + Style.BRIGHT + "Note:Password must be 9 characters at least")
                print(
                    Fore.YELLOW + Style.BRIGHT + "Note:Password must have one of the following symbols: !@#$%^&*()_+\\-=[\\]{};':\"\\|,.<>/?~")
                print(Fore.YELLOW + Style.BRIGHT + "Note:Password must have an uppercase letter")
                print(Fore.YELLOW + Style.BRIGHT + "Note:Password must have at least one digit")
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
                tcpportno = input(Fore.BLUE + Style.BRIGHT + "Port Number for private messaging : ")
                udpportno = input(Fore.BLUE + Style.BRIGHT + "Port Number for chatroom messaging : ")
                print(Style.RESET_ALL)

                status = self.login(username, password, tcpportno, udpportno)
                # is user logs in successfully, peer variables are set
                if status == 1:
                    self.isOnline = True
                    self.loginCredentials = (username, password)
                    self.peerServerPort = tcpportno
                    self.peerServer = PeerServer(self.loginCredentials[0], self.peerServerPort,udpportno)
                    self.peerServer.start()
                    # creates the server thread for this peer, and run
                    # hello message is sent to server
                    self.sendHelloMessage()
            # if choice is 3 and user is logged in, then user is logged out
            # and peer variables are set, and server and client sockets are closed
            elif choice == "3" and self.isOnline:
                self.logout(1)
                self.isOnline = False
                self.loginCredentials = (None, None)
                self.peerServer.isOnline = False
                self.peerServer.tcpServerSocket.close()
                if self.peerClient is not None:
                    self.peerClient.tcpClientSocket.close()
                print(Fore.GREEN + "Logged out successfully")
                print(Fore.YELLOW + Style.BRIGHT + "Goodbye!!")
                print(Style.RESET_ALL)
            # is peer is not logged in and exits the program
            elif choice == "3":
                self.logout(2)
                print(Fore.YELLOW + Style.BRIGHT + "Goodbye!!")
                print(Style.RESET_ALL)
            elif choice == "4":
                self.checkOnline()
            elif choice == "5" and self.isOnline:
                self.createChatRoom()
            elif choice == "6" and self.isOnline:
                self.joinChatRoom()
            elif choice == "7" and self.isOnline:
                self.listChatrooms()
            elif choice == "8" and self.isOnline:
                self.connect()
            elif choice == "9" and self.isOnline:
                self.leaveChatRoom()
            elif choice == "10" and self.isOnline:
                self.privateChat()


            elif choice == "OK" and self.isOnline:
                okMessage = "OK " + self.loginCredentials[0]
                logging.info("Send to " + self.peerServer.connectedPeerIP + " -> " + okMessage)
                self.peerServer.connectedPeerSocket.send(okMessage.encode())
                self.peerClient = PeerClient(self.peerServer.connectedPeerIP, self.peerServer.connectedPeerPort , self.loginCredentials[0], self.peerServer, "OK", '1' , None, None,self.serverName)
                self.peerClient.start()
                self.peerClient.join()
            # if user rejects the chat request then reject message is sent to the requester side
            elif choice == "REJECT" and self.isOnline:
                self.peerServer.connectedPeerSocket.send("REJECT".encode())
                self.peerServer.isChatRequested = 0
                logging.info("Send to " + self.peerServer.connectedPeerIP + " -> REJECT")

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

    def login(self, username, password, tcpportno, udpportno):
        # a login message is composed and sent to server
        # an integer is returned according to each response
        message = "LOGIN " + username + " " + password + " " + tcpportno + " " + udpportno
        logging.info("Send to " + self.serverName + ":" + str(self.serverPort) + " -> " + message)
        self.tcpClientSocket.send(message.encode())
        response = self.tcpClientSocket.recv(1024).decode()
        logging.info("Received from " + self.serverName + " -> " + response)
        if response == "SUCCESS":
            print(Fore.GREEN + "Logged in successfully...")
            print(Style.RESET_ALL)
            return 1
        elif response == "USER-NOT-EXIST":
            print(Fore.RED + "Account does not exist...")
            print(Style.RESET_ALL)
            return 0
        elif response == "USER-ONLINE":
            print(Fore.RED + "Account is already online...")
            print(Style.RESET_ALL)
            return 2
        elif response == "WRONG-PASSWORD":
            print(Fore.RED + "Password entered is wrong...")
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

    # Check Online users
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
                    print(Fore.GREEN + p)
        print(Style.RESET_ALL)

    # function for sending hello message
    # a timer thread is used to send hello messages to udp socket of server
    def sendHelloMessage(self):
        message = "HELLO " + self.loginCredentials[0]
        logging.info("Send to " + self.serverName + ":" + str(self.serverUDPPort) + " -> " + message)
        self.udpClientSocket.sendto(message.encode(), (self.serverName, self.serverUDPPort))
        self.timer = threading.Timer(1, self.sendHelloMessage)
        self.timer.start()

    def createChatRoom(self):
        if self.isOnline == True:
            room_name = input(Fore.BLUE + Style.BRIGHT + "Enter the chat room name: ")  # message[1]
            message = "CREATE-ROOM " + room_name  # message[0]
            self.tcpClientSocket.send(message.encode())
            response = self.tcpClientSocket.recv(1024).decode().split()
            if response[0] == "SUCCESS":
                message = "JOIN-ROOM " + room_name + " " + self.loginCredentials[0]
                self.tcpClientSocket.send(message.encode())
                response = self.tcpClientSocket.recv(1024).decode().split()
                message = "SET-ROOM-ADMIN " + room_name + " " + self.loginCredentials[0]
                self.tcpClientSocket.send(message.encode())
                response = self.tcpClientSocket.recv(1024).decode().split()
                print(Fore.GREEN + f"Chat room '{room_name}' created and joined successfully.")

            elif response[0] == "ROOM-EXISTS":
                print(Fore.GREEN + f"Chat room already exists")

        else:
            print(Fore.RED + "You are not logged in ")
        print(Style.RESET_ALL)
    def connect(self):
        room_name = input(Fore.BLUE + Style.BRIGHT + "Enter the chat room name to connect to: ")
        message = "CONNECT " + room_name + " " + self.loginCredentials[0]
        self.tcpClientSocket.send(message.encode())
        response = self.tcpClientSocket.recv(1024).decode().split()
        if response[0] == "ALREADY-IN-ROOM":
            print(Fore.RED + f"You are Already connected to this room '{room_name}'.")
            print(Style.RESET_ALL)
        elif response[0] == "ROOM-NOT-EXIST":
            print(Fore.RED + f"No Room Exists'{room_name}'.")
            print(Style.RESET_ALL)
        elif response[0] == "NOT-IN-ROOM":
            print(Fore.RED + f"You are not a member of this room '{room_name}'.")
            print(Style.RESET_ALL)
        elif response[0] == "SUCCESS":
            print(Fore.GREEN + f"You are being connected to the chat room '{room_name}'.")
            print(Style.RESET_ALL)
            host = gethostname()
            ipToConnect = gethostbyname(host)
            self.peerServer.room = 1
            self.peerClient = PeerClient(ipToConnect, None, self.loginCredentials[0], self.peerServer, None, '2',room_name, self.GetRoomPeers(room_name), self.serverName)
            self.peerClient.start()
            self.peerClient.join()
    def joinChatRoom(self):
        room_name = input(Fore.BLUE + Style.BRIGHT + "Enter the chat room name to join: ")
        message = "JOIN-ROOM " + room_name + " " +self.loginCredentials[0]
        self.tcpClientSocket.send(message.encode())
        response = self.tcpClientSocket.recv(1024).decode().split()
        if response[0] == "ALREADY-JOINED":
            print(Fore.RED + f"You are Already A member of this room '{room_name}'.")
            print(Style.RESET_ALL)
        elif response[0] == "ROOM-NOT-EXIST":
            print(Fore.RED + f"No Room Exists'{room_name}'.")
            print(Style.RESET_ALL)
        elif response[0] == "SUCCESS":
            print(Fore.GREEN + f"You joined the chat room '{room_name}'.")
            print(Style.RESET_ALL)


    def leaveChatRoom(self):

        room_name = input(Fore.BLUE + Style.BRIGHT + "Enter the chat room name to Leave: ")

        message = "LEAVE-ROOM " + room_name + " " + self.loginCredentials[0]
        self.tcpClientSocket.send(message.encode())
        response = self.tcpClientSocket.recv(1024).decode().split()
        if response[0] == "ROOM-NOT-EXIST":
            print(Fore.RED + "Room You Entered does not exist")
            print(Style.RESET_ALL)
        elif response[0] == "NOT-IN-ROOM":
            print(Fore.RED + "User Not in Room ")
            print(Style.RESET_ALL)
        elif response[0] == "SUCCESS":
            print(Fore.GREEN + "Room was Left Successfully")
            print(Style.RESET_ALL)

    def GetRoomPeers(self, room_name):
        message = "GET-ROOM-PEERS " + room_name
        self.tcpClientSocket.send(message.encode())
        response = self.tcpClientSocket.recv(1024).decode().split()
        list_all_usernames_peerside = []
        if response[0] == "SENDING-USERNAMES":
            for i in response:  # retreiving
                if i != "SENDING-USERNAMES" and i != self.loginCredentials[0]:  # here to ignore first response only.
                    peer_usernames = i
                    message = "IP-PORT-NEEDED " + peer_usernames
                    self.tcpClientSocket.send(message.encode())
                    response = self.tcpClientSocket.recv(1024).decode().split()
                    list_all_usernames_peerside.append((response[0], response[1]))
        return list_all_usernames_peerside

    def listChatrooms(self):
        message = "CHECK-ROOMS"
        self.tcpClientSocket.send(message.encode())
        response = self.tcpClientSocket.recv(1024).decode().split()
        if response[0] == "NO-ROOMS":
            print(Fore.RED + "No rooms are available")
            print(Style.RESET_ALL)
        elif response[0] == "SUCCESS":
            for i in response:
                if i != "SUCCESS":
                    print(Fore.GREEN + i)
            print(Style.RESET_ALL)

    def privateChat(self):
        username = input(Fore.BLUE + "Enter username you want to chat with: ")
        message = "SEARCH " + username
        self.tcpClientSocket.send(message.encode())
        response = self.tcpClientSocket.recv(1024).decode().split()
        if response[0] == "USER-NOT-ONLINE":
            print(Fore.RED+"The user you are trying to message is not online.")
            print(Style.RESET_ALL)
        elif response[0] == "USER-NOT-EXIST":
            print(Fore.RED+"The user you are trying to message does not exist.")
            print(Style.RESET_ALL)
        elif response[0] == "SUCCESS":
            peerip = response[1]
            peerPort = response[2]
            self.peerServer.chat = 1
            self.peerClient = PeerClient(ipToConnect=peerip, portToConnect=int(peerPort),username=self.loginCredentials[0], peerServer=self.peerServer,responseReceived=None, flag='1', room_name=None, room_peers=None, registry_name=self.serverName)
            self.peerClient.start()
            self.peerClient.join()


# peer is started
colorama.init()
print(colorama.ansi.clear_screen())
print("\033[%d;%dH" % (1, 1), end="")  # Move cursor to top left
welcome_message = """
    ╔════════════════════════╗
    ║         Welcome        ║
    ╚════════════════════════╝"""
print(Fore.BLUE + welcome_message)
print(Style.RESET_ALL)
main = peerMain()
