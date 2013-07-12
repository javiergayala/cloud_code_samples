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
import re
import argparse
import socket
import getpass
import pyrax
import pyrax.exceptions as exc

# Pre-defined Variables
defConfigFile = os.path.expanduser('~') + '/.rackspace_cloud_credentials'
progName = 'RAX Challenge-inator 4000'

# Argument Parsing
raxParse = argparse.ArgumentParser(description='Challenge 4 of the \
     API Challenge: Write a script that uses Cloud DNS to create a new A \
     record when passed a FQDN and IP address as arguments. ')
raxParse.add_argument('-c', '--config', dest='configFile',
                      help="Location of the config file",
                      default=defConfigFile)
raxParse.add_argument('-ld', '--list-domains', action='store_true',
                      help="List Domain Names in DNS")
raxParse.add_argument('aFQDN', help="FQDN for new A record")
raxParse.add_argument('aIP', help="IP for new A record")
raxParse.add_argument('domainName', help='Domain')
raxParse.add_argument('-d', dest='debug', action='store_true',
                      help="Show debug info, such as HTTP responses")
raxParse.add_argument('-V', '--version', action='version',
                      version='%(prog)s 0.1 by Javier Ayala')
raxArgs = raxParse.parse_args()

# See if there is a pyrax.cfg file
configFileTest = os.path.isfile(raxArgs.configFile)


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


def isFQDN(hostname):
    if len(hostname) > 255:
        return False
    if hostname[-1:] == ".":
        hostname = hostname[:-1]  # strip 1 dot from the right, if present
    allowed = re.compile("(?!-)[A-Z\d-]{1,63}(?<!-)$", re.IGNORECASE)
    return all(allowed.match(x) for x in hostname.split("."))


def isIP(ipAddr):
    try:
        socket.inet_aton(ipAddr)
        validIP = True
    except socket.error:
        validIP = False

    return validIP


def raxListDomains():
    for domain in raxDns.get_domain_iterator():
        print '%(name)s' % {"name": domain.name}
    dom = raw_input('Choose a domain to view records, or \'q\' to quit: ')
    if (dom == 'q'):
        sys.exit()
    try:
        domId = raxDns.find(name=dom)
    except exc.NotFound:
        print "%(fail)s%(dom)s not found %(endc)s" % {
            "fail": bcolors.FAIL, "dom": dom, "endc": bcolors.ENDC}
        sys.exit(1)
    recs = raxDns.list_records(domId)
    for rec in recs:
        print rec


def raxAddDNSA():
    aRecName = raxArgs.aFQDN
    aIPAddr = raxArgs.aIP

    try:
        domid = raxDns.find(name=raxArgs.domainName)
    except exc.NotFound:
        print bcolors.FAIL + raxArgs.domainName + 'NOT FOUND!!!' + \
            bcolors.ENDC
        sys.exit()

    if (isIP(aIPAddr) is True) and (isFQDN(aRecName) is True):
        print "Creating DNS Record"
        aRec = [{
            "type": "A",
            "name": aRecName,
            "data": aIPAddr,
        }]
        try:
            newRecord = domid.add_records(aRec)
        except exc.OverLimit:
            print bcolors.FAIL
            print "API Limit Reached!!"
            print bcolors.ENDC
            sys.exit(2)
        except exc.DomainRecordAdditionFailed as e:
            print bcolors.FAIL
            print "Domain Record Addition Failed!"
            print str(e)
            print bcolors.ENDC
            sys.exit(3)
        print bcolors.HEADER
        print "DNS Record Added"
        print "================"
        print bcolors.OKBLUE
        for rec in newRecord:
            print('Record Name: %s') % rec.name
            print('         IP: %s') % rec.data
            print('        TTL: %s') % rec.ttl
            print('  Domain ID: %s') % rec.domain_id
            print('  Record ID: %s') % rec.id
            print('Record Type: %s') % rec.type

        print bcolors.ENDC
    else:
        print bcolors.FAIL + \
            "There was a problem with your IP or FQDN! Check them!" + \
            bcolors.ENDC
        print "IP: %s" % aIPAddr
        print "FQDN: %s" % aRecName


"""This is where the magic happens!"""

print "\n%(header)sWelcome to the %(progname)s! %(endc)s" % {
    "header": bcolors.HEADER, "progname": progName, "endc": bcolors.ENDC
}
if (len(sys.argv) == 1):
    print ("%(warning)sThe %(progname)s is happiest when you correctly "
           "tell it what to do...%(endc)s\n") % {"warning": bcolors.WARNING,
                                                 "progname": progName,
                                                 "endc": bcolors.ENDC}
    raxParse.print_usage()
    sys.exit()

if (len(sys.argv) == 1):
    raxParse.print_usage()
    sys.exit()

print ("%(blue)sWhipping out our janitor's keyring to see if we have "
       "the right key to open the door...%(endc)s") % {"blue": bcolors.OKBLUE,
                                                       "endc": bcolors.ENDC}
try:
    myLogin = raxLogin(raxArgs.configFile)
    myLogin.authenticate()
    raxDns = pyrax.cloud_dns
except:
    print bcolors.FAIL + "Couldn't login" + bcolors.ENDC
    sys.exit()

if raxArgs.debug:
    pyrax.set_http_debug(True)
if raxArgs.list_domains:
    raxListDomains()
else:
    raxAddDNSA()
