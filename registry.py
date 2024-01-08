'''
    ##  Implementation of registry
    ##  150114822 - Eren Ulaş
'''

from socket import *
import threading
import select
import logging
import db
import bcrypt

# This class is used to process the peer messages sent to registry
# for each peer connected to registry, a new client thread is created

class ClientThread(threading.Thread):
    # initializations for client thread
    def __init__(self, ip, port, tcpClientSocket):
        threading.Thread.__init__(self)
        # ip of the connected peer
        self.ip = ip
        # port number of the connected peer
        self.port = port
        # socket of the peer
        self.tcpClientSocket = tcpClientSocket
        # username, online status and udp server initializations
        self.username = None
        self.isOnline = True
        self.udpServer = None
        print("New thread started for " + ip + ":" + str(port))
        # List to store the chat rooms the client is a member of
        self.chat_rooms = set()

    def bcrypthash(self,password):
        bytes=password.encode('utf-8')
        salt = bcrypt.gensalt(rounds=12) #rounds was choosen to be 12 to balance between performance and security
        hashed_password = bcrypt.hashpw(bytes, salt)
        return hashed_password
    # main of the thread
    def run(self):
        # locks for thread which will be used for thread synchronization
        self.lock = threading.Lock()
        print("Connection from: " + self.ip + ":" + str(port))
        print("IP Connected: " + self.ip)

        while True:
            try:
                # waits for incoming messages from peers
                message = self.tcpClientSocket.recv(1024).decode().split()
                logging.info("Received from " + self.ip + ":" + str(self.port) + " -> " + " ".join(message))
                #   JOIN    #
                if message[0] == "SIGNUP":
                    # join-exist is sent to peer,
                    # if an account with this username already exists
                    if db.is_account_exist(message[1]):
                        response = "USERNAME-EXISTS"
                        print("From-> " + self.ip + ":" + str(self.port) + " " + response)
                        logging.info("Send to " + self.ip + ":" + str(self.port) + " -> " + response)
                        self.tcpClientSocket.send(response.encode())
                    # join-success is sent to peer,
                    # if an account with this username is not exist, and the account is created
                    else:
                        register_hashed_password = self.bcrypthash(message[2])
                        print(register_hashed_password)# hashing password before sending it to database
                        db.register(message[1], register_hashed_password)
                        response = "SUCCESS"
                        logging.info("Send to " + self.ip + ":" + str(self.port) + " -> " + response)
                        self.tcpClientSocket.send(response.encode())
                #   LOGIN    #
                elif message[0] == "LOGIN":
                    # login-account-not-exist is sent to peer,
                    # if an account with the username does not exist
                    if not db.is_account_exist(message[1]):
                        response = "USER-NOT-EXIST"
                        logging.info("Send to " + self.ip + ":" + str(self.port) + " -> " + response)
                        self.tcpClientSocket.send(response.encode())
                    # login-online is sent to peer,
                    # if an account with the username already online
                    elif db.is_account_online(message[1]):
                        response = "USER-ONLINE"
                        logging.info("Send to " + self.ip + ":" + str(self.port) + " -> " + response)
                        self.tcpClientSocket.send(response.encode())
                    # login-success is sent to peer,
                    # if an account with the username exists and not online
                    else:
                        # retrieves the account's password, and checks if the one entered by the user is correct
                        retrieved_Hashed_Pass = db.get_password(message[1])
                        # if password is correct, then peer's thread is added to threads list
                        # peer is added to db with its username, port number, and ip address
                        if bcrypt.checkpw(message[2].encode('utf-8'),
                                          retrieved_Hashed_Pass):  # method to compare hashed with sent plain text passwords
                            self.username = message[1]
                            self.lock.acquire()
                            try:
                                tcpThreads[self.username] = self  # passing to tcpThreads Dictionary instance of ClientThread to monitor active Tcp threads
                            finally:
                                self.lock.release()

                            tcpportno=message[3]
                            udpportno=message[4]
                            db.user_login(message[1], self.ip,tcpportno,udpportno)
                            # login-success is sent to peer,
                            # and a udp server thread is created for this peer, and thread is started
                            # timer thread of the udp server is started
                            response = "SUCCESS"
                            logging.info("Send to " + self.ip + ":" + str(self.port) + " -> " + response)
                            self.tcpClientSocket.send(response.encode())
                            self.udpServer = UDPServer(self.username, self.tcpClientSocket)
                            self.udpServer.start()
                            self.udpServer.timer.start()
                        # if password not matches and then login-wrong-password response is sent
                        else:
                            response = "WRONG-PASSWORD"
                            logging.info("Send to " + self.ip + ":" + str(self.port) + " -> " + response)
                            self.tcpClientSocket.send(response.encode())
                #   LOGOUT  #
                elif message[0] == "LOGOUT":
                    # if user is online,
                    # removes the user from onlinePeers list
                    # and removes the thread for this user from tcpThreads
                    # socket is closed and timer thread of the udp for this
                    # user is cancelled
                    if len(message) > 1 and message[1] is not None and db.is_account_online(message[1]):
                        db.user_logout(message[1])
                        self.lock.acquire()
                        try:
                            if message[1] in tcpThreads:
                                del tcpThreads[message[1]]
                        finally:
                            self.lock.release()
                        print(self.ip + ":" + str(self.port) + " is logged out")
                        self.tcpClientSocket.close()
                        self.udpServer.timer.cancel()
                        break
                    else:
                        self.tcpClientSocket.close()
                        break
                #Check online users#
                elif message[0] == "CHECK-ONLINE":
                    online_users = db.accounts_online()
                    if online_users==0:
                        response ="NOT-ONLINE"
                        self.tcpClientSocket.send(response.encode())
                    else:
                        response = "SUCCESS "
                        for peer in online_users:
                            response += peer +" "
                        self.tcpClientSocket.send(response.encode())
                #   SEARCH  #
                elif message[0] == "SEARCH":
                    # checks if an account with the username exists
                    if db.is_account_exist(message[1]):
                        # checks if the account is online
                        # and sends the related response to peer
                        if db.is_account_online(message[1]):
                            peer_info = db.search(message[1])
                            response = "SUCCESS " + peer_info[0] + " " + peer_info[1]
                            logging.info("Send to " + self.ip + ":" + str(self.port) + " -> " + response)
                            self.tcpClientSocket.send(response.encode())
                        else:
                            response = "USER-NOT-ONLINE"
                            logging.info("Send to " + self.ip + ":" + str(self.port) + " -> " + response)
                            self.tcpClientSocket.send(response.encode())
                    # enters if username does not exist
                    else:
                        response = "USER-NOT-EXIST"
                        logging.info("Send to " + self.ip + ":" + str(self.port) + " -> " + response)
                        self.tcpClientSocket.send(response.encode())
                        # Phase 3
                elif message[0] == "CREATE-ROOM":
                    room_name = message[1]
                    if db.chatroom_exist(room_name)!= True:
                        db.create_chat_rooms(room_name)
                        response = "SUCCESS"
                        logging.info("Send to " + self.ip + ":" + str(self.port) + " -> " + response)
                        self.tcpClientSocket.send(response.encode())
                    else:
                        response = "ROOM-EXISTS"
                        logging.info("Send to " + self.ip + ":" + str(self.port) + " -> " + response)
                        self.tcpClientSocket.send(response.encode())

                    #   JOIN-CHATROOM    #
                elif message[0] == "JOIN-ROOM":
                    room_name = message[1]
                    if db.is_peer_in_room(message[2],room_name) ==True:
                        response = "ALREADY-JOINED"
                        logging.info("Send to " + self.ip + ":" + str(self.port) + " -> " + response)
                        self.tcpClientSocket.send(response.encode())
                    elif db.chatroom_exist(room_name)!=True:
                        response = "ROOM-NOT-EXIST"
                        logging.info("Send to " + self.ip + ":" + str(self.port) + " -> " + response)
                        self.tcpClientSocket.send(response.encode())
                    else:
                        db.insert_peer_room(message[2],room_name)
                        response = "SUCCESS"
                        logging.info("Send to " + self.ip + ":" + str(self.port) + " -> " + response)
                        self.tcpClientSocket.send(response.encode())
                elif message[0]=="IP-PORT-NEEDED":
                    needed_username=message[1]
                    peer_ip, peer_port = db.get_peer_ip_port(needed_username)
                    response=peer_ip+" "+peer_port
                    self.tcpClientSocket.send(response.encode())


                    #   LEAVE-CHATROOM   #
                elif message[0] == "LEAVE-ROOM":
                    room_name = message[1]
                    username=message[2]
                    if db.chatroom_exist(room_name) !=True:
                        response = "ROOM-NOT-EXIST"
                        logging.info("Send to " + self.ip + ":" + str(self.port) + " -> " + response)
                        self.tcpClientSocket.send(response.encode())

                    elif db.is_peer_in_room(username,room_name)== True:
                        db.peer_leave_room(username, room_name)
                        if db.check_last_user(room_name) == True:
                            db.delete_chat_rooms(room_name)

                        response = "SUCCESS"
                        logging.info("Send to " + self.ip + ":" + str(self.port) + " -> " + response)
                        self.tcpClientSocket.send(response.encode())

                    elif db.is_peer_in_room(username,room_name)!= True:
                        response = "NOT-IN-ROOM"
                        logging.info("Send to " + self.ip + ":" + str(self.port) + " -> " + response)
                        self.tcpClientSocket.send(response.encode())

                elif message[0] == "GET-ROOM-PEERS":
                    # now i want to retireve list of all users in this room in order to contact them via peer to peer in client side
                    list_all_users_in_room = []
                    list_all_users_in_room = db.retrieve_users_in_room(message[1])
                    response = "SENDING-USERNAMES "
                    for i in list_all_users_in_room:
                        # pass list of usernames to client side
                        response += i + " "

                    self.tcpClientSocket.send(response.encode())  # sending to client list of all usernames of members in room

                elif message[0] == "CHECK-ROOMS":
                    rooms_available = []
                    rooms_available = db.show_rooms()
                    if rooms_available == 0:
                        response = "NO-ROOMS"
                        logging.info("Send to " + self.ip + ":" + str(self.port) + " -> " + response)
                        self.tcpClientSocket.send(response.encode())
                    else:
                        response = "SUCCESS "
                        for room in rooms_available:
                            response += room + " "
                        logging.info("Send to " + self.ip + ":" + str(self.port) + " -> " + response)
                        self.tcpClientSocket.send(response.encode())

                elif message[0] == "CONNECT":
                    room_name = message[1]
                    username = message[2]
                    if db.chatroom_exist(room_name)==False:
                        response = "ROOM-NOT-EXIST"
                        logging.info("Send to " + self.ip + ":" + str(self.port) + " -> " + response)
                        self.tcpClientSocket.send(response.encode())
                    elif db.is_user_in_room_currently(room_name, username):
                        response = "ALREADY-IN-ROOM"
                        logging.info("Send to " + self.ip + ":" + str(self.port) + " -> " + response)
                        self.tcpClientSocket.send(response.encode())
                    elif db.is_peer_in_room(username,room_name):
                        db.connect_peer(room_name,username)
                        response = "SUCCESS"
                        logging.info("Send to " + self.ip + ":" + str(self.port) + " -> " + response)
                        self.tcpClientSocket.send(response.encode())
                    else:
                        response = "NOT-IN-ROOM"
                        logging.info("Send to " + self.ip + ":" + str(self.port) + " -> " + response)
                        self.tcpClientSocket.send(response.encode())

                elif message[0] == "DISCONNECT":
                    room_name = message[1]
                    username = message[2]
                    if not db.chatroom_exist(room_name):
                        response = "ROOM-NOT-EXIST"
                        logging.info("Send to " + self.ip + ":" + str(self.port) + " -> " + response)
                        self.tcpClientSocket.send(response.encode())
                    elif not db.is_peer_in_room(username, room_name):
                        response = "NOT-IN-ROOM"
                        logging.info("Send to " + self.ip + ":" + str(self.port) + " -> " + response)
                        self.tcpClientSocket.send(response.encode())
                    elif db.is_user_in_room_currently(room_name, username):
                        db.disconnect_peer(room_name, username)
                        response = "SUCCESS"
                        logging.info("Send to " + self.ip + ":" + str(self.port) + " -> " + response)
                        self.tcpClientSocket.send(response.encode())
                    else:
                        response = "NOT-IN-ROOM-CURRENTLY"
                        logging.info("Send to " + self.ip + ":" + str(self.port) + " -> " + response)
                        self.tcpClientSocket.send(response.encode())

                elif message[0] == "SET-ROOM-ADMIN":
                    room_name = message[1]
                    username = message[2]
                    if not db.chatroom_exist(room_name):
                        response = "ROOM-NOT-EXIST"
                        logging.info("Send to " + self.ip + ":" + str(self.port) + " -> " + response)
                        self.tcpClientSocket.send(response.encode())
                    elif not db.is_peer_in_room(username, room_name):
                        response = "NOT-IN-ROOM"
                        logging.info("Send to " + self.ip + ":" + str(self.port) + " -> " + response)
                        self.tcpClientSocket.send(response.encode())
                    else:
                        db.set_room_admin(username,room_name)
                        response = "SUCCESS"
                        logging.info("Send to " + self.ip + ":" + str(self.port) + " -> " + response)
                        self.tcpClientSocket.send(response.encode())

                elif message[0] == "GET-PEERS-OUT-OF-ROOM":
                    room_name = message[1]
                    all_peers = db.retrieve_all_users(room_name)
                    peers_not_in = []
                    for peer in all_peers:
                        if not db.is_user_in_room_currently(room_name, peer):
                            peers_not_in.append(peer)
                    if not peers_not_in:
                        response = "NONE"
                        logging.info("Send to " + self.ip + ":" + str(self.port) + " -> " + response)
                        self.tcpClientSocket.send(response.encode())
                    else:
                        response = "SENDING-USERNAMES "
                        for i in peers_not_in:
                            if db.is_account_online(i):
                                # pass list of usernames to client side
                                response += i + " "
                        logging.info("Send to " + self.ip + ":" + str(self.port) + " -> " + response)
                        self.tcpClientSocket.send(response.encode())



            except OSError as oErr:
                logging.error("OSError: {0}".format(oErr))

                # function for resettin the timeout for the udp timer thread

    def resetTimeout(self):
        self.udpServer.resetTimer()

    def broadcastChatRoomMessage(self, room_name, content):
        for username, thread in tcpThreads.items():
            if username != self.username and room_name in thread.chat_rooms:
                response = f"CHAT-MESSAGE {self.username} {room_name} {content}"
                logging.info("Send to " + thread.ip + ":" + str(thread.port) + " -> " + response)
                thread.tcpClientSocket.send(response.encode())


