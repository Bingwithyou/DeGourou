from setup.loginAccount import loginAndGetKey
from setup.fulfill import downloadFile

from decrypt.decodePDF import decryptPDF
from decrypt.decodeEPUB import decryptEPUB

import argparse
from os import mkdir, remove, rename
from os.path import exists

from setup.params import FILE_DEVICEKEY, FILE_DEVICEXML, FILE_ACTIVATIONXML
from decrypt.params import KEYPATH
from setup.data import createDefaultFiles
from setup.ia import SESSION_FILE, manage_login, get_book, return_book


def loginADE(email, password):
    if email is None or password is None:
        print("Email or Password cannot be empty")
        print()
        return
    if not exists('account'): mkdir('account')
    loginAndGetKey(email, password)
    print()

def loginIA(email,password):
    if email is None or password is None:
        print("Email or Password cannot be empty")
        print()
        return
    manage_login(email,password)
    print()

def main(acsmFile, outputFilename):
    if not exists('account'): mkdir('account')

    # setting up the account and keys
    if not (exists(FILE_ACTIVATIONXML) and exists(FILE_DEVICEXML) and exists(FILE_DEVICEKEY) and exists(KEYPATH)):
        createDefaultFiles()
    print()

    # cheek for file existance
    if not exists(acsmFile):
        print(f"{acsmFile} file does not exist")
        print()
        return

    # download
    encryptedFile = downloadFile(acsmFile)
    print(encryptedFile)
    print()

    # decrypt
    if encryptedFile is None:
        print("Failed to Download, try decrypting from ACSM file")
        return
    if encryptedFile.endswith(".pdf"):
        decryptedFile = decryptPDF(encryptedFile)
    elif encryptedFile.endswith(".epub"):
        decryptedFile = decryptEPUB(encryptedFile)
    else:
        print("File format not supported")
        print()
        return

    remove(encryptedFile)
    if outputFilename is None:
        tempName = encryptedFile
    else:
        tempName = outputFilename
    rename(decryptedFile, tempName)
    print(tempName)
    print()

def handle_IA(url,format):
    if not exists(SESSION_FILE):
        print("Login to InternetArchive first or give ACSm file as input")
        return
    acsmFile = get_book(url,format)
    if acsmFile is None:
        print("Could not get Book, try using ACSm file as input")
        return
    main(acsmFile,None)
    remove(acsmFile)
    if(return_book(url) is None):
        print("Please return it yourself")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Download and Decrypt an encrypted PDF or EPUB file.")
    parser.add_argument("-f", type=str, nargs='?', default=None, help="path to the ACSM file")
    parser.add_argument("-u", type=str, nargs='?', default=None, help="book url from InternetArchive")
    parser.add_argument("-t", type=str, nargs='?', default='pdf', help="book file type/format/extension for book url (defaults to PDF)")
    parser.add_argument("-o", type=str, nargs='?', default=None, help="output file name")
    parser.add_argument("-la", action="store_true", help="login to your ADE account.")
    parser.add_argument("-li", action="store_true", help="login to your InternetArchive.")
    parser.add_argument("-e", type=str,  nargs='?', default=None, help="email/username")
    parser.add_argument("-p", type=str,  nargs='?', default=None, help="password")
    parser.add_argument("-lo", action="store_true", help="logout from all")
    args = parser.parse_args()

    # Logout
    if args.lo:
        from shutil import rmtree
        rmtree("account")
        mkdir('account')
        print()
        print("Logout Sucessfull")
        print()

    # ADE login
    elif args.la:
        print()
        print("chose login for ADE")
        loginADE(args.e, args.p)

    # IA login
    elif args.li:
        print()
        print("chose login for InternetArchive")
        loginIA(args.e, args.p)

    # Book url
    elif args.u:
        print()
        if not args.t in ['pdf','epub']:
            print("only PDF and EPUB are supported")
        else: 
            handle_IA(args.u, args.t)
        print()

    # check for default value
    elif args.f == None:
        if exists("URLLink.acsm"):
            args.f = "URLLink.acsm"
            main(args.f, args.o)
        else: parser.print_help()

    else:
        main(args.f, args.o)
