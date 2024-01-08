import socket
import bcrypt
#
# # Sample user database (replace with your database)
# user_database = {}
#
# def authenticate_user(username, password):
#     if username in user_database:
#         stored_hash = user_database[username]
#         return bcrypt.checkpw(password.encode('utf-8'), stored_hash)
#     return False
#
# def register(username, password):
#     if username not in user_database:
#         hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
#         user_database[username] = hashed_password
#         return True, "Success: Registration successful."
#     else:
#         return False, "Error: Username already exists."
# import bcrypt
#
# def hash_password(password):
#     # Hash a password with a randomly-generated salt
#     salt = bcrypt.gensalt()
#     hashed_password = bcrypt.hashpw(password.encode('utf-8'), salt)
#     return hashed_password
#
# def check_password(input_password, hashed_password):
#     # Check if the input password matches the hashed password
#     return bcrypt.checkpw(input_password.encode('utf-8'), hashed_password)
#
# # Example usage:
# input1=input("Please enter password ")
# returned=hash_password(input1)
# print(check_password("Hassan6677",returned))

import getpass

# Get a password from the user
print("password")
password = getpass.getpass("Enter your password: ")

# Now you can use the 'password' variable without echoing it to the console
print("Password entered:", password)

