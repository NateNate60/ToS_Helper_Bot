import socket
import json

def fetch_reports (user: str, guilty_only: bool) -> list :
    clientSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    clientSocket.connect(("127.0.0.1",54296))
    clientSocket.send(user.encode() if guilty_only else ('*' + user).encode())
    string = ""
    while ("\26" not in string) :
        string += str(clientSocket.recv(16), "utf-8")
    return json.loads(string[:-1])