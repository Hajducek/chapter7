import socket

target_host = "www.google.com"
target_port = 80

# utworzenie gniazda obiektu
client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# polaczenie z klientem
client.connect((target_host,target_port))

# wysylanie danych
client.send("GET / HTTP/1.1\r\nHost: google.com\r\n\r\n")

# odebranie danych
response = client.recv(4096)

print response 