# implementation of the udp server thread for clients
class UDPServer(threading.Thread):

    # udp server thread initializations
    def __init__(self, username, clientSocket):
        threading.Thread.__init__(self)
        self.username = username
        # timer thread for the udp server is initialized
        self.timer = threading.Timer(3, self.waitHelloMessage)
        self.tcpClientSocket = clientSocket

    # if hello message is not received before timeout
    # then peer is disconnected
    def waitHelloMessage(self):
        if self.username is not None:
            db.user_logout(self.username)
            if self.username in tcpThreads:
                del tcpThreads[self.username]
        self.tcpClientSocket.close()
        print("Removed " + self.username + " from online peers")

    # resets the timer for udp server
    def resetTimer(self):
        self.timer.cancel()
        self.timer = threading.Timer(3, self.waitHelloMessage)
        self.timer.start()


# tcp and udp server port initializations
print("Server started...")
port = 15600
portUDP = 15500

# db initialization
db = db.DB()

# gets the ip address of this peer
# first checks to get it for windows devices
# if the device that runs this application is not windows
# it checks to get it for macos devices
hostname = gethostname()
try:
    host = gethostbyname(hostname)
except gaierror:
    import netifaces as ni

    host = ni.ifaddresses('en0')[ni.AF_INET][0]['addr']

