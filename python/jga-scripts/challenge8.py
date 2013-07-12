#!/usr/bin/env python
# Copyright 2013 Javier Ayala
# All Rights Reserved.
#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.
import os
import sys
import argparse
import getpass
import pyrax
import pyrax.exceptions as exc
# Pre-defined Variables
defConfigFile = os.path.expanduser('~') + '/.rackspace_cloud_credentials'
progName = 'RAX Challenge-inator 8000'
metaWeb = 'X-Container-Meta-Web-Index'
indexFile = 'index.html'
indexHtml = """\
<html>
    <head>
        <title>
            Cloud Files Page
        </title>
        <style type="text/css" media="screen">
body{padding:20px;text-align:center;background:#fff}
.msgbox{position:absolute;width:400px;height:400px;left:50%;top:50%;margin-left:-200px;margin-top:-200px;border-radius:0 79px 0 79px;-moz-border-radius:0 79px;-webkit-border-radius:0 79px 0 79px;border:8px solid #000;background-color:#cf2d36}
.innerbox{position:relative;margin-top:-75px;margin-left:-400px;top:50%;left:50%;overflow:hidden}
        </style>
    </head>
    <body>
        <div class='msgbox'>
            <div class='innerbox'>
                <h1>
                    This is a CF hosted site
                </h1>
                <p>
                    By Javier Ayala
                </p>
            </div>
        </div>
    </body>
</html>
"""

# Argument Parsing
raxParse = argparse.ArgumentParser(description='Challenge 8 of the API \
    Challenge: Write a script that will create a static webpage served out of \
    Cloud Files. The script must create a new container, cdn enable it, \
    enable it to serve an index file, create an index file object, upload \
    the object to the container, and create a CNAME record pointing to the \
    CDN URL of the container.')
raxParse.add_argument('-c', '--config', dest='configFile', help="Location of \
    the config file", default=defConfigFile)
raxParse.add_argument('-co', '--container', dest='contName', help="Name \
    of the new CF Container to hold the uploaded files", required=True)
raxParse.add_argument('-dns', dest='dnsDomain', help="DNS Domain to use")
raxParse.add_argument('-cn', dest='cname', help="CNAME to use")
raxParse.add_argument('-dc', choices=['DFW', 'ORD', 'LON'])
raxParse.add_argument('-v', dest='verbose', action='store_true', help="Show \
    debug info, such as HTTP responses")
raxParse.add_argument('-V', '--version', action='version', version='%(prog)s \
    0.1 by Javier Ayala')
raxArgs = raxParse.parse_args()


class bcolors():
    """Provides color definitions for text output"""
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'

    def disable(self):
        self.HEADER = ''
        self.OKBLUE = ''
        self.OKGREEN = ''
        self.WARNING = ''
        self.FAIL = ''
        self.ENDC = ''


class raxLogin(object):
    """Provides functionality for logging into the API"""
    def __init__(self, configFile):
        super(raxLogin, self).__init__()
        self.configFile = configFile

    def authenticate(self):
        """Authenticate using credentials in config file, or fall back to
            prompting the user for the credentials."""
        try:
            pyrax.set_credential_file(self.configFile)
            print bcolors.OKBLUE + "Authentication SUCCEEDED!" + bcolors.ENDC
        except exc.AuthenticationFailed:
            print ("%(blue)sCan't seem to find the right key on my keyring... "
                   "%(endc)s") % {"blue": bcolors.OKBLUE, "endc": bcolors.ENDC}
            print bcolors.FAIL + "Authentication Failed using the " + \
                "credentials in " + str(self.configFile) + bcolors.ENDC
            self.raxLoginPrompt()
        except exc.FileNotFound:
            print ("%(blue)sI seem to have misplaced my keyring... Awkward..."
                   "%(endc)s") % {"blue": bcolors.OKBLUE, "endc": bcolors.ENDC}
            print bcolors.WARNING + "No config file found: " + str(
                self.configFile) + bcolors.ENDC
            self.raxLoginPrompt()

    def raxLoginPrompt(self):
        """Prompt the user for a login name and API Key to use for logging
            into the API."""
        print ("%(blue)sI really hate to ask...but...can I borrow your key?"
               "%(endc)s") % {"blue": bcolors.OKBLUE, "endc": bcolors.ENDC}
        self.raxUser = raw_input('Username: ')
        self.raxAPIKey = getpass.getpass('API Key: ')
        try:
            pyrax.set_credentials(self.raxUser, self.raxAPIKey)
            print bcolors.OKBLUE + "Authentication SUCCEEDED!" + bcolors.ENDC
        except exc.AuthenticationFailed:
            print bcolors.FAIL + "Authentication Failed using the " + \
                "Username and API Key provided!" + bcolors.ENDC
            sys.exit(1)


