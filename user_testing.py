import unittest
from unittest.mock import patch
import db 
from socket import *
import time





class TestPeerMain(unittest.TestCase):
    def setUp(self):
        hostname = gethostname()
        try:
            self.peerServerHostname = gethostbyname(hostname)  # Get IP address
        except gaierror:  # gaierror means host name couldn't be resolved
            import netifaces as ni
            self.peerServerHostname = ni.ifaddresses('en0')[ni.AF_INET][0][
                'addr']  # Get IP adderess using the en0 interface of IPV4

        # ip address of this peer
        self.peerServerHostname = gethostbyname(gethostname())
        # ip address of the server
        self.serverName =  self.peerServerHostname
        # port number of the server
        self.serverPort = 15600
        # tcp socket connection to server
        self.tcpClientSocket = socket(AF_INET, SOCK_STREAM)
        self.tcpClientSocket.connect((self.serverName, self.serverPort))




    def test_CreateAccount_Happy_scenario(self):
     #Simulating making new user account
        message = "SIGNUP " + "Hassan_Mohamed" + " " + "Hassan_Mohamed123#"
        self.tcpClientSocket.send(message.encode())
        response = self.tcpClientSocket.recv(1024).decode()
        self.assertEqual(response, "SUCCESS")

    def test_CreateAccount_failure_scenario(self):
        # Simulating making new user account with username already exists
        message = "SIGNUP " + "Hassan_Mohamed" + " " + "sonson_123#"
        self.tcpClientSocket.send(message.encode())
        response = self.tcpClientSocket.recv(1024).decode()
        self.assertEqual(response, "USERNAME-EXISTS")

    def test_login_Wrong_password(self):
        # Simulating wrong password as if user tries to enter using saved username in db but with wrong password
        # saved password in db is HassanEl-Tobgy123
        portno_simulation = "1200"
        portno2_simulation = "1700"
        message = "LOGIN " + "Hassan_Mohamed" + " " + "Mohamedkhafagy123" + " " + portno_simulation + " " + portno2_simulation

        self.tcpClientSocket.send(message.encode())
        response = self.tcpClientSocket.recv(1024).decode()
        self.assertEqual(response, "USER-ONLINE")


    def test_login_Happy_senario(self) :
        # Simulating Right  password entered  as if user tries to enter using saved username in db but with wrong password
        #saved password in db is HassanEl-Tobgy123
        portno_simulation = "1200"
        portno2_simulation = "1700"
        message = "LOGIN " + "Hassan_Mohamed" + " " +"Hassan_Mohamed123#"+" "+portno_simulation + " " + portno2_simulation

        self.tcpClientSocket.send(message.encode())
        response = self.tcpClientSocket.recv(1024).decode()
        self.assertEqual(response, "SUCCESS")



    def test_login_UserNotExit(self):
       #simulating trying to login without registering
        portno_simulation = "1200"
        portno2_simulation = "1700"
        message = "LOGIN " + "seif" + " " + "seif123" + " " + portno_simulation+ " " + portno2_simulation

        self.tcpClientSocket.send(message.encode())
        response = self.tcpClientSocket.recv(1024).decode()
        self.assertEqual(response, "USER-NOT-EXIST")

    def test_login_UserOnline(self):
        # Simulating user trying to login while he is already logged in
        portno_simulation = "1200"
        portno2_simulation = "1700"
        message = "LOGIN " + "Hassan_Mohamed" + " " + "Hassan_Mohamed123#" + " " + portno_simulation + " " + portno2_simulation

        self.tcpClientSocket.send(message.encode())
        response = self.tcpClientSocket.recv(1024).decode()
        self.assertEqual(response, "USER-ONLINE")




    def test_check_online_users_no_one_online(self):
        # Checking online users while no one is online

        message = "CHECK-ONLINE"
        self.tcpClientSocket.send(message.encode())
        response = self.tcpClientSocket.recv(1024).decode().split()
        self.assertEqual(response[0], "NOT-ONLINE")

    def test_check_online_users_exist_online_users(self):
        #checking online users while there exist users that are online
        message = "CHECK-ONLINE"
        self.tcpClientSocket.send(message.encode())
        response = self.tcpClientSocket.recv(1024).decode().split()
        self.assertEqual(response[0], "NOT-ONLINE")
    def test_search_Happy_Senario(self):
        # simulating if an account with username exists and is online
        message = "SEARCH "+ "Hassan_Mohamed"
        self.tcpClientSocket.send(message.encode())
        response = self.tcpClientSocket.recv(1024).decode().split()
        self.assertEqual(response[0], "USER-NOT-ONLINE")

    def test_logout(self, db=db.DB()):
        message = "LOGOUT " + "Hassan_Mohamed"
        self.tcpClientSocket.send(message.encode())
        username="Hassan"

        Online_flag=db.is_account_online(username)
        self.assertEqual(Online_flag,False)



    def test_search_Failure_Senario(self):
        # simulating if an account with username exists and is online
        message = "SEARCH "+ "Hassan_Mohamed"
        self.tcpClientSocket.send(message.encode())
        response = self.tcpClientSocket.recv(1024).decode().split()
        self.assertEqual(response[0], "USER-NOT-ONLINE")













    #----




if __name__ == "__main__":
    unittest.main()