print("Registry IP address: " + host)
print("Registry port number: " + str(port))

# onlinePeers list for online account
onlinePeers = {}
# accounts list for accounts
accounts = {}
# tcpThreads list for online client's thread
tcpThreads = {}  # Beyshoof meen online currently


# tcp and udp socket initializations
tcpSocket = socket(AF_INET, SOCK_STREAM)
udpSocket = socket(AF_INET, SOCK_DGRAM)
tcpSocket.bind((host, port))
udpSocket.bind((host, portUDP))
tcpSocket.listen(5)

# input sockets that are listened
inputs = [tcpSocket, udpSocket]

# log file initialization
logging.basicConfig(filename="registry.log", level=logging.INFO)

# as long as at least a socket exists to listen registry runs
while inputs:

    print("Listening for incoming connections...")
    # monitors for the incoming connections
    readable, writable, exceptional = select.select(inputs, [], [])
    for s in readable:
        # if the message received comes to the tcp socket
        # the connection is accepted and a thread is created for it, and that thread is started
        if s is tcpSocket:
            tcpClientSocket, addr = tcpSocket.accept()
            newThread = ClientThread(addr[0], addr[1], tcpClientSocket)
            newThread.start()
        # if the message received comes to the udp socket
        elif s is udpSocket:
            # received the incoming udp message and parses it
            message, clientAddress = s.recvfrom(1024)
            message = message.decode().split()
            # checks if it is a hello message
            if message[0] == "HELLO":
                # checks if the account that this hello message
                # is sent from is online
                if message[1] in tcpThreads:
                    # resets the timeout for that peer since the hello message is received
                    tcpThreads[message[1]].resetTimeout()
                    print("Hello is received from " + message[1])
                    logging.info(
                        "Received from " + clientAddress[0] + ":" + str(clientAddress[1]) + " -> " + " ".join(message))

# registry tcp socket is closed
tcpSocket.close()

