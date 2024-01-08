from pymongo import MongoClient

# Includes database operations
class DB:
    # db initializations
    def __init__(self):
        self.client = MongoClient('mongodb://localhost:27017/')
        self.db = self.client['p2p']

    # checks if an account with the username exists
    def is_account_exist(self, username):
        return self.db.accounts.count_documents({'username': username}) > 0

    # registers a user
    def register(self, username, password):
        account = {
            "username": username,
            "password": password
        }
        self.db.accounts.insert_one(account)

    # retrieves the password for a given username
    def get_password(self, username):
        user_data = self.db.accounts.find_one({"username": username})
        return user_data["password"] if user_data else None

    # checks if an account with the username is online
    def is_account_online(self, username):
        return self.db.online_peers.count_documents({"username": username}) > 0


    #Get online users
    def accounts_online(self):
        if self.db.online_peers.count_documents({}) < 2:
            return 0
        else:
            online= self.db.online_peers.find()
            usernames=[]
            for p in online:
                usernames.append(p.get("username"))
            return usernames
    # logs in the user
    def user_login(self, username, ip,tcpport,udpport):
        online_peer = {
            "username": username,
            "ip": ip,
            "tcpport": tcpport,
            "udpport": udpport
        }
        self.db.online_peers.insert_one(online_peer)

    # logs out the user
    def user_logout(self, username):
        self.db.online_peers.delete_one({"username": username})

    # retrieves the ip address and the port number of the username
    def get_peer_ip_port(self, username):
        res = self.db.online_peers.find_one({"username": username})
        if res:
            return (res["ip"], res["udpport"])

    def search(self, username):
        res = self.db.online_peers.find_one({"username": username})
        if res:
            return (res["ip"], res["tcpport"])
    def create_chat_rooms(self,chatroom):
        new_room = {
            "room_name": chatroom
        }
        self.db.chat_rooms.insert_one(new_room)
    def delete_chat_rooms(self,chatroom):
        new_room = {
            "room_name": chatroom
        }
        self.db.chat_rooms.delete_one(new_room)
    def insert_peer_room(self,username,chatroom):
        chatroom_peer = {
            "room_name": chatroom,
            "username": username,
            "is_admin": "no"

        }
        self.db.chat_rooms_information.insert_one(chatroom_peer)

    def set_room_admin(self,username,chatroom):
        query = {"username": username, "room_name": chatroom}
        admin = self.db.chat_rooms_information.find_one(query)
        if admin:
            # Update the "is_admin" field to "yes"
            update_query = {"$set": {"is_admin": "yes"}}
            self.db.chat_rooms_information.update_one(query, update_query)


    def chatroom_exist(self,chatroom):
        return self.db.chat_rooms.count_documents({"room_name": chatroom}) > 0

    def is_peer_in_room(self,username,room_name):
        return self.db.chat_rooms_information.count_documents({  "room_name": room_name,"username": username}) > 0

    def peer_leave_room(self,username,room_name):
        remove_chatroom_peer = {
            "room_name": room_name,
            "username": username

        }
        self.db.chat_rooms_information.delete_one(remove_chatroom_peer)

    def check_last_user(self,room_name):
        return self.db.chat_rooms_information.count_documents({"room_name": room_name}) <1

    def retrieve_all_users(self,room_name):  # this will return list of usernames for users that are members of specific room
        online = self.db.chat_rooms_information.find()
        list_all_users = []
        for p in online:
            if p.get("room_name") == room_name:
                list_all_users.append(p.get("username"))
        return list_all_users

    #function to show rooms available in the server
    def show_rooms(self):
        if self.db.chat_rooms.count_documents({}) < 1:
            return 0
        rooms = self.db.chat_rooms.find()
        room_name = []
        for p in rooms:
            room_name.append(p.get("room_name"))
        return room_name

    def connect_peer(self, room_name, username):
        in_room = {
            "room_name": room_name,
            "username": username
        }
        self.db.chat_rooms_currently_in.insert_one(in_room)

    def disconnect_peer(self, room_name, username):
        in_room = {
            "room_name": room_name,
            "username": username
        }
        self.db.chat_rooms_currently_in.delete_one(in_room)
        
    def retrieve_users_in_room(self, room_name):
        online = self.db.chat_rooms_currently_in.find()
        list_all_users = []
        for p in online:
            if p.get("room_name") == room_name:
                list_all_users.append(p.get("username"))
        return list_all_users

    def is_user_in_room_currently(self, room_name, username):
        return self.db.chat_rooms_currently_in.count_documents({"room_name": room_name, "username": username}) > 0