#!/usr/bin/env python

import os
import urllib
import urllib2
import hashlib
import tarfile


URL_LASTVER='http://192.168.133.129/deploy/lastver'
URL_LIVEVER='http://192.168.133.129/deploy/livever'
URL_PKG='http://192.168.133.129/deploy/packages/'
DOWNLOAD_DIR='/var/www/download/'
DEPLOY_DIR='/var/www/deploy/'
APP_NAME='wordpress'
DOC_ROOT='/var/www/html/current'


def init():
    if not os.path.exists(DOWNLOAD_DIR):
        os.makedirs(DOWNLOAD_DIR)
    if not os.path.exists(DEPLOY_DIR):
        os.makedirs(DEPLOY_DIR)

def getURL(url):
    return urllib2.urlopen(url).read().strip()

def checkversion():
    lastver=getURL(URL_LASTVER)
    url_pkg_path=URL_PKG + "%s-%s.tar.gz" %(APP_NAME,lastver)
    pkg_path=os.path.join(DOWNLOAD_DIR,"%s-%s.tar.gz" %(APP_NAME,lastver))
    if not os.path.exists(pkg_path):
        if not download(pkg_path,url_pkg_path):
            return False
    extract_dir=os.path.join(DEPLOY_DIR,"%s-%s" %(APP_NAME,lastver))
    if not os.path.exists(extract_dir):
        pkg_deploy(pkg_path,DEPLOY_DIR)
        

def download(fn,url_pkg_path):
    url_pkg_path_md5=url_pkg_path+".md5"
    md5=getURL(url_pkg_path_md5)
    req=urllib2.urlopen(url_pkg_path)
    n=1
    while True:
        data=req.read(4096)
        if not data:
            break
        if n==1:
            with open(fn,'wb') as fd:
                fd.write(data)
            n+=1
        elif n>1:
            with open(fn,'a') as fd:
                fd.write(data)
            n+=1
    if checkFileSum(fn,md5):
        return True
    return False   

def checkFileSum(fn,md5):
    with open(fn) as fd:
        m=hashlib.md5(fd.read()).hexdigest()
        if m==md5:
            return True
        return False

def pkg_deploy(fn,d):
    tar=tarfile.open(fn)
    tar.extractall(path=d)

def checkliver():
    livever=getURL(URL_LIVEVER)
    pkg_path=os.path.join(DEPLOY_DIR,"%s-%s" %(APP_NAME,livever))
    if os.path.exists(pkg_path):
        if os.path.exists(DOC_ROOT):
            target=os.readlink(DOC_ROOT)
            if target != pkg_path:
                os.unlink(DOC_ROOT)
                os.symlink(pkg_path,DOC_ROOT)
        else:
            os.symlink(pkg_path,DOC_ROOT)

if __name__=='__main__':
    init()
    checkversion()
    checkliver()

