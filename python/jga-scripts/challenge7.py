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
import time
import getpass
import pyrax
import pyrax.exceptions as exc

# Pre-defined Variables
defConfigFile = os.path.expanduser('~') + '/.rackspace_cloud_credentials'
progName = 'RAX Challenge-inator 7000'


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


def raxListImages(raxCldSvr):
    if (raxArgs.imgIDToUse is None):
        serverImgs = raxCldSvr.images.list()
        for img in sorted(serverImgs, key=lambda serverImgs: serverImgs.name):
            print img.name, " || ID:", img.id
        imgIDToUse = raw_input('ID of image to use: ')
    else:
        imgIDToUse = raxArgs.imgIDToUse
    if (raxArgs.flvrIDToUse is None):
        serverFlvrs = raxCldSvr.flavors.list()
        for flvr in serverFlvrs:
            print "Name: " + flvr.name + " || ID:" + flvr.id
        flvrIDToUse = raw_input('ID of flavor to use: ')
    else:
        flvrIDToUse = raxArgs.flvrIDToUse
    return imgIDToUse, flvrIDToUse


def raxCreateServer(raxCldSvr, numServers, svrBaseName, imgIDToUse,
                    flvrIDToUse):
    svrsCreated = {}  # Dictionary to hold info on the servers that get created
    nodeInfo = {}  # Dictionary to hold Private IPs of the nodes
    completed = []  # Array to hold the servers that complete creation
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
                    print('Status: %(fail)s %(stat)s'
                          ' %(endc)s') % {"fail": bcolors.FAIL,
                                          "stat": server.status,
                                          "endc": bcolors.ENDC}
                else:
                    print 'Status: %s' % server.status
                    print 'ID: %s' % server.id
                    print 'Networks: %s' % server.networks
                    nodeInfo[name] = \
                        str(server.networks['private'][0])
                    print 'Password: %s' % server.adminPass
                completed.append(name)
    return nodeInfo

# Argument Parsing
raxParse = argparse.ArgumentParser(description='Challenge 7 of the API \
    Challenge: Write a script that will create 2 Cloud Servers and add them \
    as nodes to a new Cloud Load Balancer.')
raxParse.add_argument('-c', '--config', dest='configFile', help="Location of \
    the config file", default=defConfigFile)
raxParse.add_argument('-sn', '--server-name', dest='svrBaseName', help="Base \
    name of the newly created servers")
raxParse.add_argument('-si', '--server-image', dest='imgIDToUse', help="ID \
    of the server image to use")
raxParse.add_argument('-sf', '--server-flavor', dest='flvrIDToUse', help="ID \
    of the server flavor to use")
raxParse.add_argument('-ln', '--lb-name', dest='lbName', help="Name \
    of the load-balacer to create")
raxParse.add_argument('-n', '--num-servers', dest='numServers', help="Number \
    of servers to create")
raxParse.add_argument('-dc', choices=['DFW', 'ORD', 'LON'])
raxParse.add_argument('-v', dest='verbose', action='store_true', help="Show \
    debug info, such as HTTP responses")
raxParse.add_argument('-V', '--version', action='version', version='%(prog)s \
    0.1 by Javier Ayala')
raxArgs = raxParse.parse_args()

if raxArgs.verbose:
    pyrax.set_http_debug(True)
if raxArgs.dc:
    dc = raxArgs.dc
else:
    dc = pyrax.safe_region()

print "\n%(header)sWelcome to the %(progname)s! %(endc)s" % {
    "header": bcolors.HEADER, "progname": progName, "endc": bcolors.ENDC}

try:
    myLogin = raxLogin(raxArgs.configFile)
    myLogin.authenticate()
except:
    print bcolors.FAIL + "Couldn't login" + bcolors.ENDC
    sys.exit(2)


raxCldSvr = pyrax.connect_to_cloudservers(region=dc)
raxCldLB = pyrax.connect_to_cloud_loadbalancers(region=dc)

if (raxArgs.svrBaseName is None):
    svrBaseName = raw_input('What is the server base name to use: ')
else:
    svrBaseName = raxArgs.svrBaseName
try:
    numServers = int(raxArgs.numServers)
except (ValueError, TypeError):
    numServers = int(raw_input('Number of servers to create: '))
if (raxArgs.lbName is None):
    lbName = raw_input('What is the name of the new load-balancer: ')
else:
    lbName = raxArgs.lbName

imgIDToUse, flvrIDToUse = raxListImages(raxCldSvr)

lbNodes = raxCreateServer(raxCldSvr, numServers, svrBaseName, imgIDToUse,
                          flvrIDToUse)

nodes = []
print "\n%(header)sCreating LB Nodes! %(endc)s" % {
    "header": bcolors.HEADER, "endc": bcolors.ENDC}
for name, privateIp in lbNodes.iteritems():
    nodes.append(raxCldLB.Node(address=privateIp, port=80,
                               condition='ENABLED'))
    print "%s node created..." % name
print "\n%(header)sCreating LB VIP! %(endc)s" % {
    "header": bcolors.HEADER, "endc": bcolors.ENDC}
vip = raxCldLB.VirtualIP(type='PUBLIC')

print "\n%(header)sPiecing it all together! %(endc)s" % {
    "header": bcolors.HEADER, "endc": bcolors.ENDC}
newLb = raxCldLB.create(lbName, port=80, protocol="HTTP", nodes=nodes,
                        virtual_ips=[vip])
print "New Cloud LB ID: %s" % newLb.id
print "\n%(header)sCloud LB Built! Waiting for 'ACTIVE'... %(endc)s" % {
    "header": bcolors.HEADER, "endc": bcolors.ENDC}

try:
    pyrax.utils.wait_until(newLb, "status", ['ACTIVE', 'ERROR'], interval=5,
                           attempts=24, verbose=True)
except exc.BadResponse:
    pyrax.utils.wait_until(newLb, "status", ['ACTIVE', 'ERROR'], interval=5,
                           attempts=24, verbose=True)

if (str(newLb.status) == 'ACTIVE'):
    print("%(head)sCloud Load-balancer is now active!"
          "%(endc)s") % {"head": bcolors.HEADER, "endc": bcolors.ENDC}
    print bcolors.OKBLUE
    print "LB Name: %s" % str(newLb.name)
    print "LB Port: %s" % str(newLb.port)
    print "Protocol: %s" % str(newLb.protocol)
    print "Algorithm: %s" % str(newLb.algorithm)
    print "LB IP: %(a)s" % {"a": newLb.virtual_ips[0]}
    print bcolors.ENDC
elif (str(newLb.status) == 'ERROR') or (str(newLb.status) == 'BUILD'):
    print bcolors.FAIL
    print("You got a problem, Jack! Your new LB has a status"
          " of '%s'!") % str(newLb.status)
    print "LB Name: %s" % str(newLb.name)
    print bcolors.WARN
    print "Debug Info:"
    print str(newLb)
    print bcolors.ENDC
