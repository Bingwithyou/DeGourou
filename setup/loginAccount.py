#!/usr/bin/env python3
# -*- coding: utf-8 -*-

'''
This is an experimental Python version of libgourou. 
'''

from setup.libadobe import createDeviceKeyFile, FILE_DEVICEKEY, FILE_DEVICEXML, FILE_ACTIVATIONXML
from setup.libadobeAccount import createDeviceFile, createUser, signIn, activateDevice, exportAccountEncryptionKeyDER, getAccountUUID
from os.path import exists

VAR_MAIL = ""
VAR_PASS = ""
VAR_VER = 1 # None # 1 for ADE2.0.1, 2 for ADE3.0.1
from decrypt.params import KEYPATH

#################################################################

def loginAndGetKey(email, password):

    global VAR_MAIL
    global VAR_PASS
    global VAR_VER
    global KEYPATH

    # acc files
    if True:
        
        VAR_MAIL = email
        VAR_PASS = password
        
        print("Logging in")
        createDeviceKeyFile()

        success = createDeviceFile(True, VAR_VER)
        if (success is False):
            print("Error, couldn't create device file.")
            return

        success, resp = createUser(VAR_VER, None)
        if (success is False):
            print("Error, couldn't create user: %s" % resp)
            return

        success, resp = signIn("AdobeID", VAR_MAIL, VAR_PASS)
            
        if (success is False):
            print("Login unsuccessful: " + resp)
            return

        success, resp = activateDevice(VAR_VER, None)
        if (success is False):
            print("Couldn't activate device: " + resp)
            return

        print("Authorized to account " + VAR_MAIL)


    # KEY
    if not exists(KEYPATH):
        print("Exporting keys ...")
        try: 
            account_uuid = getAccountUUID()
            if (account_uuid is not None):
                filename = KEYPATH
                success = exportAccountEncryptionKeyDER(filename)
                if (success is False):
                    print("Couldn't export key.")
                    return
                print("Successfully exported key for account " + VAR_MAIL + " to file " + filename)

            else:
                print("failed")
 
        except Exception as e: 
                print(e)


    print('All Set')
    print()