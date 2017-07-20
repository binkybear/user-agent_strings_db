import os
import re
import json
import fileinput
import hashlib
import urllib2
import xml.etree.cElementTree as ET # Parse XML useragent
from bs4 import BeautifulSoup # To parse webpages
from user_agents import parse # Parse user agent strings
import sqlite3

def sqlite_ua_createdb(sqlfile):

    try:
        table_name = 'user_agents'   # name of the table to be created

        first_column = "useragent_string"

        columns = [ "browser_family", "browser_version", "operating_system", \
                   "operating_system_version", "device_family", "is_mobile", "is_tablet", "is_touch_capable", \
                   "is_pc", "is_bot", "overview"]

        field_type = 'TEXT'  # column data type

        # Connect to database useragents.sqlite
        conn = sqlite3.connect(sqlfile)
        c = conn.cursor()

        # Create table with id_field column

        c.execute('CREATE TABLE {tn} ({fn} {ft} PRIMARY KEY)'\
            .format(tn=table_name, fn=first_column, ft=field_type))

        # Add columns to the table from columns list
        for x in columns:
            c.execute("ALTER TABLE {tn} ADD COLUMN '{cn}'".format(tn=table_name, cn=x))
        print("Created emtpy sqlite file %s with columns" % sqlfile)

        # Close database
        conn.close()

    except:
        pass

class UA(object):
    def __init__(self, useragent):
        self.table_name = 'user_agents'   # name of the sql table to be created

        self.columns = [ "useragent_string", "browser_family", "browser_version", "operating_system", \
                   "operating_system_version", "device_family", "is_mobile", "is_tablet", "is_touch_capable", \
                   "is_pc", "is_bot", "overview" ]

        self.list = []

        user_agent = parse(useragent)

        self.useragent_string = str(useragent)

        if self.useragent_string.startswith('"') and self.useragent_string.endswith('"'): # Check UA for quotes
            self.useragent_string = self.useragent_string[1:-1]

        if self.useragent_string.startswith(' '): # Check UA for spaces
            self.useragent_string = self.useragent_string[1:]

        self.browser_family = str(user_agent.browser.family)
        self.browser_version = str(user_agent.browser.version_string)
        self.os = str(user_agent.os.family)
        self.os_version = str(user_agent.os.version_string)
        self.device_family = str(user_agent.device.family)
        self.is_mobile = str(user_agent.is_mobile)
        self.is_tablet = str(user_agent.is_tablet)
        self.is_touch_capable = str(user_agent.is_touch_capable)
        self.is_pc = str(user_agent.is_pc)
        self.is_bot = str(user_agent.is_bot)
        self.overview = str(user_agent)

        self.list = [ self.useragent_string, self.browser_family, self.browser_version, self.os, \
                     self.os_version, self.device_family, self.is_mobile, self.is_tablet, \
                     self.is_touch_capable, self.is_pc, self.is_bot, self.overview ]

        self.sqlite_ua_populatedb()

    def sqlite_ua_populatedb(self):
        try:

            sqlfile = "useragents.sqlite"

            columns = str(self.columns).strip('[]')
            list = str(self.list).strip('[]').encode('utf-8')

            # Connect to database useragents.sqlite
            conn = sqlite3.connect(sqlfile)

            #print("Inserting", self.useragent_string, "into table", self.table_name) # For debugging

            insert = "INSERT INTO " + self.table_name + " ( " + str(columns) + " ) VALUES ( " + str(list) + " )"

            conn.execute(str(insert));

            conn.commit()

            # Close database
            conn.close()

        except sqlite3.IntegrityError:
            pass # Prevent the program from stopping when

def web_soup(url, filename):
    try:
        print("[+] Connecting to %s" % url)
        content = urllib2.urlopen(url).read()

        print("[+] Creating file %s" % filename)
        f = open(filename, 'w')

        soup = BeautifulSoup(content)

        li = soup.find_all("li")

        print("[+] Scraping data from %s" % url)
        for urlstring in li:
            uagent = urlstring.get_text()
            uagent = re.sub(r'^"|"$', '', uagent) # Remove double quotes
            object = UA(uagent)
            f.write(json.dumps(object.__dict__, indent=1))
        f.close()

    #handle errors
    except urllib2.HTTPError, e:
        print('HTTP Error:',e.code , url)
    except urllib2.URLError, e:
        print('URL Error:',e.reason , url)
    except IOError, e:
        print(e.reason)

