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
import time
import socket
import pyrax
import pyrax.exceptions as exc
# Pre-defined Variables
defConfigFile = os.path.expanduser('~') + '/.rackspace_cloud_credentials'
progName = 'RAX Challenge-inator 9000'

# Argument Parsing
raxParse = argparse.ArgumentParser(description="Write an application that \
    when passed the arguments FQDN, image, and flavor it creates a server of \
    the specified image and flavor with the same name as the fqdn, and \
    creates a DNS entry for the fqdn pointing to the server's public IP")
raxParse.add_argument('-c', '--config', dest='configFile', help="Location of \
    the config file", default=defConfigFile)
raxParse.add_argument('FQDN', help="FQDN of the server to be created.")
raxParse.add_argument('domain', help="Domain name of the server.")
raxParse.add_argument('imgID', help='ID of the Image to use when building \
    the server.')
raxParse.add_argument('flvrID', help='ID of the Flavor to use when building \
    the server.')
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


def raxCreateServer(raxCldSvr, svrBaseName, imgIDToUse,
                    flvrIDToUse):
    completed = []  # Array to hold the servers that complete creation
    print "\n%(header)sCreating New Server '%(fqdn)s'... %(endc)s" % {
        "header": bcolors.HEADER, "fqdn": raxArgs.FQDN, "endc": bcolors.ENDC}
    try:
        newSvr = raxCldSvr.servers.create(raxArgs.FQDN, imgIDToUse,
                                          flvrIDToUse)
    except Exception as e:
        print("%(fail)sCan't create server: "
              "%(e)s%(endc)s") % {"fail": bcolors.FAIL,
                                  "e": e, "endc": bcolors.ENDC}
        sys.exit(2)
    sys.stdout.write("Waiting for builds to complete")
    sys.stdout.flush()
    while len(completed) < 1:
        sys.stdout.write('.')
        sys.stdout.flush()
        time.sleep(30)
        if newSvr.name in completed:
            continue
        newSvr.get()
        if newSvr.status in ['ACTIVE', 'ERROR', 'UNKNOWN']:
            sys.stdout.write("\n")
            print '======================================='
            print 'Name: %s' % newSvr.name
            if (newSvr.status == 'ERROR'):
                print('Status: %(fail)s %(stat)s'
                      ' %(endc)s') % {"fail": bcolors.FAIL,
                                      "stat": newSvr.status,
                                      "endc": bcolors.ENDC}
            else:
                print bcolors.OKBLUE
                print 'Status: %s' % newSvr.status
                print 'ID: %s' % newSvr.id
                print 'Networks: %s' % newSvr.networks
                print 'Password: %s' % newSvr.adminPass
                print bcolors.ENDC
                ipv4Check = False
                fqdnInfo = None
                for ipToChk in newSvr.networks['public']:
                    ipv4Check = isIPv4(str(ipToChk))
                    if ipv4Check is True:
                        fqdnInfo = ipToChk
                        break
                    pass
            completed.append(newSvr.name)
    return fqdnInfo


def isIPv4(address):
    print "Testing: %s" % address
    try:
        socket.inet_aton(address)
        ip = True
    except socket.error:
        ip = False

    return ip


def raxAddDNSA(svrIP):
    try:
        domid = raxDns.find(name=raxArgs.domain)
    except exc.NotFound:
        print bcolors.FAIL + raxArgs.domain + 'NOT FOUND!!!' + \
            bcolors.ENDC
        sys.exit()

    aRec = [{
        "type": "A",
        "name": raxArgs.FQDN,
        "data": svrIP,
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
    return 0


if raxArgs.verbose:
    pyrax.set_http_debug(True)
if raxArgs.dc:
    dc = raxArgs.dc
else:
    dc = pyrax.safe_region()
numSections = len(raxArgs.domain.split('.'))
if (raxArgs.domain.split('.')[(numSections * -1):]) != (
        raxArgs.FQDN.split('.')[(numSections * -1):]):
    print("%(fqdn)s is not in %(domain)s") % {"fqdn": raxArgs.FQDN,
                                              "domain": raxArgs.domain}
    sys.exit(1)
print "\n%(header)sWelcome to the %(progname)s! %(endc)s" % {
    "header": bcolors.HEADER, "progname": progName, "endc": bcolors.ENDC}

try:
    myLogin = raxLogin(raxArgs.configFile)
    myLogin.authenticate()
except:
    print bcolors.FAIL + "Couldn't login" + bcolors.ENDC
    sys.exit(2)

raxCldSvr = pyrax.connect_to_cloudservers(region=dc)
raxDns = pyrax.cloud_dns

try:
    builtSvr = raxCreateServer(raxCldSvr, raxArgs.FQDN, raxArgs.imgID,
                               raxArgs.flvrID)
except Exception as e:
    print("%(fail)sCan't create server: "
          "%(e)s%(endc)s") % {"fail": bcolors.FAIL,
                              "e": e, "endc": bcolors.ENDC}
    sys.exit(2)

print "\n%(header)sCreating DNS Entry... %(endc)s" % {
    "header": bcolors.HEADER, "endc": bcolors.ENDC}
try:
    dnsRec = raxAddDNSA(builtSvr)
except Exception as e:
    print "\n%(fail)sERROR Creating DNS Entry: %(e)s %(endc)s" % {
        "fail": bcolors.FAIL, "e": e, "endc": bcolors.ENDC}
    sys.exit(3)

print "\n%(okb)sComplete!%(endc)s" % {
    "okb": bcolors.OKBLUE, "endc": bcolors.ENDC}
