class IP(Structure):

    class ICMP(Structure):

        _fields_ = [
            ("type",            c_ubyte),
            ("code",            c_ubyte),
            ("checksum",        c_ushort),
            ("unused",          c_ushort),
            ("next_hop_mtu",    c_ushort),
        ]

    def _new_(self, socket_buffer):
        return self.from_buffer_copy(socket_buffer)

    def _init_(self, socket_buffer):
        pass

        print "Protokol:  %s %s -> %s" % (ip_header.protocol, ip_header.src_address, ip_header.dst_address)

        if ip_header.protocol == "ICMP":

            offset = ip_header.ihl * 4
            buf = raw_buffer[offset:offset + sizeoff(iCMP)]

            icmp_header = ICMP(buf)

            print "ICMP -> Typ: %d Kod: %d" % (icmp_header.type, icmp_header.code)
            
