import os

def run(**args):

    print "[*] W module dirlister."
    files = os.listdir(".")

    return str(files)