def printContAttr(cont):
    """Print out the attributes of the specified container."""
    print bcolors.HEADER
    print "CDN Status"
    print "=========="
    print bcolors.OKBLUE
    print "Container: ", cont.name
    print "cdn_enabled: ", cont.cdn_ttl
    print "cdn_log_retention: ", cont.cdn_log_retention
    print "cdn_uri: ", cont.cdn_uri
    print "cdn_ssl_uri: ", cont.cdn_ssl_uri
    print "cdn_streaming_uri: ", cont.cdn_streaming_uri
    print bcolors.ENDC


if raxArgs.verbose:
    pyrax.set_http_debug(True)
if raxArgs.dc:
    dc = raxArgs.dc
else:
    dc = pyrax.safe_region()
if raxArgs.contName:
    contName = raxArgs.contName
else:
    contName = raw_input("Enter the name of the new container: ")
if raxArgs.dnsDomain:
    dnsDomain = raxArgs.dnsDomain
else:
    dnsDomain = raw_input("Enter the domain name (not CNAME): ")
if raxArgs.cname:
    cname = raxArgs.cname
else:
    cname = raw_input("Enter the FQDN name of the new CNAME: ")

print "\n%(header)sWelcome to the %(progname)s! %(endc)s" % {
    "header": bcolors.HEADER, "progname": progName, "endc": bcolors.ENDC}

try:
    myLogin = raxLogin(raxArgs.configFile)
    myLogin.authenticate()
except:
    print bcolors.FAIL + "Couldn't login" + bcolors.ENDC
    sys.exit(2)

cf = pyrax.connect_to_cloudfiles(region=dc)

print "\n%(header)sCreating Cloud Files Container... %(endc)s" % {
    "header": bcolors.HEADER, "endc": bcolors.ENDC}
try:
    cont = cf.create_container(contName)
    print("%(hdr)sSuccessfully created %(contname)s"
          "%(endc)s") % {"hdr": bcolors.HEADER, "contname": cont.name,
                         "endc": bcolors.ENDC}
except Exception as e:
    print("%(fail)sCan't create container: "
          "%(e)s%(endc)s") % {"fail": bcolors.FAIL,
                              "e": e, "endc": bcolors.ENDC}
    sys.exit(2)

print "\n%(header)sCreating index.html file... %(endc)s" % {
    "header": bcolors.HEADER, "endc": bcolors.ENDC}
try:
    indexObj = cf.store_object(cont, 'index.html', indexHtml)
except:
    print "\n%(fail)sERROR Creating index.html file... %(endc)s" % {
        "fail": bcolors.FAIL, "endc": bcolors.ENDC}
    sys.exit(3)

print "\n%(header)sEnabling %(mw)s for Cloud Files Container... %(endc)s" % {
    "header": bcolors.HEADER, "mw": metaWeb, "endc": bcolors.ENDC}
metaEntry = {metaWeb: indexFile}
try:
    cf.set_container_metadata(cont, metaEntry)
except:
    print "\n%(fail)sERROR Setting Meta Info... %(endc)s" % {
        "fail": bcolors.FAIL, "endc": bcolors.ENDC}
    sys.exit(3)

print "\n%(header)sEnabling CDN for Cloud Files Container... %(endc)s" % {
    "header": bcolors.HEADER, "endc": bcolors.ENDC}
cont.make_public(ttl=1200)
cont = cf.get_container(contName)
printContAttr(cont)

print "\n%(header)sCreating CNAME for %(cname)s --> %(cdn)s. %(endc)s" % {
    "header": bcolors.HEADER, "cname": cname,
    "cdn": cont.cdn_uri, "endc": bcolors.ENDC}
dns = pyrax.cloud_dns
try:
    dom = dns.find(name=dnsDomain)
except:
    print "\n%(fail)sERROR Can't find domain %(dns)s... %(endc)s" % {
        "fail": bcolors.FAIL, "dns": dnsDomain, "endc": bcolors.ENDC}
cname_rec = {"type": "CNAME",
             "name": cname,
             "data": cont.cdn_uri}
print dom.add_records(cname_rec)

print "\n%(okb)sComplete!%(endc)s" % {
    "okb": bcolors.OKBLUE, "endc": bcolors.ENDC}
