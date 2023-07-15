#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# ineptepub.py
# Copyright © 2009-2022 by i♥cabbages, Apprentice Harper et al.

# Released under the terms of the GNU General Public Licence, version 3
# <http://www.gnu.org/licenses/>

"""
Decrypt Adobe Digital Editions encrypted ePub books.
"""

from decrypt.params import KEYPATH
__license__ = 'GPL v3'
__version__ = "8.0"

import sys
import os
import traceback
import base64
import zlib
from zipfile import ZipInfo, ZipFile, ZIP_STORED, ZIP_DEFLATED
from decrypt.zeroedzipinfo import ZeroedZipInfo
from contextlib import closing
from lxml import etree
from uuid import UUID
import hashlib

try:
    from Cryptodome.Cipher import AES, PKCS1_v1_5
    from Cryptodome.PublicKey import RSA
except ImportError:
    from Crypto.Cipher import AES, PKCS1_v1_5
    from Crypto.PublicKey import RSA


def unpad(data, padding=16):
    if sys.version_info[0] == 2:
        pad_len = ord(data[-1])
    else:
        pad_len = data[-1]

    return data[:-pad_len]


class ADEPTError(Exception):
    pass

class ADEPTNewVersionError(Exception):
    pass

META_NAMES = ('mimetype', 'META-INF/rights.xml')
NSMAP = {'adept': 'http://ns.adobe.com/adept',
         'enc': 'http://www.w3.org/2001/04/xmlenc#'}

class Decryptor(object):
    def __init__(self, bookkey, encryption):
        enc = lambda tag: '{%s}%s' % (NSMAP['enc'], tag)
        self._aes = AES.new(bookkey, AES.MODE_CBC, b'\x00'*16)
        self._encryption = etree.fromstring(encryption)
        self._encrypted = encrypted = set()
        self._encryptedForceNoDecomp = encryptedForceNoDecomp = set()
        self._otherData = otherData = set()

        self._json_elements_to_remove = json_elements_to_remove = set()
        self._has_remaining_xml = False
        expr = './%s/%s/%s' % (enc('EncryptedData'), enc('CipherData'),
                               enc('CipherReference'))
        for elem in self._encryption.findall(expr):
            path = elem.get('URI', None)
            encryption_type_url = (elem.getparent().getparent().find("./%s" % (enc('EncryptionMethod'))).get('Algorithm', None))
            if path is not None:
                if (encryption_type_url == "http://www.w3.org/2001/04/xmlenc#aes128-cbc"):
                    # Adobe
                    path = path.encode('utf-8')
                    encrypted.add(path)
                    json_elements_to_remove.add(elem.getparent().getparent())
                elif (encryption_type_url == "http://ns.adobe.com/adept/xmlenc#aes128-cbc-uncompressed"):
                    # Adobe uncompressed, for stuff like video files
                    path = path.encode('utf-8')
                    encryptedForceNoDecomp.add(path)
                    json_elements_to_remove.add(elem.getparent().getparent())
                else:
                    path = path.encode('utf-8')
                    otherData.add(path)
                    self._has_remaining_xml = True

        for elem in json_elements_to_remove:
            elem.getparent().remove(elem)

    def check_if_remaining(self):
        return self._has_remaining_xml

    def get_xml(self):
        return "<?xml version=\"1.0\" encoding=\"UTF-8\"?>\n" + etree.tostring(self._encryption, encoding="utf-8", pretty_print=True, xml_declaration=False).decode("utf-8")


    def decompress(self, bytes):
        dc = zlib.decompressobj(-15)
        try:
            decompressed_bytes = dc.decompress(bytes)
            ex = dc.decompress(b'Z') + dc.flush()
            if ex:
                decompressed_bytes = decompressed_bytes + ex
        except:
            # possibly not compressed by zip - just return bytes
            return bytes
        return decompressed_bytes

    def decrypt(self, path, data):
        if path.encode('utf-8') in self._encrypted or path.encode('utf-8') in self._encryptedForceNoDecomp:
            data = self._aes.decrypt(data)[16:]
            if type(data[-1]) != int:
                place = ord(data[-1])
            else:
                place = data[-1]
            data = data[:-place]
            if not path.encode('utf-8') in self._encryptedForceNoDecomp:
                data = self.decompress(data)
        return data

