from burp import IBurpExtender
from burp import IContextMenuFactory

form javax.swing import JManuItem
from java.util import List, ArrayList
from java.net import URL

import socket
import urllib
import json
import re
import base64
bing_api_key = "TWOJ KLUCZ"

class BurpExtender(IBurpExtender, IContextMenuFactory):

    def registerExtenderCallbacks(self, callbacks):

        self._callbacks         = callbacks
        self._helpers           = callbacks.getHelper()
        self.context            = None

        callbacks.setExtensionName("BHP Bing")
        callbacks.registerContextMenuFactory(self)

        return

    def createMenuItems(self, context_menu):

        self.context    = context_menu
        menu_list       = ArrayList()
        menu_list.add(JMenuItem("Wyslij do Bing", actionPerformed = self.bing_menu))

        return manu_list

    def bing_menu(self, event):

        http_traffic = self.context.getSelectedMessages()

        print "Wyroznionych zadan: %d" % len(http_traffic)

        for traffic in http_traffic:

            http_service    = traffic.getHttpService()
            host            = http_service.getHost()

            print "Host wybrany przez uzytkownika: %s" % host

            self.bing_search(host)

        return

    def bing_search(self, host):

        is_ip = re.match("[0-9]+(?:\.[0-9]+){3}", host)

        if is_ip:

            ip_address  = host
            domain      = False
        else:

            ip_address  = socket.gethostbyname(host)
            domain      = True

        bing_query_string = "'ip:%s'" % ip_address
        self.bing_query(bing_query_string)

        if domain:

            bing_query_string = "'domain:%s'" % host
            self.bing_query(bing_query_string)

    def bing_query(self, bing_query_string):

        print "Wyszukiwanie w Bing: " % bing_query_string

        quoted_query = urllib.quote(bing_query_string)

        http_request    = "GET https://api.datamarket.azure.com/Bing/Search/Web?$format=json&$top=20&Query=%s HTTP/1.1\r\n" % quoted_query
        http_request    += "Host: api.datamarket.azure.com\r\n"
        http_request    += "Connection: close\r\n"
        http_request    += "Authorization: Basic %s\r\n" % base64.b64encode(":%s" % bing_api_key)
        http_request    += "User-Agent: Lordaeron\r\n\r\n"

        json_body       = self.callbacks.makeHttpRequest("api.datamarket.azure.com", 443, True, http_request).tostring()

        try:

            r = json.loads(json_body)

            if len(r["d"]["results"]):
                for site in r["d"]["results"]:

                    print "*" * 100
                    print site['Title']
                    print site['Url']
                    print site['Description']
                    print "*" * 100

                    j_url = URL(site['Url'])

            if not self._callbacks.isInScope(j_url):

                print "Dodawanie do zakresu Burpa"
                self._callbacks.includeInScope(j_url)

        except:

            print "Brak wynikow w wyszukiwarce Bing"
            pass
            
        return
