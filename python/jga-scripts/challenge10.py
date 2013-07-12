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
import pyrax
import pyrax.exceptions as exc
import pyrax.utils as utils
# Pre-defined Variables
defConfigFile = os.path.expanduser('~') + '/.rackspace_cloud_credentials'
progName = 'RAX Challenge-inator 10,000'
numServers = 2
metaWeb = 'X-Container-Meta-Web-Index'
authKeysDest = '/root/.ssh/authorized_keys'
pubKey = "ssh-dss AAAAB3NzaC1kc3MAAACBAMa7vKRyD1L5z2DUbcapO9/8dLswyAFFZAeb" \
         "XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX" \
         "MzD7/kRFwwv9w6dD0WCgS+zRQBggsVufMnNfEe9RLAzFHulGNxnfN4yOS276T0sw" \
         "h5mskJlPAAAAFQCCL0+/2tzsCXRmvjh5gO/Jo8Mb2wAAAIAn0MaHFch0hTnzwVuk" \
         "V24VsgrgGl0CAR5ZDAIKxZHfLJTzV/4YOCBtJi4m3yJmDlzXtxmQQTU9ZVi4/m7C" \
         "aFidHmD4z2xUOTsWNO0mp+CxTQMJHUX7oJokERptfCNDxK82eUlrunoj3wrHy7S4" \
         "xamaobAuVeitV5B4K8W24ohXdQAAAIB0/lH/XvKn3qg4MV0cWyUgNyDsU3LKmGFW" \
         "BB/WWDNW1iPM6lUROgpftXqd1KNw2RlubwAbCDefGHiJKLpEW3nSUsKCJJSxhCTK" \
         "uJoT7htfHRLRE26+8y3SnJph2cvza+QbmtMHqLEA1+b8JR/feIadzERRAlpI08S0" \
         "h+S8iTi//Q== blah@blah.com"
errorHtml = """\
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
                    Whoops!
                </h1>
                <p>
                    Something went terribly wrong...
                </p>
            </div>
        </div>
    </body>
</html>
"""

# Argument Parsing
raxParse = argparse.ArgumentParser(description="Write an application that \
    when passed the arguments FQDN, image, and flavor it creates a server of \
    the specified image and flavor with the same name as the fqdn, and \
    creates a DNS entry for the fqdn pointing to the server's public IP")
raxParse.add_argument('-c', '--config', dest='configFile', help="Location of \
    the config file", default=defConfigFile)
raxParse.add_argument('FQDN', help="FQDN of the LB to be created.")
raxParse.add_argument('domain', help="Domain name containing the LB.")
raxParse.add_argument('imgID', help="ID of the Image to use when building \
    the server.")
raxParse.add_argument('flvrID', help="ID of the Flavor to use when building \
    the server.")
raxParse.add_argument('cfContainer', help="Container name to store the LB \
    error page backup.")
raxParse.add_argument('-k', '--key', dest='sshKeyFile', help="Location of \
    the ssh public key file to be uploaded to /root/.ssh/authorized_keys \
    on the newly built server. (If one is not specified, then the one \
    embedded in the script's 'pubKey' variable is used.)")
raxParse.add_argument('-sn', '--server-name', dest='svrBaseName', help="Base \
    name to use when creating the server hostnames (i.e. 'web-')")
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


def raxCreateServer(raxCldSvr, numServers, svrBaseName, imgIDToUse,
                    flvrIDToUse):
    svrsCreated = {}  # Dictionary to hold info on the servers that get created
    nodeInfo = {}  # Dictionary to hold Private IPs of the nodes
    completed = []  # Array to hold the servers that complete creation
    authKeyFile = {'/root/.ssh/authorized_keys': pubKey}
    print 'Creating ' + str(numServers) + ' servers.'
    print 'Server name will begin with ' + svrBaseName
    for i in xrange(0, numServers):
        svrName = '%s%s.%s' % (svrBaseName, i, raxArgs.domain)
        svrsCreated[svrName] = raxCldSvr.servers.create(svrName, imgIDToUse,
                                                        flvrIDToUse,
                                                        files=authKeyFile)
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