# check file to make check whether it's probably an Adobe Adept encrypted ePub
def adeptBook(inpath):
    with closing(ZipFile(open(inpath, 'rb'))) as inf:
        namelist = set(inf.namelist())
        if 'META-INF/rights.xml' not in namelist or \
           'META-INF/encryption.xml' not in namelist:
            return False
        try:
            rights = etree.fromstring(inf.read('META-INF/rights.xml'))
            adept = lambda tag: '{%s}%s' % (NSMAP['adept'], tag)
            expr = './/%s' % (adept('encryptedKey'),)
            bookkey = ''.join(rights.findtext(expr))
            if len(bookkey) in [192, 172, 64]:
                return True
        except:
            # if we couldn't check, assume it is
            return True
    return False

def isPassHashBook(inpath):
    # If this is an Adobe book, check if it's a PassHash-encrypted book (B&N)
    with closing(ZipFile(open(inpath, 'rb'))) as inf:
        namelist = set(inf.namelist())
        if 'META-INF/rights.xml' not in namelist or \
           'META-INF/encryption.xml' not in namelist:
            return False
        try:
            rights = etree.fromstring(inf.read('META-INF/rights.xml'))
            adept = lambda tag: '{%s}%s' % (NSMAP['adept'], tag)
            expr = './/%s' % (adept('encryptedKey'),)
            bookkey = ''.join(rights.findtext(expr))
            if len(bookkey) == 64:
                return True
        except:
            pass

    return False

# Checks the license file and returns the UUID the book is licensed for.
# This is used so that the Calibre plugin can pick the correct decryption key
# first try without having to loop through all possible keys.
def adeptGetUserUUID(inpath):
    with closing(ZipFile(open(inpath, 'rb'))) as inf:
        try:
            rights = etree.fromstring(inf.read('META-INF/rights.xml'))
            adept = lambda tag: '{%s}%s' % (NSMAP['adept'], tag)
            expr = './/%s' % (adept('user'),)
            user_uuid = ''.join(rights.findtext(expr))
            if user_uuid[:9] != "urn:uuid:":
                return None
            return user_uuid[9:]
        except:
            return None

def removeHardening(rights, keytype, keydata):
    adept = lambda tag: '{%s}%s' % (NSMAP['adept'], tag)
    textGetter = lambda name: ''.join(rights.findtext('.//%s' % (adept(name),)))

    # Gather what we need, and generate the IV
    resourceuuid = UUID(textGetter("resource"))
    deviceuuid = UUID(textGetter("device"))
    fullfillmentuuid = UUID(textGetter("fulfillment")[:36])
    kekiv = UUID(int=resourceuuid.int ^ deviceuuid.int ^ fullfillmentuuid.int).bytes

    # Derive kek from just "keytype"
    rem = int(keytype, 10) % 16
    H = hashlib.sha256(keytype.encode("ascii")).digest()
    kek = H[2*rem : 16 + rem] + H[rem : 2*rem]

    return unpad(AES.new(kek, AES.MODE_CBC, kekiv).decrypt(keydata), 16) # PKCS#7

