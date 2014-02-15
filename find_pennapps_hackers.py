#!/usr/bin/env python3

import http.client
import re
import sys
import time

def main():
    # find twitter names and usernames
    twitterUsers = set(findbetween(gethttp("twitter.com", "/search?q=%23PennApps", True), "data-screen-name=\"", "\""))
    print(twitterUsers)
    # find real names and website domains
    names = set()
    domains = set()
    githubUsers = set()
    for twitterUser in twitterUsers:
        sys.stdout.write(".")
        sys.stdout.flush()
        html = gethttp("twitter.com", "/" + twitterUser, True)
        nameFields = findbetween(html, "<span class=\"profile-field\">", "</span>")
        if len(nameFields) > 0:
            names.add(nameFields[0])
        for url in findurls(html):
            url2 = url[:len(url) - 1] if url.endswith("/") else url
            if url2.find("twitter.com") == -1 and url2.find("twimg.com") == -1 and (url2.endswith(".com") or url2.endswith(".org") or url.endswith(".net")):
                domains.add(url2)
            elif url.find("github.com") != -1:
                githubUsers.add(url)
    print()
    print(names)
    print(domains)
    # find github accounts
    """for name in names:
        html = ""
        try:
            html = gethttp("duckduckgo.com", "/html/?q=site:github.com " + name, True)
        except:
            print("error searching " + name)
        for url in findlinks(html):
            if url.find("https://github.com/") != -1 and url.count("/") == 3:
                githubUsers.add(url)
        time.sleep(2)"""
    for name in names:
        for url in findlinks(gethttp("www.google.com", "/search?q=site:github.com+" + name.replace(" ", "+"), True)):
            if url.startswith("/url?q=https://github.com/") and url.count("/") == 4:
                 githubUsers.add(findbetween(url, "/url?q=https://github.com/", "&")[0].split("%")[0])
        sys.stdout.write(".")
        sys.stdout.flush()
    print()
    for domain in domains:
        html = gethttpsmart(domain)
        for url in findlinks(html):
            if (url.find("github.com/") != -1):
                githubUsers.add(url.split("github.com/")[1].split("/")[0])
        sys.stdout.write(".")
        sys.stdout.flush()
    print()
    print(githubUsers)

def gethttpsmart(url):
    minusProtocol = url[url.find("//") + 2 : ]
    if minusProtocol.find("/") == -1:
        minusProtocol += "/"
    return gethttp(minusProtocol.split("/")[0], "/" + minusProtocol.split("/")[1], url.startswith("https"))

def gethttp(domain, url, https):
    #print(domain, url, https)
    conn = http.client.HTTPSConnection(domain) if https else http.client.HTTPConnection(domain)
    conn.request("GET", url)
    r1 = conn.getresponse()
    if r1.status == 301 or r1.status == 302:
        return gethttpsmart(r1.getheader("Location")) # got a "moved permanently" error
    elif r1.status != 200:
        print("non-normal status connecting to", domain, url, r1.status, r1.reason)
    r1str = str(r1.read())
    conn.close()
    return r1str

def findbetween(string, before, after):
    ret = []
    for match in re.finditer(re.escape(before), string):
        ret.append(string[match.start() + len(before) : string.find(after, match.start() + len(before))])
    return ret

def findurls(string): # thanks to https://stackoverflow.com/questions/6883049/regex-to-find-urls-in-string-in-python
    return re.findall('http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', string)

def findlinks(string):
    return re.findall('href="?\'?([^"\'>]*)', string)

if __name__ == "__main__":
    main()