def raxAddDNSA(lbIp):
    try:
        domid = raxDns.find(name=raxArgs.domain)
    except Exception as e:
        raise Exception(e)
    print "Creating DNS Record"
    aRec = [{
        "type": "A",
        "name": raxArgs.FQDN,
        "data": lbIp,
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

    return newRecord


def checkLb(newLb):
    try:
        pyrax.utils.wait_until(newLb, "status", ['ACTIVE', 'ERROR'],
                               interval=5, attempts=24, verbose=True)
    except exc.BadResponse:
        pyrax.utils.wait_until(newLb, "status", ['ACTIVE', 'ERROR'],
                               interval=5, attempts=24, verbose=True)
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


if raxArgs.verbose:
    pyrax.set_http_debug(True)
if raxArgs.dc:
    dc = raxArgs.dc
else:
    dc = pyrax.safe_region()
if raxArgs.sshKeyFile:
    pubKey = raxArgs.sshKeyFile
if raxArgs.svrBaseName:
    svrBaseName = raxArgs.svrBaseName
else:
    svrBaseName = 'wb-' + utils.random_name(length=3, ascii_only=True) + '-'

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

raxCf = pyrax.connect_to_cloudfiles(region=dc)
raxCldSvr = pyrax.connect_to_cloudservers(region=dc)
raxDns = pyrax.cloud_dns
raxCldLB = pyrax.connect_to_cloud_loadbalancers(region=dc)

print "\n%(header)sCreating Cloud Servers... %(endc)s" % {
    "header": bcolors.HEADER, "endc": bcolors.ENDC}
try:
    lbNodes = raxCreateServer(raxCldSvr, numServers, svrBaseName,
                              raxArgs.imgID, raxArgs.flvrID)
    print("%(hdr)sSuccessfully created %(numServers)s servers"
          "%(endc)s") % {"hdr": bcolors.HEADER, "numServers": numServers,
                         "endc": bcolors.ENDC}
except Exception as e:
    print("%(fail)sCan't create server: "
          "%(e)s%(endc)s") % {"fail": bcolors.FAIL,
                              "e": e, "endc": bcolors.ENDC}
    sys.exit(2)

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
newLb = raxCldLB.create(raxArgs.FQDN, port=80, protocol="HTTP", nodes=nodes,
                        virtual_ips=[vip])
print "New Cloud LB ID: %s" % newLb.id

print "\n%(header)sCloud LB Built! Waiting for 'ACTIVE'... %(endc)s" % {
    "header": bcolors.HEADER, "endc": bcolors.ENDC}
checkLb(newLb)

print "\n%(header)sSetting Custom Cloud LB Error Page! %(endc)s" % {
    "header": bcolors.HEADER, "endc": bcolors.ENDC}
try:
    newLb.manager.set_error_page(newLb, errorHtml)
except Exception as e:
    print "\n%(fail)sERROR Setting Custom CLB Error Page: %(e)s %(endc)s" % {
        "fail": bcolors.FAIL, "e": e, "endc": bcolors.ENDC}
checkLb(newLb)

print "\n%(header)sCreating Cloud LB Health Monitor! %(endc)s" % {
    "header": bcolors.HEADER, "endc": bcolors.ENDC}
try:
    newLb.add_health_monitor(type="CONNECT", delay=10, timeout=10,
                             attemptsBeforeDeactivation=3)
except Exception as e:
    print "\n%(fail)sERROR Creating CLB Health Monitor: %(e)s %(endc)s" % {
        "fail": bcolors.FAIL, "e": e, "endc": bcolors.ENDC}

print "\n%(header)sCreating DNS Entry for Cloud LB %(endc)s" % {
    "header": bcolors.HEADER, "endc": bcolors.ENDC}
try:
    dnsLB = raxAddDNSA(newLb.virtual_ips[0].address)
except Exception as e:
    print("%(fail)sCan't create DNS Entry: "
          "%(e)s%(endc)s") % {"fail": bcolors.FAIL,
                              "e": e, "endc": bcolors.ENDC}
try:
    cont = raxCf.create_container(raxArgs.cfContainer)
    print("%(hdr)sSuccessfully created %(raxArgs.cfContainer)s"
          "%(endc)s") % {"hdr": bcolors.HEADER,
                         "raxArgs.cfContainer": cont.name,
                         "endc": bcolors.ENDC}
except Exception as e:
    print("%(fail)sCan't create container: "
          "%(e)s%(endc)s") % {"fail": bcolors.FAIL,
                              "e": e, "endc": bcolors.ENDC}
    sys.exit(2)

print "\n%(header)sCreating error.html file... %(endc)s" % {
    "header": bcolors.HEADER, "endc": bcolors.ENDC}
try:
    indexObj = raxCf.store_object(cont, 'error.html', errorHtml)
except:
    print "\n%(fail)sERROR Creating error.html file... %(endc)s" % {
        "fail": bcolors.FAIL, "endc": bcolors.ENDC}
    sys.exit(3)

print "\n%(okb)sComplete!%(endc)s" % {
    "okb": bcolors.OKBLUE, "endc": bcolors.ENDC}