def decryptBook(userkey, inpath, outpath):
    with closing(ZipFile(open(inpath, 'rb'))) as inf:
        namelist = inf.namelist()
        if 'META-INF/rights.xml' not in namelist or \
           'META-INF/encryption.xml' not in namelist:
            print("{0:s} is DRM-free.".format(os.path.basename(inpath)))
            return 1
        for name in META_NAMES:
            namelist.remove(name)
        try:
            rights = etree.fromstring(inf.read('META-INF/rights.xml'))
            adept = lambda tag: '{%s}%s' % (NSMAP['adept'], tag)
            expr = './/%s' % (adept('encryptedKey'),)
            bookkeyelem = rights.find(expr)
            bookkey = bookkeyelem.text
            keytype = bookkeyelem.attrib.get('keyType', '0')
            if len(bookkey) >= 172 and int(keytype, 10) > 2:
                print("{0:s} is a secure Adobe Adept ePub with hardening.".format(os.path.basename(inpath)))
            elif len(bookkey) == 172:
                print("{0:s} is a secure Adobe Adept ePub.".format(os.path.basename(inpath)))
            elif len(bookkey) == 64:
                print("{0:s} is a secure Adobe PassHash (B&N) ePub.".format(os.path.basename(inpath)))
            else:
                print("{0:s} is not an Adobe-protected ePub!".format(os.path.basename(inpath)))
                return 1

            if len(bookkey) != 64:
                # Normal or "hardened" Adobe ADEPT
                rsakey = RSA.importKey(userkey) # parses the ASN1 structure
                bookkey = base64.b64decode(bookkey)
                if int(keytype, 10) > 2:
                    bookkey = removeHardening(rights, keytype, bookkey)
                try:
                    bookkey = PKCS1_v1_5.new(rsakey).decrypt(bookkey, None) # automatically unpads
                except ValueError:
                    bookkey = None

                if bookkey is None:
                    print("Could not decrypt {0:s}. Wrong key".format(os.path.basename(inpath)))
                    return 2
            else:
                # Adobe PassHash / B&N
                key = base64.b64decode(userkey)[:16]
                bookkey = base64.b64decode(bookkey)
                bookkey = unpad(AES.new(key, AES.MODE_CBC, b'\x00'*16).decrypt(bookkey), 16) # PKCS#7

                if len(bookkey) > 16:
                    bookkey = bookkey[-16:]

            encryption = inf.read('META-INF/encryption.xml')
            decryptor = Decryptor(bookkey, encryption)
            kwds = dict(compression=ZIP_DEFLATED, allowZip64=False)
            with closing(ZipFile(open(outpath, 'wb'), 'w', **kwds)) as outf:

                for path in (["mimetype"] + namelist):
                    data = inf.read(path)
                    zi = ZipInfo(path)
                    zi.compress_type=ZIP_DEFLATED

                    if path == "mimetype":
                        zi.compress_type = ZIP_STORED

                    elif path == "META-INF/encryption.xml":
                        # Check if there's still something in there
                        if (decryptor.check_if_remaining()):
                            data = decryptor.get_xml()
                            print("Adding encryption.xml for the remaining embedded files.")
                            # We removed DRM, but there's still stuff like obfuscated fonts.
                        else:
                            continue


                    try:
                        # get the file info, including time-stamp
                        oldzi = inf.getinfo(path)
                        # copy across useful fields
                        zi.date_time = oldzi.date_time
                        zi.comment = oldzi.comment
                        zi.extra = oldzi.extra
                        zi.internal_attr = oldzi.internal_attr
                        # external attributes are dependent on the create system, so copy both.
                        zi.external_attr = oldzi.external_attr

                        zi.volume = oldzi.volume
                        zi.create_system = oldzi.create_system
                        zi.create_version = oldzi.create_version

                        if any(ord(c) >= 128 for c in path) or any(ord(c) >= 128 for c in zi.comment):
                            # If the file name or the comment contains any non-ASCII char, set the UTF8-flag
                            zi.flag_bits |= 0x800
                    except:
                        pass

                    # Python 3 has a bug where the external_attr is reset to `0o600 << 16`
                    # if it's NULL, so we need a workaround:
                    if zi.external_attr == 0: 
                        zi = ZeroedZipInfo(zi)


                    if path == "META-INF/encryption.xml":
                        outf.writestr(zi, data)
                    else:
                        outf.writestr(zi, decryptor.decrypt(path, data))
        except:
            print("Could not decrypt {0:s} because of an exception:\n{1:s}".format(os.path.basename(inpath), traceback.format_exc()))
            return 2
    return 0


def decryptEPUB(inpath):
    keypath = KEYPATH
    outpath = os.path.basename(inpath).removesuffix(".epub") + "_decrypted.epub"
    userkey = open(keypath,'rb').read()
    result = decryptBook(userkey, inpath, outpath)
    if result == 0:
        print("Successfully decrypted")
        return outpath
    else:
        print("Decryption failed")
        return None
