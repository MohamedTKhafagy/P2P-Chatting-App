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


    # Get online users
    # Returns a list of online users' usernames
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
    def user_login(self, username, ip):
        online_peer = {
            "username": username,
            "ip": ip
        }
        self.db.online_peers.insert_one(online_peer)

    # logs out the user
    def user_logout(self, username):
        self.db.online_peers.delete_one({"username": username})

    # retrieves the ip address and the port number of the username
    def get_peer_ip_port(self, username):
        res = self.db.online_peers.find_one({"username": username})
        return (res["ip"], res["port"]) if res else (None, None)
