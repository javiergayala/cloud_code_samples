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
import time
import argparse
import getpass
import pprint
import pyrax
import pyrax.exceptions as exc

# Pre-defined Variables
defConfigFile = os.path.expanduser('~') + '/.rackspace_cloud_credentials'
progName = 'RAX Challenge-inator 1000'

# Argument Parsing
raxParse = argparse.ArgumentParser(description='Challenge 1 of the \
    API Challenge: Write a script that builds three 512 MB Cloud Servers \
    that following a similar naming convention. (ie., web1, web2, web3) \
    and returns the IP and login credentials for each server. Use any image \
    you want.', epilog="You MUST select either '-ls' or '-cs'!")
raxParse.add_argument('-c', '--config', dest='configFile',
                      help="Location of the config file",
                      default=defConfigFile)
raxParse.add_argument('-ls', '--list-servers', action='store_true',
                      help="List Cloud Servers")
raxParse.add_argument('-cs', '--create-server', action='store_true',
                      help="Create Server")
raxParse.add_argument('-ns', '--number-of-servers', dest='numServers',
                      help="Number of servers")
raxParse.add_argument('-sn', '--server-name', dest='svrBaseName',
                      help="Base name of servers")
raxParse.add_argument('-img', '--image-ID', dest='imgIDToUse',
                      help="Image ID for building servers")
raxParse.add_argument('-flv', '--flavor-ID', dest='flvrIDToUse',
                      help="Flavor ID for building servers")
raxParse.add_argument('-i', '--interactive', action='store_true',
                      help="Interactively prompt for info")
raxParse.add_argument('-dc', choices=['DFW', 'ORD', 'LON'])
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


def raxListServers(dc):
    cs = pyrax.connect_to_cloudservers(region=dc)
    servers = cs.servers.list()
    ls_pp = pprint.PrettyPrinter(indent=4)
    print "%s: " % dc
    ls_pp.pprint(servers)


def raxCreateServer(dc, imgIDToUse, flvrIDToUse, svrBaseName, numServers):
    raxCldSvr = pyrax.connect_to_cloudservers(region=dc)
    serverImgs = raxCldSvr.images.list()
    svrsCreated = {}  # Dictionary to hold info on the servers that get created
    completed = []  # Array to hold the servers that complete creation
    if raxArgs.interactive:
        for img in sorted(serverImgs, key=lambda serverImgs: serverImgs.name):
            print img.name, " || ID:", img.id
        imgIDToUse = raw_input('ID of image to use: ')
        imgNameToUse = [img.name for img in serverImgs if img.id == imgIDToUse][0]
        #print str(imgToUse)
        serverFlvrs = raxCldSvr.flavors.list()
        for flvr in serverFlvrs:
            print "Name: " + flvr.name + " || ID:" + flvr.id
        flvrIDToUse = raw_input('ID of flavor to use: ')
        print 'Using ' + bcolors.OKBLUE + imgNameToUse + bcolors.ENDC
        try:
            numServers = int(raxArgs.numServers)
        except (ValueError, TypeError):
            numServers = 3
        if (raxArgs.svrBaseName is None):
            svrBaseName = raw_input('What is the server base name to use: ')
        else:
            svrBaseName = raxArgs.svrBaseName
    print 'Creating a new server from image' \
        ' ' + bcolors.OKBLUE + imgIDToUse + bcolors.ENDC + ' in ' + \
        bcolors.WARNING + dc + bcolors.ENDC + '.'
    print 'Creating ' + str(numServers) + ' servers.'
    print 'Server name will begin with ' + svrBaseName

    for i in xrange(0, numServers):
        svrName = '%s%s' % (svrBaseName, i)
        svrsCreated[svrName] = raxCldSvr.servers.create(svrName, imgIDToUse,
                                                        flvrIDToUse)
        print "Created server: %s" % svrName
    sys.stdout.write("Waiting for builds to complete")
    sys.stdout.flush()
    while len(completed) < numServers:
        sys.stdout.write('.')
        sys.stdout.flush()
        time.sleep(30)
        for name, server in svrsCreated.iteritems():
            if name in completed:
                continue
            server.get()
            if server.status in ['ACTIVE', 'ERROR', 'UNKNOWN']:
                sys.stdout.write("\n")
                print '======================================='
                print 'Name: %s' % server.name
                if (server.status == 'ERROR'):
                    print 'Status: %s %s %s' % bcolors.FAIL, server.status, \
                        bcolors.ENDC
                else:
                    print 'Status: %s' % server.status
                print 'ID: %s' % server.id
                print 'Networks: %s' % server.networks
                print 'Password: %s' % server.adminPass
                completed.append(name)

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

print ("%(blue)sWhipping out our janitor's keyring to see if we have "
       "the right key to open the door...%(endc)s") % {"blue": bcolors.OKBLUE,
                                                       "endc": bcolors.ENDC}
try:
    myLogin = raxLogin(raxArgs.configFile)
    myLogin.authenticate()
except:
    print bcolors.FAIL + "Couldn't login" + bcolors.ENDC
    sys.exit()


#  Setup our variables
if raxArgs.debug:
    pyrax.set_http_debug(True)
if raxArgs.dc:
    dc = raxArgs.dc
else:
    dc = pyrax.safe_region()
if raxArgs.imgIDToUse:
    imgIDToUse = raxArgs.imgIDToUse
else:
    imgIDToUse = 'acf05b3c-5403-4cf0-900c-9b12b0db0644'
if raxArgs.flvrIDToUse:
    flvrIDToUse = raxArgs.flvrIDToUse
else:
    flvrIDToUse = '2'
if raxArgs.svrBaseName:
    svrBaseName = raxArgs.svrBaseName
else:
    svrBaseName = 'web-'
if raxArgs.numServers:
    numServers = raxArgs.numServers
else:
    numServers = 3
if raxArgs.list_servers:
    raxListServers(dc)
if raxArgs.create_server:
    raxCreateServer(dc, imgIDToUse, flvrIDToUse, svrBaseName, numServers)
