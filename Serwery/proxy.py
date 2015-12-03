import sys
import socket
import threading

def server_loop(local_host, local_port, remote_host, remote_port, receive_first):
    
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        server.bind((local_host, local_port))
    except:
        print "[*] Nieudana proba naluchu na porcie %s:%d" % (local_host, local_port)
        print "[!!] Poszukaj innego gniazda lub zdobadz odpowiednie uprawnienia."
        sys.exit()
        print "[*] Nasluchiwanie na porcie %s:%d" % (local_host, local_port)
        
        server.listen(5)
        
        while True:
            client_socket, addr = server.accept()
            
            # wydruk informacji o polaczeniu lokalnym
            print "[==>] Otrzymano polaczenie przychodzace od %s:%d" % (addr[0],addr[1])
            
            # uruchomienie watku do wspolpracy ze zdalnym hostem
            proxy_thread = threading.Thread(target=proxy_handler, args=(client_socket, remote_host, remote_port, receive_first))
            
            proxy_thread.start()
            
def main():
    
    # zadnego dziwnego przetworzenia wiersza polecen
    if len(sys.argv[1:]) !=5:
        print "Sposob uzycia: ./proxy.py [localhost] [localport] [remotehost] [remoteport] [receive_first]" 
        print "Przyklad: ./proxy.py 127.0.0.1 9000 10.12.132.1 9000 True"
        sys.exit()
    
    # konfiguracja lokalnych parametrow nasluchu 
    local_host = sys.argv[1]
    local_port = int(sys.argv[2])
    
    # ustwienie zdalnego celu
    remote_host = sys.argv[3]
    remote_port = int(sys.argv[4])
    
    # nazakujemy proxy nawiazanie polaczenia i odebranie danych przed wyslaniem do zdalnego hosta
    receive_first = sys.argv[5]
    
    if "True" in receive_first:
        receive_first = True
    else:
        receive_first = False
        
    # wlaczmy gniazdo do nasluchu 
    server_loop(local_host, local_port, remote_host, remote_port, receive_first)
    
main()

def proxy_handler(client_socket, remote_host, remote_port, receive_first):
    
    # polaczenie ze zdalnym hostem
    remote_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    remote_socket.connet((remote_host, remote_port))
    
    # odebranie danych od zdalnego hosta w razie potrzeby 
    if receive_first:
        
        remote_buffer = receive_from(receive_socket)
        hexdump(remote_buffer)
        
        # wysylanie danych do procedury obslugi odpowiedzi
        remote_buffer = response_handler(remote_buffer)
        
        # jesli mamy dane do wyslania do klienta lokalnego to je wysylamy
        if len(remote_buffer):
            print "[<==] Wysylanie %d bajtow do localhost." % len(remote_buffer)
            client_socket.send(remote_buffer)
            
    # uruchamiamy petle w ktorej odczytujemy dane z hosta lokalnego wysylamy dane do hosta zdalnego wysylamy dane do hosta lokalnego
    # wszystko powtarzamy
    while True:
        
        # odczyt z lokalnego hosta
        local_buffer = recieve_from(client_socket)
        
        if len(local_buffer):
            
            print "[==>] Odebrano %d bajtow od localhost." % len(local_buffer)
            hexdump(local_buffer)
            
            # wysylanie danych do procedury obslugi zadan
            local_buffer = request_handler(local_buffer)
            
            # wysylanie danych do zdalnego hosta
            remote_socket.send(local_buffer)
            print "[==>] Wyslano do zdalnego hosta."
            
            # odebranie odpowiedzi
            remote_buffer = receive_from(remote_socket)
            
            if len(remote_socket):
                
                print "[<==] Odebrano %d bajtow od zdalnego hosta." % len(remote_buffer)
                hexdump(remote_buffer)
                
                # wysylanie danych do procedury obslugi odpowiedzi
                remote_buffer = response_handler(remote_buffer)
                
                # wysylanie dopowiedzi do lokalnego gniazda
                client_socket.send(remote_buffer)
                
                print "[<==] Wyslano do localhost."
                
            # jesli nie ma wiecej danych po zadnej ze stron zamykamy polaczenia 
            if not len(local_buffer) or not len(remote_buffer):
                client_socket.close()
                remote_socket.close()
                print "[*] Nie ma wiecej danych. Zamykanie polaczenia"
                
                break
            
# jest to elegancka funkcja do robienia zrzutow szesnastkowych wydobyta wprost z komentarzy na tej stronie
# https://code.activestate.com/recipes/142812-hex-dumper/
            
def hexdump(src , length=16):
    result = []
    digits = 4 if isinstance(src, unicode) else 2
    for i in xrange(0, len(src), length):
        s = src[i:i+length]
        hexa = b' '.join(["%0*x" % (digits, ord(x)) for x in s])
        tex = b''.join([x if 0x20 <= ord(x) < 0x7F else b'.' for x in s])
        result.append(b"%04X %-*s %s" % (i, length*(digits+1), hexa, text))
        
    print b'\n'.join(result) 

def recive_from(connection):
    buffer = ""
    
    # ustawiamy 2-sekundowy limit czasu w niektorych przypadkach moze byc konieczna zmiana tej wartosci
    
    connection.settimeout(2)
    
    try: 
        # wczytujemy dane do bufora, az wczytamy wszystkie albo sie skonczy nam czas
        while True:
            
                   data = connection.recv(4096)
                   if not data:
                               break
                   buffer += data
             
    except:
        pass
    return buffer

# modyfikujemy zadania przeznaczone dla zdalnego hosta
def request_handler(buffer):
    # modyfikujemy pakiety
    return buffer

# modfikujemy odpowiedzi przeznaczone dla lokalnego hosta
def response_handler(buffer):
    # modyfikujemy pakiety
    return buffer


            
