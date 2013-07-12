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

# Pre-defined Variables
defConfigFile = os.path.expanduser('~') + '/.rackspace_cloud_credentials'
progName = 'RAX Challenge-inator 5000'
dbName = None

# Argument Parsing
raxParse = argparse.ArgumentParser(description='Challenge 5 of the API \
    Challenge: Write a script that creates a Cloud Database instance. This \
    instance should contain at least one database, and the database should \
    have at least one user that can connect to it.')
raxParse.add_argument('-c', '--config', dest='configFile', help="Location of \
    the config file", default=defConfigFile)
raxParse.add_argument('instanceName', help="Name of the Database Instance")
raxParse.add_argument('dbName', help="Name of the Database")
raxParse.add_argument('dbUser', help="Name of the  Database User")
raxParse.add_argument('-p', '--db-pass', dest='dbPass', help="Password for \
    the Database User")
raxParse.add_argument('-f', '--flavor', dest='flavor', help='Flavor to \
    use for the Database Instance', type=int, choices=xrange(1, 7))
raxParse.add_argument('-s', dest='instSize', help='Size of the \
    Database Instance in GB (1-50)', type=int, choices=xrange(1, 51))
raxParse.add_argument('-dc', choices=['DFW', 'ORD', 'LON'])
raxParse.add_argument('-d', dest='debug', action='store_true', help="Show \
    debug info, such as HTTP responses")
raxParse.add_argument('-V', '--version', action='version', version='%(prog)s \
    0.1 by Javier Ayala')
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


def raxCreateInstance():
    """Create a new Cloud Database Instance"""
    flavors = cdb.list_flavors()
    if (raxArgs.flavor is None):
        print "\n%(header)sAvailable Cloud DB Flavors: %(endc)s" % {
            "header": bcolors.HEADER, "endc": bcolors.ENDC}
        for pos, flavor in enumerate(flavors):
            print "%s: %s [%s]" % (flavor.id, flavor.name, flavor.ram)
        flavor2use = int(raw_input(
            "Select a Flavor for the new Cloud DB Instance: "))
    else:
        flavor2use = raxArgs.flavor
    try:
        selectedFlvr = [flvr.id for flvr in flavors if
                        flvr.id == flavor2use][0]
    except:
        print "%(fail)sInvalid Flavor Selection!%(endc)s" % {
            "fail": bcolors.FAIL, "endc": bcolors.ENDC}
        sys.exit(1)
    if (raxArgs.instanceName is None):
        instanceName = raw_input("Enter a name for your  Cloud DB Instance: ")
    else:
        instanceName = raxArgs.instanceName
    if (raxArgs.instSize is None):
        instanceSize = int(raw_input("Enter the Instance Size in GB(1-50): "))
        if ((instanceSize < 1) or (instanceSize > 50)):
            print "%(fail)sInstance Size MUST be between 1-50!%(endc)s" % {
                "fail": bcolors.FAIL, "endc": bcolors.ENDC}
            sys.exit(1)
    else:
        instanceSize = raxArgs.instSize
    print "\n%(header)sCreating Cloud DB Instance... %(endc)s\n" % {
        "header": bcolors.HEADER, "endc": bcolors.ENDC}
    newInstance = cdb.create(instanceName, flavor=selectedFlvr,
                             volume=instanceSize)
    dbInstReady = False
    while (dbInstReady is False):
        print "Waiting for instance '%(name)s' to become active..." \
            % {"name": newInstance.name}
        if newInstance.status == 'ACTIVE':
            print "Instance is ready"
            dbInstReady = True
        else:
            time.sleep(30)
            newInstance.get()

    return newInstance


def raxCreateDb(dbInst):
    """Provided an Instance ID, create a cloud database on the instance."""
    if (raxArgs.dbName is None):
        dbName = raw_input("Enter the name of the new database: ")
    else:
        dbName = raxArgs.dbName
    print("\n%(header)sCreating Cloud DB '%(db)s' inside Instance "
          "'%(inst)s'...\n") % {"header": bcolors.HEADER, "db": dbName,
                                "inst": dbInst.name, "endc": bcolors.ENDC}
    newDbObj = dbInst.create_database(dbName)
    return newDbObj


def raxCreateUser(dbInst, dbName):
    """Provided a Cloud DB Instance and DB Name, create a cloud database user
        on the instance for that database."""
    if (raxArgs.dbUser is None):
        dbUser = raw_input("Enter the name of the new database user: ")
    else:
        dbUser = raxArgs.dbUser
    if (raxArgs.dbPass is None):
        dbPass = getpass.getpass("Enter the password for the new user: ")
    else:
        dbPass = raxArgs.dbPass
    print("\n%(header)sCreating Cloud DB User '%(usr)s' inside Instance "
          "'%(inst)s'...") % {"header": bcolors.HEADER, "usr": dbUser,
                              "inst": dbInst.name, "endc": bcolors.ENDC}
    newUserObj = dbInst.create_user(dbUser, dbPass, database_names=dbName)
    return newUserObj


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


if raxArgs.dc:
    dc = raxArgs.dc
else:
    dc = pyrax.safe_region()

print ("%(blue)sWhipping out our janitor's keyring to see if we have "
       "the right key to open the door...%(endc)s") % {"blue": bcolors.OKBLUE,
                                                       "endc": bcolors.ENDC}
try:
    myLogin = raxLogin(raxArgs.configFile)
    myLogin.authenticate()
except:
    print bcolors.FAIL + "Couldn't login" + bcolors.ENDC
    sys.exit(2)

cdb = pyrax.connect_to_cloud_databases(region=dc)

if raxArgs.debug:
    pyrax.set_http_debug(True)
try:
    newDbInst = raxCreateInstance()
except:
    print "%(fail)sUnable to create a new Cloud DB Instance!%(endc)s" % {
        "fail": bcolors.FAIL, "endc": bcolors.ENDC}
    print sys.exc_info()[0]
    sys.exit(2)

try:
    newDbObj = raxCreateDb(newDbInst)
except:
    print "%(fail)sUnable to create a new Cloud Database!%(endc)s" % {
        "fail": bcolors.FAIL, "endc": bcolors.ENDC}
    sys.exit(3)

try:
    newDbUserObj = raxCreateUser(newDbInst, newDbObj.name)
except:
    print "%(fail)sUnable to create a new Cloud DB User!%(endc)s" % {
        "fail": bcolors.FAIL, "endc": bcolors.ENDC}
    sys.exit(4)

print
print "%(hdr)sOperation Complete!%(endc)s\n" % {
    "hdr": bcolors.HEADER, "endc": bcolors.ENDC}
print "Instance Created: %s" % newDbInst.name
print "Instance Hostname: %s" % newDbInst.hostname
print "Database Created: %s" % newDbObj.name
print "%(ok)sUser '%(dbuser)s' given rights to '%(dbname)s'%(endc)s" % {
    "ok": bcolors.OKBLUE, "dbuser": newDbUserObj.name,
    "dbname": newDbObj.name, "endc": bcolors.ENDC}
