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
        self.serverName = self.peerServerHostname
        # port number of the server
        self.serverPort = 15600
        # tcp socket connection to server
        self.tcpClientSocket = socket(AF_INET, SOCK_STREAM)
        self.tcpClientSocket.connect((self.serverName, self.serverPort))

    def test_CreateRoom_Happy_scenario(self):
        # Simulating Creating New room
        room_name="Friends"
        message = "CREATE-ROOM " + room_name
        self.tcpClientSocket.send(message.encode())
        response = self.tcpClientSocket.recv(1024).decode()
        self.assertEqual(response, "ROOM-EXISTS")



    def test_CreateRoom_Already_Exists(self):
        # Simulating Trying to make room while there already exists room with same name
        room_name="Friends"
        message = "CREATE-ROOM " + room_name
        self.tcpClientSocket.send(message.encode())
        response = self.tcpClientSocket.recv(1024).decode()
        self.assertEqual(response,"SUCCESS")

    def test_JoinRoom(self):
        # Simulating Trying to make room while there already exists room with same name
        room_name = "Friends"
        message = "JOIN-ROOM " + room_name+" "+"Hassan_Mohamed"
        self.tcpClientSocket.send(message.encode())
        response = self.tcpClientSocket.recv(1024).decode()
        self.assertEqual(response, "SUCCESS")



    def test_JoinRoom_Already_joined(self):
        # Simulating Trying to make room while there already exists room with same name
        room_name = "Friends"
        message = "JOIN-ROOM " + room_name+" "+"Hassan_Mohamed"
        self.tcpClientSocket.send(message.encode())
        response = self.tcpClientSocket.recv(1024).decode()
        self.assertEqual(response, "ALREADY-JOINED")

    def test_JoinRoom_Doesnot_exist(self):
        room_name = "ROOM1"
        message = "JOIN-ROOM " + room_name+" "+"Hassan_Mohamed"
        self.tcpClientSocket.send(message.encode())
        response = self.tcpClientSocket.recv(1024).decode()
        self.assertEqual(response, "ROOM-NOT-EXIST")

    def test_LeaveRoom(self):
        room_name = "Friends"
        message = "LEAVE-ROOM " + room_name+ " "+"Hassan_Mohamed"
        self.tcpClientSocket.send(message.encode())
        response = self.tcpClientSocket.recv(1024).decode()
        self.assertEqual(response, "SUCCESS")
    def test_LeaveRoom_Room_not_exist(self):
        room_name = "Batman"
        message = "LEAVE-ROOM " + room_name+" "+"Hassan_Mohamed"
        self.tcpClientSocket.send(message.encode())
        response = self.tcpClientSocket.recv(1024).decode()
        self.assertEqual(response, "ROOM-NOT-EXIST")

    def test_get_room_peers(self):
        room_name="Friends"
        message = "GET-ROOM-PEERS " + room_name
        self.tcpClientSocket.send(message.encode())
        response = self.tcpClientSocket.recv(1024).decode()
        self.assertIn('SENDING-USERNAMES', response)








    # ----


if __name__ == "__main__":
    unittest.main()
