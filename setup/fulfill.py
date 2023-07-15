#!/usr/bin/env python3
# -*- coding: utf-8 -*-

'''
This is an experimental Python version of libgourou. 
'''

# pyright: reportUndefinedVariable=false

import os, time, shutil

import zipfile
from lxml import etree

from setup.libadobe import sendHTTPRequest_DL2FILE
from setup.libadobeFulfill import buildRights, fulfill
from setup.libpdf import patch_drm_into_pdf

#######################################################################


def download(replyData):
    # replyData: str
    adobe_fulfill_response = etree.fromstring(replyData)
    NSMAP = { "adept" : "http://ns.adobe.com/adept" }
    adNS = lambda tag: '{%s}%s' % ('http://ns.adobe.com/adept', tag)
    adDC = lambda tag: '{%s}%s' % ('http://purl.org/dc/elements/1.1/', tag)

    # print (replyData)

    download_url = adobe_fulfill_response.find("./%s/%s/%s" % (adNS("fulfillmentResult"), adNS("resourceItemInfo"), adNS("src"))).text
    resource_id = adobe_fulfill_response.find("./%s/%s/%s" % (adNS("fulfillmentResult"), adNS("resourceItemInfo"), adNS("resource"))).text
    license_token_node = adobe_fulfill_response.find("./%s/%s/%s" % (adNS("fulfillmentResult"), adNS("resourceItemInfo"), adNS("licenseToken")))

    rights_xml_str = buildRights(license_token_node)

    if (rights_xml_str is None):
        print("Building rights.xml failed!")
        return False

    book_name = None

    try: 
        metadata_node = adobe_fulfill_response.find("./%s/%s/%s" % (adNS("fulfillmentResult"), adNS("resourceItemInfo"), adNS("metadata")))
        book_name = metadata_node.find("./%s" % (adDC("title"))).text
        # removing illegal characters for filename
        book_name = book_name.replace(":","-")
        book_name = ''.join([c for c in book_name if c not in '\/*?"<>|'])
    except: 
        book_name = "Book"
    

    # Download eBook: 

    print(download_url)
    filename_tmp = book_name + ".tmp"

    dl_start_time = int(time.time() * 1000)
    ret = sendHTTPRequest_DL2FILE(download_url, filename_tmp)
    dl_end_time = int(time.time() * 1000)
    print()
    print("Download took %d milliseconds" % (dl_end_time - dl_start_time))

    if (ret != 200):
        print("Download failed with error %d" % (ret))
        return False

    with open(filename_tmp, "rb") as f:
        book_content = f.read(10)

    filetype = ".bin"
    
    if (book_content.startswith(b"PK")):
        print("That's a ZIP file -> EPUB")
        filetype = ".epub"
    elif (book_content.startswith(b"%PDF")):
        print("That's a PDF file")
        filetype = ".pdf"

    filename = book_name + filetype
    shutil.move(filename_tmp, filename)

    if filetype == ".epub":
        # Store EPUB rights / encryption stuff
        zf = zipfile.ZipFile(filename, "a")
        zf.writestr("META-INF/rights.xml", rights_xml_str)
        zf.close()
        print()
        print("File successfully fulfilled")
        return filename
    
    elif filetype == ".pdf":
        print("Successfully downloaded PDF, patching encryption ...")

        adobe_fulfill_response = etree.fromstring(rights_xml_str)
        NSMAP = { "adept" : "http://ns.adobe.com/adept" }
        adNS = lambda tag: '{%s}%s' % ('http://ns.adobe.com/adept', tag)
        resource = adobe_fulfill_response.find("./%s/%s" % (adNS("licenseToken"), adNS("resource"))).text
        
        os.rename(filename, "tmp_" + filename)
        ret = patch_drm_into_pdf("tmp_" + filename, rights_xml_str, filename, resource)
        os.remove("tmp_" + filename)
        if (ret):
            print()
            print("File successfully fulfilled")
            return filename
        else: 
            print("Errors occurred while patching " + filename)
            return False

    else: 
        print("Error: Weird filetype")
        return False


def downloadFile(file="URLLink.acsm"):

    print("Fulfilling book '" + file + "' ...")
    success, replyData = fulfill(file)
    if (success is False):
        print()
        print("Hey, that didn't work!")
        print(replyData)
    else: 
        print()
        print("Downloading book '" + file + "' with download link")
        success = download(replyData)
        if (success is False):
            print("That didn't work!")
            return None
        else:
            return success
