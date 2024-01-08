import unittest
from unittest.mock import patch
import db
from socket import *


class TestPeerMain(unittest.TestCase):
    def setUp(self):
        # ip address of the server
        hostname = gethostname()
        try:
            self.peerServerHostname = gethostbyname(hostname)  # Get IP address
        except gaierror:  # gaierror means host name couldn't be resolved
            import netifaces as ni
            self.peerServerHostname = ni.ifaddresses('en0')[ni.AF_INET][0][
                'addr']  # Get IP adderess using the en0 interface of IPV4

            # ip address of this peer
        self.peerServerHostname = gethostbyname(gethostname())
        self.serverName =  self.peerServerHostname
        # port number of the server
        self.serverPort = 15600
        # tcp socket connection to server
        self.tcpClientSocket = socket(AF_INET, SOCK_STREAM)
        self.tcpClientSocket.connect((self.serverName, self.serverPort))

    def test_integration1(self):
     #Simulating making new user account
        message = "SIGNUP " + "Mohamed_Khafagy" + " " + "Hassan_Mohamed123#"
        self.tcpClientSocket.send(message.encode())
        response = self.tcpClientSocket.recv(1024).decode()
        self.assertEqual(response, "SUCCESS")

    def test_integration2(self):
        # Simulating making new user account that already exists
        message = "SIGNUP " + "Mohamed_Khafagy" + " " + "Hassan_Mohamed123#"
        self.tcpClientSocket.send(message.encode())
        response = self.tcpClientSocket.recv(1024).decode()
        self.assertEqual(response, "USERNAME-EXISTS")
        # Simulating making new user account
        message = "SIGNUP " + "Hassan_Tobgy" + " " + "Hassan_ELTOB123#"
        self.tcpClientSocket.send(message.encode())
        response = self.tcpClientSocket.recv(1024).decode()
        self.assertEqual(response, "SUCCESS")

    def test_integration3(self):
        # Simulating making new user account
        message = "SIGNUP " + "Hassan_Tobgy" + " " + "Hassan_ELTOB123#"
        self.tcpClientSocket.send(message.encode())
        response = self.tcpClientSocket.recv(1024).decode()
        self.assertEqual(response, "USERNAME-EXISTS")
        # login with Correct password
        portno_simulation = "1200"
        message = "LOGIN " + "Hassan_Tobgy" + " " + "Hassan_ELTOB123#" + " " + portno_simulation

        self.tcpClientSocket.send(message.encode())
        response = self.tcpClientSocket.recv(1024).decode()
        self.assertEqual(response, "SUCCESS")
        # check online user with no on online just logged in user
        message = "CHECK-ONLINE"
        self.tcpClientSocket.send(message.encode())
        response = self.tcpClientSocket.recv(1024).decode().split()
        self.assertEqual(response[0], 'NOT-ONLINE')



    def test_integration4(self,db=db.DB()):
        # login with Correct  password
        portno_simulation = "1200"
        message = "LOGIN " + "Hassan_Tobgy" + " " + "Hassan_ELTOB123#" + " " + portno_simulation

        self.tcpClientSocket.send(message.encode())
        response = self.tcpClientSocket.recv(1024).decode()
        self.assertEqual(response, "SUCCESS")
        # check online user with no on online just logged in user
        message = "CHECK-ONLINE"
        self.tcpClientSocket.send(message.encode())
        response = self.tcpClientSocket.recv(1024).decode().split()
        self.assertEqual(response[0], 'NOT-ONLINE')

        #LOGOUT
        message = "LOGOUT " + "Hassan_Tobgy"
        self.tcpClientSocket.send(message.encode())
        username = "Hassan"

        Online_flag = db.is_account_online(username)
        self.assertEqual(Online_flag, False)


    def test_integration5(self,db=db.DB()):
        # login with Wrong   password
        portno_simulation = "1200"
        message = "LOGIN " + "Hassan_Tobgy" + " " + "Hassan_ELTOB123$" + " " + portno_simulation

        self.tcpClientSocket.send(message.encode())
        response = self.tcpClientSocket.recv(1024).decode()
        self.assertEqual(response, "WRONG-PASSWORD")
        # login with Correct   password
        portno_simulation = "1200"
        message = "LOGIN " + "Hassan_Tobgy" + " " + "Hassan_ELTOB123#" + " " + portno_simulation

        self.tcpClientSocket.send(message.encode())
        response = self.tcpClientSocket.recv(1024).decode()
        self.assertEqual(response, "SUCCESS")
        # check online user with no on online just logged in user
        message = "CHECK-ONLINE"
        self.tcpClientSocket.send(message.encode())
        response = self.tcpClientSocket.recv(1024).decode().split()
        self.assertEqual(response[0], 'NOT-ONLINE')

        #LOGOUT
        message = "LOGOUT " + "Hassan_Tobgy"
        self.tcpClientSocket.send(message.encode())
        username = "Hassan"

        Online_flag = db.is_account_online(username)
        self.assertEqual(Online_flag, False)

    def test_integration6(self,db=db.DB()):
        # login with Wrong   password
        portno_simulation = "1200"
        message = "LOGIN " + "Hassan_Tobgy" + " " + "Hassan_ELTOB123$" + " " + portno_simulation

        self.tcpClientSocket.send(message.encode())
        response = self.tcpClientSocket.recv(1024).decode()
        self.assertEqual(response, "WRONG-PASSWORD")
        # login with Correct   password
        portno_simulation = "1200"
        message = "LOGIN " + "Hassan_Tobgy" + " " + "Hassan_ELTOB123#" + " " + portno_simulation

        self.tcpClientSocket.send(message.encode())
        response = self.tcpClientSocket.recv(1024).decode()
        self.assertEqual(response, "SUCCESS")
        # check online user with no on online just logged in user
        message = "CHECK-ONLINE"
        self.tcpClientSocket.send(message.encode())
        response = self.tcpClientSocket.recv(1024).decode().split()
        self.assertEqual(response[0], 'NOT-ONLINE')


        #Creat ROOM
        # Simulating Creating New room
        room_name = "Friends"
        message = "CREATE-ROOM " + room_name
        self.tcpClientSocket.send(message.encode())
        response = self.tcpClientSocket.recv(1024).decode()
        self.assertEqual(response, "SUCCESS")

        # LOGOUT
        message = "LOGOUT " + "Hassan_Tobgy"
        self.tcpClientSocket.send(message.encode())
        username = "Hassan"

        Online_flag = db.is_account_online(username)
        self.assertEqual(Online_flag, False)


    def test_integration7(self,db=db.DB()):
        # login with Wrong   password
        portno_simulation = "1200"
        message = "LOGIN " + "Hassan_Tobgy" + " " + "Hassan_ELTOB123$" + " " + portno_simulation

        self.tcpClientSocket.send(message.encode())
        response = self.tcpClientSocket.recv(1024).decode()
        self.assertEqual(response, "WRONG-PASSWORD")
        # login with Correct   password
        portno_simulation = "1200"
        message = "LOGIN " + "Hassan_Tobgy" + " " + "Hassan_ELTOB123#" + " " + portno_simulation

        self.tcpClientSocket.send(message.encode())
        response = self.tcpClientSocket.recv(1024).decode()
        self.assertEqual(response, "SUCCESS")
        # check online user with no on online just logged in user
        message = "CHECK-ONLINE"
        self.tcpClientSocket.send(message.encode())
        response = self.tcpClientSocket.recv(1024).decode().split()
        self.assertEqual(response[0], 'NOT-ONLINE')

        # Create ROOM with name that exists

        room_name = "Friends"
        message = "CREATE-ROOM " + room_name
        self.tcpClientSocket.send(message.encode())
        response = self.tcpClientSocket.recv(1024).decode()
        self.assertEqual(response, "ROOM-EXISTS")

        # LOGOUT
        message = "LOGOUT " + "Hassan_Tobgy"
        self.tcpClientSocket.send(message.encode())
        username = "Hassan"

        Online_flag = db.is_account_online(username)
        self.assertEqual(Online_flag, False)


    def test_integration8(self,db=db.DB()):
        # login with Wrong   password
        portno_simulation = "1200"
        message = "LOGIN " + "Hassan_Tobgy" + " " + "Hassan_ELTOB123$" + " " + portno_simulation

        self.tcpClientSocket.send(message.encode())
        response = self.tcpClientSocket.recv(1024).decode()
        self.assertEqual(response, "WRONG-PASSWORD")
        # login with Correct   password
        portno_simulation = "1200"
        message = "LOGIN " + "Hassan_Tobgy" + " " + "Hassan_ELTOB123#" + " " + portno_simulation

        self.tcpClientSocket.send(message.encode())
        response = self.tcpClientSocket.recv(1024).decode()
        self.assertEqual(response, "SUCCESS")
        # check online user with no on online just logged in user
        message = "CHECK-ONLINE"
        self.tcpClientSocket.send(message.encode())
        response = self.tcpClientSocket.recv(1024).decode().split()
        self.assertEqual(response[0], 'NOT-ONLINE')

        # Create ROOM with name that exists

        room_name = "Friends"
        message = "CREATE-ROOM " + room_name
        self.tcpClientSocket.send(message.encode())
        response = self.tcpClientSocket.recv(1024).decode()
        self.assertEqual(response, "ROOM-EXISTS")

        #join room that exists
        # Simulating Trying to make room while there already exists room with same name
        room_name = "Friends"
        message = "JOIN-ROOM " + room_name + " " + "Hassan_Mohamed"
        self.tcpClientSocket.send(message.encode())
        response = self.tcpClientSocket.recv(1024).decode()
        self.assertEqual(response, "SUCCESS")

        # LOGOUT
        message = "LOGOUT " + "Hassan_Tobgy"
        self.tcpClientSocket.send(message.encode())
        username = "Hassan"

        Online_flag = db.is_account_online(username)
        self.assertEqual(Online_flag, False)



    def test_integration9(self,db=db.DB()):
        # login with Wrong   password
        portno_simulation = "1200"
        message = "LOGIN " + "Hassan_Tobgy" + " " + "Hassan_ELTOB123$" + " " + portno_simulation

        self.tcpClientSocket.send(message.encode())
        response = self.tcpClientSocket.recv(1024).decode()
        self.assertEqual(response, "WRONG-PASSWORD")
        # login with Correct   password
        portno_simulation = "1200"
        message = "LOGIN " + "Hassan_Tobgy" + " " + "Hassan_ELTOB123#" + " " + portno_simulation

        self.tcpClientSocket.send(message.encode())
        response = self.tcpClientSocket.recv(1024).decode()
        self.assertEqual(response, "SUCCESS")
        # check online user with no on online just logged in user
        message = "CHECK-ONLINE"
        self.tcpClientSocket.send(message.encode())
        response = self.tcpClientSocket.recv(1024).decode().split()
        self.assertEqual(response[0], 'NOT-ONLINE')

        # Create ROOM with name that exists

        room_name = "Friends"
        message = "CREATE-ROOM " + room_name
        self.tcpClientSocket.send(message.encode())
        response = self.tcpClientSocket.recv(1024).decode()
        self.assertEqual(response, "ROOM-EXISTS")

        # join room that exists
        # Simulating Trying to make room while there already exists room with same name
        room_name = "Friends"
        message = "JOIN-ROOM " + room_name + " " + "Hassan_Mohamed"
        self.tcpClientSocket.send(message.encode())
        response = self.tcpClientSocket.recv(1024).decode()
        self.assertEqual(response, "ALREADY-JOINED")

        # LOGOUT
        message = "LOGOUT " + "Hassan_Tobgy"
        self.tcpClientSocket.send(message.encode())
        username = "Hassan"

        Online_flag = db.is_account_online(username)
        self.assertEqual(Online_flag, False)


    def test_integration10(self,db=db.DB()):
        # login with Wrong   password
        portno_simulation = "1200"
        message = "LOGIN " + "Hassan_Tobgy" + " " + "Hassan_ELTOB123$" + " " + portno_simulation

        self.tcpClientSocket.send(message.encode())
        response = self.tcpClientSocket.recv(1024).decode()
        self.assertEqual(response, "WRONG-PASSWORD")
        # login with Correct   password
        portno_simulation = "1200"
        message = "LOGIN " + "Hassan_Tobgy" + " " + "Hassan_ELTOB123#" + " " + portno_simulation

        self.tcpClientSocket.send(message.encode())
        response = self.tcpClientSocket.recv(1024).decode()
        self.assertEqual(response, "SUCCESS")
        # check online user with no on online just logged in user
        message = "CHECK-ONLINE"
        self.tcpClientSocket.send(message.encode())
        response = self.tcpClientSocket.recv(1024).decode().split()
        self.assertEqual(response[0], 'NOT-ONLINE')

        # Create ROOM with name that exists

        room_name = "Friends"
        message = "CREATE-ROOM " + room_name
        self.tcpClientSocket.send(message.encode())
        response = self.tcpClientSocket.recv(1024).decode()
        self.assertEqual(response, "ROOM-EXISTS")

        # join room that exists
        # Simulating Trying to make room while there already exists room with same name
        room_name = "Friends"
        message = "JOIN-ROOM " + room_name + " " + "Hassan_Mohamed"
        self.tcpClientSocket.send(message.encode())
        response = self.tcpClientSocket.recv(1024).decode()
        self.assertEqual(response, "ALREADY-JOINED")

        #GET_ROOM_PEERS
        message = "GET-ROOM-PEERS " + room_name
        self.tcpClientSocket.send(message.encode())
        response = self.tcpClientSocket.recv(1024).decode()
        self.assertIn('SENDING-USERNAMES', response)

        # LOGOUT
        message = "LOGOUT " + "Hassan_Tobgy"
        self.tcpClientSocket.send(message.encode())
        username = "Hassan"

        Online_flag = db.is_account_online(username)
        self.assertEqual(Online_flag, False)

    def   test_integration11(self,db=db.DB()):
        # login with Wrong   password
        portno_simulation = "1200"
        message = "LOGIN " + "Hassan_Tobgy" + " " + "Hassan_ELTOB123$" + " " + portno_simulation

        self.tcpClientSocket.send(message.encode())
        response = self.tcpClientSocket.recv(1024).decode()
        self.assertEqual(response, "WRONG-PASSWORD")
        # login with Correct   password
        portno_simulation = "1200"
        message = "LOGIN " + "Hassan_Tobgy" + " " + "Hassan_ELTOB123#" + " " + portno_simulation

        self.tcpClientSocket.send(message.encode())
        response = self.tcpClientSocket.recv(1024).decode()
        self.assertEqual(response, "SUCCESS")
        # check online user with no on online just logged in user
        message = "CHECK-ONLINE"
        self.tcpClientSocket.send(message.encode())
        response = self.tcpClientSocket.recv(1024).decode().split()
        self.assertEqual(response[0], 'NOT-ONLINE')

        # Create ROOM with name that exists

        room_name = "Friends"
        message = "CREATE-ROOM " + room_name
        self.tcpClientSocket.send(message.encode())
        response = self.tcpClientSocket.recv(1024).decode()
        self.assertEqual(response, "ROOM-EXISTS")
        #trying to join room that does not exist
        room_name = "Spiderman"
        message = "JOIN-ROOM " + room_name + " " + "Hassan_Mohamed"
        self.tcpClientSocket.send(message.encode())
        response = self.tcpClientSocket.recv(1024).decode()
        self.assertEqual(response, "ROOM-NOT-EXIST")

        # join room that exists
        # Simulating Trying to make room while there already exists room with same name
        room_name = "Friends"
        message = "JOIN-ROOM " + room_name + " " + "Hassan_Mohamed"
        self.tcpClientSocket.send(message.encode())
        response = self.tcpClientSocket.recv(1024).decode()
        self.assertEqual(response, "ALREADY-JOINED")

        # GET_ROOM_PEERS
        message = "GET-ROOM-PEERS " + room_name
        self.tcpClientSocket.send(message.encode())
        response = self.tcpClientSocket.recv(1024).decode()
        self.assertIn('SENDING-USERNAMES', response)

        # LOGOUT
        message = "LOGOUT " + "Hassan_Tobgy"
        self.tcpClientSocket.send(message.encode())
        username = "Hassan"

        Online_flag = db.is_account_online(username)
        self.assertEqual(Online_flag, False)

    def test_integration12(self, db=db.DB()):
        # login with Wrong   password
        portno_simulation = "1200"
        message = "LOGIN " + "Mohamed_Khafagy" + " " + "Hassan_M" + " " + portno_simulation

        self.tcpClientSocket.send(message.encode())
        response = self.tcpClientSocket.recv(1024).decode()
        self.assertEqual(response, "WRONG-PASSWORD")
        # login with Correct   password
        portno_simulation = "1200"
        message = "LOGIN " + "Mohamed_Khafagy" + " " + "Hassan_Mohamed123#" + " " + portno_simulation

        self.tcpClientSocket.send(message.encode())
        response = self.tcpClientSocket.recv(1024).decode()
        self.assertEqual(response, "SUCCESS")
        # check online user with no on online just logged in user
        message = "CHECK-ONLINE"
        self.tcpClientSocket.send(message.encode())
        response = self.tcpClientSocket.recv(1024).decode().split()
        self.assertEqual(response[0], 'NOT-ONLINE')

        # Create ROOM with name that exists

        room_name = "Friends"
        message = "CREATE-ROOM " + room_name
        self.tcpClientSocket.send(message.encode())
        response = self.tcpClientSocket.recv(1024).decode()
        self.assertEqual(response, "ROOM-EXISTS")
        # trying to join room that does not exist
        room_name = "Spiderman"
        message = "JOIN-ROOM " + room_name + " " + "Mohamed_Khafagy"
        self.tcpClientSocket.send(message.encode())
        response = self.tcpClientSocket.recv(1024).decode()
        self.assertEqual(response, "ROOM-NOT-EXIST")
        #ENTERING ROOM THAT EXISTS
        room_name = "Friends"
        message = "JOIN-ROOM " + room_name + " " + "Mohamed_Khafagy"
        self.tcpClientSocket.send(message.encode())
        response = self.tcpClientSocket.recv(1024).decode()
        self.assertEqual(response, "SUCCESS")

        #LEAVING ROOM :
        room_name = "Friends"
        message = "LEAVE-ROOM " + room_name + " " + "Mohamed_Khafagy"
        self.tcpClientSocket.send(message.encode())
        response = self.tcpClientSocket.recv(1024).decode()
        self.assertEqual(response, "SUCCESS")


        # GET_ROOM_PEERS
        message = "GET-ROOM-PEERS " + room_name
        self.tcpClientSocket.send(message.encode())
        response = self.tcpClientSocket.recv(1024).decode()
        self.assertIn('SENDING-USERNAMES', response)

        # LOGOUT
        message = "LOGOUT " + "Mohamed_Khafagy"
        self.tcpClientSocket.send(message.encode())
        username = "Mohamed_Khafagy"

        Online_flag = db.is_account_online(username)
        self.assertEqual(Online_flag, False)

    def test_integration13(self, db=db.DB()):
        # Simulating making new user account
        message = "SIGNUP " + "HassanTobgy" + " " + "Mohamed_Khafagy456#"
        self.tcpClientSocket.send(message.encode())
        response = self.tcpClientSocket.recv(1024).decode()
        self.assertEqual(response, "SUCCESS")

        # login with Wrong   password
        portno_simulation = "1200"
        message = "LOGIN " + "HassanTobgy" + " " + "Hassan_ELTOB123$" + " " + portno_simulation
        self.tcpClientSocket.send(message.encode())
        response = self.tcpClientSocket.recv(1024).decode()
        self.assertEqual(response, "WRONG-PASSWORD")

        # login with Correct   password
        portno_simulation = "1200"
        message = "LOGIN " + "HassanTobgy" + " " + "Mohamed_Khafagy456#" + " " + portno_simulation

        self.tcpClientSocket.send(message.encode())
        response = self.tcpClientSocket.recv(1024).decode()
        self.assertEqual(response, "SUCCESS")
        # check online user with no on online just logged in user
        message = "CHECK-ONLINE"
        self.tcpClientSocket.send(message.encode())
        response = self.tcpClientSocket.recv(1024).decode().split()
        self.assertEqual(response[0], 'NOT-ONLINE')

        # Create ROOM with name that exists

        room_name = "Friends"
        message = "CREATE-ROOM " + room_name
        self.tcpClientSocket.send(message.encode())
        response = self.tcpClientSocket.recv(1024).decode()
        self.assertEqual(response, "ROOM-EXISTS")

        # trying to join room that does not exist
        room_name = "Spiderman"
        message = "JOIN-ROOM " + room_name + " " + "HassanTobgy"
        self.tcpClientSocket.send(message.encode())
        response = self.tcpClientSocket.recv(1024).decode()
        self.assertEqual(response, "ROOM-NOT-EXIST")

        # join room that exists
        room_name = "Friends"
        message = "JOIN-ROOM " + room_name + " " + "HassanTobgy"
        self.tcpClientSocket.send(message.encode())
        response = self.tcpClientSocket.recv(1024).decode()
        self.assertEqual(response, "SUCCESS")
        #Leave room that joined
        room_name = "Friends"
        message = "LEAVE-ROOM " + room_name + " " + "HassanTobgy"
        self.tcpClientSocket.send(message.encode())
        response = self.tcpClientSocket.recv(1024).decode()
        self.assertEqual(response, "SUCCESS")

        #Create_new Room
        room_name = "IntegrationRoom"
        message = "CREATE-ROOM " + room_name
        self.tcpClientSocket.send(message.encode())
        response = self.tcpClientSocket.recv(1024).decode()
        self.assertEqual(response, "SUCCESS")

        # join room that exists that
        room_name = "IntegrationRoom"
        message = "JOIN-ROOM " + room_name + " " + "HassanTobgy"
        self.tcpClientSocket.send(message.encode())
        response = self.tcpClientSocket.recv(1024).decode()
        self.assertEqual(response, "SUCCESS")

        # GET_ROOM_PEERS
        message = "GET-ROOM-PEERS " + room_name
        self.tcpClientSocket.send(message.encode())
        response = self.tcpClientSocket.recv(1024).decode()
        self.assertIn('SENDING-USERNAMES', response)

        # LOGOUT
        message = "LOGOUT " + "HassanTobgy"
        self.tcpClientSocket.send(message.encode())
        username = "Hassan"

        Online_flag = db.is_account_online(username)
        self.assertEqual(Online_flag, False)
    # ----





if __name__ == "__main__":
    unittest.main()