def checkMD5(url, max_file_size=100*1024*1024):
    # MD5 remote check from: https://gist.github.com/brianewing/994303
    try:
        print("[+] Checking to see if you have the latest xml file")
        remote = urllib2.urlopen(url)
        hash = hashlib.md5()

        total_read = 0
        while True:
            data = remote.read(4096)
            total_read += 4096

            if not data or total_read > max_file_size:
                break

            hash.update(data)

        return hash.hexdigest()

    #handle errors
    except urllib2.HTTPError, e:
        print('HTTP Error:',e.code , url)
    except urllib2.URLError, e:
        print('URL Error:',e.reason , url)

def downloadUAXML(url):
    try:
        # Status bar not necessary but taken from:
        # http://stackoverflow.com/questions/22676/how-do-i-download-a-file-over-http-using-python
        file_name = url.split('/')[-1]
        u = urllib2.urlopen(url)
        f = open(file_name, 'wb')
        meta = u.info()
        file_size = int(meta.getheaders("Content-Length")[0])
        print("[+] Downloading: %s Bytes: %s") % (file_name, file_size)

        file_size_dl = 0
        block_sz = 8192
        while True:
            buffer = u.read(block_sz)
            if not buffer:
                break

            file_size_dl += len(buffer)
            f.write(buffer)
            status = r"%10d  [%3.2f%%]" % (file_size_dl, file_size_dl * 100. / file_size)
            status = status + chr(8)*(len(status)+1)
            print status,

        f.close()

    #handle errors
    except urllib2.HTTPError, e:
        print('HTTP Error:',e.code , url)
    except urllib2.URLError, e:
        print('URL Error:',e.reason , url)

def techpatterns(url, techpatternsxml, techpatternsjson):

    check_latest_uaxml(url, techpatternsxml)

    f = open(techpatternsjson, 'w')

    tree = ET.ElementTree(file=techpatternsxml)
    root = tree.getroot() # Define root as the "root" of the xml tree

    print("[+] Parsing latest techpatterns xml file")
    # Search the XML file for useragent strings then pass as object > create json
    for browsertype in root.findall('folder'):
        for type in browsertype.findall('folder'):
            for useragent in type.findall('useragent'):
                uastrings = useragent.get('useragent') # Actual user agent string
                object = UA(uastrings)
                f.write(json.dumps(object.__dict__, indent=1))
        for newbrowser in browsertype.findall('useragent'):
            uastrings =  newbrowser.get('useragent') # This is the new user agent string
            object = UA(uastrings)
            f.write(json.dumps(object.__dict__, indent=1))

    f.close()

def check_latest_uaxml(url, techpatternsxml):

    if os.path.exists(techpatternsxml):
        # Check local uaxml md5
        md5 = hashlib.md5()
        f = open(techpatternsxml)
        for line in f:
            md5.update(line)
        f.close()
        localmd5 = md5.hexdigest()

        # Check remote uaxml md5
        remotemd5 = checkMD5(url)
        print('[+] Local MD5:  %s\n[+] Remote MD5: %s' % (localmd5, remotemd5)) # Debugging

        # Compare
        if localmd5 == remotemd5:
            print('[+] You have the latest useragent xml file')
    else:
        print('[-] Missing useragentswitcher.xml')
        downloadUAXML(url)

def dedupe_json(techpatterns_json, useragentstring_com):
    # Dedupe JSON files and combine into one
    if os.path.exists(techpatterns_json) and os.path.exists(useragentstring_com):

        filenames = [techpatterns_json, useragentstring_com]

        with open("combined.json", 'w') as fout:
            for line in fileinput.input(filenames):
                fout.write(line)

def search_json():
    if os.path.exists("combined.json"):
        f = open("combined.json", 'r')

if __name__ == '__main__':

    # Techpatterns useragentswitcher xml file
    techpatternsurl = 'http://techpatterns.com/downloads/firefox/useragentswitcher.xml'
    techpatternsxml = 'useragentswitcher.xml'
    techpatternsjson = 'techpatterns.json'

    # Useragentstring.com scrape
    useragentstring_url = "http://www.useragentstring.com/pages/useragentstring.php?name=All"
    useragentstring_com_json = "useragentstring_com.json"

    # Check if we have a DB file, if not create one
    sqlite_file = "useragents.sqlite"

    if not os.path.exists(sqlite_file):
        sqlite_ua_createdb(sqlite_file)

    # Download latest useragents
    web_soup(useragentstring_url, useragentstring_com_json) # Download latest from useragentstring.com
    techpatterns(techpatternsurl, techpatternsxml, techpatternsjson) # Download latest from techpatterns

    # Dedupe json
    dedupe_json(techpatternsjson, useragentstring_com_json) # Dedupe both json files
