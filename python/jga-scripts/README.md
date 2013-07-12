RAX-API-Challenge
=================

Script submissions for the Rackspace Support Cloud API Challenge using pyrax


## Challenge 1 _(challenge1.py)_ ##
#### Cloud Servers ####

__Goal:__ Write a script that builds three 512MB Cloud Servers that follow a similar naming convention. (i.e. web1, web2, web3) and returns the IP and login credentials for each server.  Use any image.  

	usage: challenge1.py [-h] [-c CONFIGFILE] [-ls] [-cs] [-ns NUMSERVERS]
                     [-sn SVRBASENAME] [-img IMGIDTOUSE] [-flv FLVRIDTOUSE]
                     [-i] [-dc {DFW,ORD,LON}] [-d] [-V]

	Challenge 1 of the API Challenge: Write a script that builds three 512 MB
	Cloud Servers that following a similar naming convention. (ie., web1, web2,
	web3) and returns the IP and login credentials for each server. Use any image
	you want.

	optional arguments:
	  -h, --help            show this help message and exit
	  -c CONFIGFILE, --config CONFIGFILE
	                        Location of the config file
	  -ls, --list-servers   List Cloud Servers
	  -cs, --create-server  Create Server
	  -ns NUMSERVERS, --number-of-servers NUMSERVERS
	                        Number of servers
	  -sn SVRBASENAME, --server-name SVRBASENAME
	                        Base name of servers
	  -img IMGIDTOUSE, --image-ID IMGIDTOUSE
	                        Image ID for building servers
	  -flv FLVRIDTOUSE, --flavor-ID FLVRIDTOUSE
	                        Flavor ID for building servers
	  -i, --interactive     Interactively prompt for info
	  -dc {DFW,ORD,LON}
	  -d                    Show debug info, such as HTTP responses
	  -V, --version         show program's version number and exit

	You MUST select either '-ls' or '-cs'!
	  
## Challenge 2 _(challenge2.py)_ ##
#### Cloud Servers ####

__Goal:__ Write a script that clones a server (takes an image and deploys the image as a new server).

	usage: challenge2.py [-h] [-c CONFIGFILE] [-ci] [-cs] [-ns NUMSERVERS]
                     [-sn SVRBASENAME] [-dc {DFW,ORD,LON}] [-d] [-V]

	Challenge 2 of the API Challenge: Write a script that clones a server (takes
	an image and deploys the image as a new server).

	optional arguments:
	  -h, --help            show this help message and exit
	  -c CONFIGFILE, --config CONFIGFILE
	                        Location of the config file
	  -ci, --create-image   Create an Image from a server
	  -cs, --create-server  Create Server
	  -ns NUMSERVERS, --number-of-servers NUMSERVERS
	                        Number of servers
	  -sn SVRBASENAME, --server-name SVRBASENAME
	                        Base name of servers
	  -dc {DFW,ORD,LON}
	  -d                    Show debug info, such as HTTP responses
	  -V, --version         show program's version number and exit

	You MUST select either '-ci' or '-cs'!
	  
## Challenge 3 _(challenge3.py)_ ##
#### Cloud Files ####

__Goal:__ Write a script that accepts a directory as an argument as well as a container name. The script should upload the contents of the specified directory to the container (or create it if it doesn't exist). The script should handle errors appropriately. (Check for invalid paths, etc.)

	usage: challenge3.py [-h] [-c CONFIGFILE] [-dc {DFW,ORD,LON}] [-v] [-V]
                     originDir containerName

	Challenge 3 of the API Challenge: Write a script that accepts a directory as
	an argument as well as a container name. The script should upload the contents
	of the specified directory to the container (or create it if it doesn't
	exist). The script should handle errors appropriately. (Check for invalid
	paths, etc.)

	positional arguments:
	  originDir             Directory containing source files to upload to CF
	                        Container
	  containerName         Name of the new CF Container to hold the uploaded
	                        files

	optional arguments:
	  -h, --help            show this help message and exit
	  -c CONFIGFILE, --config CONFIGFILE
	                        Location of the config file
	  -dc {DFW,ORD,LON}
	  -v                    Show debug info, such as HTTP responses
	  -V, --version         show program's version number and exit
## Challenge 4 _(challenge4.py)_ ##
#### Cloud DNS ####

__Goal:__ Write a script that uses Cloud DNS to create a new A record when passed a FQDN and IP address as arguments.  

	usage: challenge4.py [-h] [-c CONFIGFILE] [-ld] [-d] [-V] aFQDN aIP domainName

	Challenge 4 of the API Challenge: Write a script that uses Cloud DNS to create
	a new A record when passed a FQDN and IP address as arguments.

	positional arguments:
	  aFQDN                 FQDN for new A record
	  aIP                   IP for new A record
	  domainName            Domain

	optional arguments:
	  -h, --help            show this help message and exit
	  -c CONFIGFILE, --config CONFIGFILE
	                        Location of the config file
	  -ld, --list-domains   List Domain Names in DNS
	  -d                    Show debug info, such as HTTP responses
	  -V, --version         show program's version number and exit
## Challenge 5 _(challenge5.py)_ ##
#### Cloud Databases ####

__Goal:__ Write a script that creates a Cloud Database instance. This instance should contain at least one database, and the database should have at least one user that can connect to it.

	usage: challenge5.py [-h] [-c CONFIGFILE] [-p DBPASS] [-f {1,2,3,4,5,6}]
                     [-s {1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24,25,26,27,28,29,30,31,32,33,34,35,36,37,38,39,40,41,42,43,44,45,46,47,48,49,50}]
                     [-dc {DFW,ORD,LON}] [-d] [-V]
                     instanceName dbName dbUser

	Challenge 5 of the API Challenge: Write a script that creates a Cloud Database
	instance. This instance should contain at least one database, and the database
	should have at least one user that can connect to it.

	positional arguments:
	  instanceName          Name of the Database Instance
	  dbName                Name of the Database
	  dbUser                Name of the Database User

	optional arguments:
	  -h, --help            show this help message and exit
	  -c CONFIGFILE, --config CONFIGFILE
	                        Location of the config file
	  -p DBPASS, --db-pass DBPASS
	                        Password for the Database User
	  -f {1,2,3,4,5,6}, --flavor {1,2,3,4,5,6}
	                        Flavor to use for the Database Instance
	  -s {1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24,25,26,27,28,29,30,31,32,33,34,35,36,37,38,39,40,41,42,43,44,45,46,47,48,49,50}
	                        Size of the Database Instance in GB (1-50)
	  -dc {DFW,ORD,LON}
	  -d                    Show debug info, such as HTTP responses
	  -V, --version         show program's version number and exit
## Challenge 6 _(challenge6.py)_ ##
#### Cloud Files (CDN) ####

__Goal:__ Write a script that creates a CDN-enabled container in Cloud Files.

	usage: challenge6.py [-h] [-c CONFIGFILE] [-dc {DFW,ORD,LON}] [-v] [-V]
                     contName

	Challenge 6 of the API Challenge: Write a script that creates a CDN-enabled
	container in Cloud Files.

	positional arguments:
	  contName              Name of the new CF Container to hold the uploaded
	                        files

	optional arguments:
	  -h, --help            show this help message and exit
	  -c CONFIGFILE, --config CONFIGFILE
	                        Location of the config file
	  -dc {DFW,ORD,LON}
	  -v                    Show debug info, such as HTTP responses
	  -V, --version         show program's version number and exit
## Challenge 7 _(challenge7.py)_ ##
#### Cloud Loadbalancers ####

__Goal:__ Write a script that will create 2 Cloud Servers and add them as nodes to a new Cloud Load Balancer.

	usage: challenge7.py [-h] [-c CONFIGFILE] [-sn SVRBASENAME] [-si IMGIDTOUSE]
                     [-sf FLVRIDTOUSE] [-ln LBNAME] [-n NUMSERVERS]
                     [-dc {DFW,ORD,LON}] [-v] [-V]

	Challenge 7 of the API Challenge: Write a script that will create 2 Cloud
	Servers and add them as nodes to a new Cloud Load Balancer.

	optional arguments:
	  -h, --help            show this help message and exit
	  -c CONFIGFILE, --config CONFIGFILE
	                        Location of the config file
	  -sn SVRBASENAME, --server-name SVRBASENAME
	                        Base name of the newly created servers
	  -si IMGIDTOUSE, --server-image IMGIDTOUSE
	                        ID of the server image to use
	  -sf FLVRIDTOUSE, --server-flavor FLVRIDTOUSE
	                        ID of the server flavor to use
	  -ln LBNAME, --lb-name LBNAME
	                        Name of the load-balacer to create
	  -n NUMSERVERS, --num-servers NUMSERVERS
	                        Number of servers to create
	  -dc {DFW,ORD,LON}
	  -v                    Show debug info, such as HTTP responses
	  -V, --version         show program's version number and exit
## Challenge 8 _(challenge8.py)_ ##
#### Cloud Files (CDN) & Cloud DNS ####

__Goal:__ Write a script that will create a static webpage served out of Cloud Files. The script must create a new container, cdn enable it, enable it to serve an index file, create an index file object, upload the object to the container, and create a CNAME record pointing to the CDN URL of the container.

	usage: challenge8.py [-h] [-c CONFIGFILE] -co CONTNAME [-dns DNSDOMAIN]
                     [-cn CNAME] [-dc {DFW,ORD,LON}] [-v] [-V]

	Challenge 8 of the API Challenge: Write a script that will create a static
	webpage served out of Cloud Files. The script must create a new container, cdn
	enable it, enable it to serve an index file, create an index file object,
	upload the object to the container, and create a CNAME record pointing to the
	CDN URL of the container.

	optional arguments:
	  -h, --help            show this help message and exit
	  -c CONFIGFILE, --config CONFIGFILE
	                        Location of the config file
	  -co CONTNAME, --container CONTNAME
	                        Name of the new CF Container to hold the uploaded
	                        files
	  -dns DNSDOMAIN        DNS Domain to use
	  -cn CNAME             CNAME to use
	  -dc {DFW,ORD,LON}
	  -v                    Show debug info, such as HTTP responses
	  -V, --version         show program's version number and exit
## Challenge 9 _(challenge9.py)_ ##
#### Cloud Servers & Cloud DNS ####

__Goal:__ Write an application that when passed the arguments FQDN, image, and flavor it creates a server of the specified image and flavor with the same name as the fqdn, and creates a DNS entry for the fqdn pointing to the server's public IP

	usage: challenge9.py [-h] [-c CONFIGFILE] [-dc {DFW,ORD,LON}] [-v] [-V]
                     FQDN domain imgID flvrID

	Write an application that when passed the arguments FQDN, image, and flavor it
	creates a server of the specified image and flavor with the same name as the
	fqdn, and creates a DNS entry for the fqdn pointing to the server's public IP

	positional arguments:
	  FQDN                  FQDN of the server to be created.
	  domain                Domain name of the server.
	  imgID                 ID of the Image to use when building the server.
	  flvrID                ID of the Flavor to use when building the server.

	optional arguments:
	  -h, --help            show this help message and exit
	  -c CONFIGFILE, --config CONFIGFILE
	                        Location of the config file
	  -dc {DFW,ORD,LON}
	  -v                    Show debug info, such as HTTP responses
	  -V, --version         show program's version number and exit

## Challenge 10 _(challenge10.py)_ ##
#### Cloud Servers, Cloud LB, Cloud DNS, Cloud Files ####

__Goal:__ Write an application that will:
- Create 2 servers, supplying a ssh key to be installed at /root/.ssh/authorized_keys.
- Create a load balancer
- Add the 2 new servers to the LB
- Set up LB monitor and custom error page. 
- Create a DNS record based on a FQDN for the LB VIP. 
- Write the error page html to a file in cloud files for backup.

	usage: challenge10.py [-h] [-c CONFIGFILE] [-k SSHKEYFILE] [-sn SVRBASENAME]
                      [-dc {DFW,ORD,LON}] [-v] [-V]
                      FQDN domain imgID flvrID cfContainer

	Write an application that when passed the arguments FQDN, image, and flavor it
	creates a server of the specified image and flavor with the same name as the
	fqdn, and creates a DNS entry for the fqdn pointing to the server's public IP

	positional arguments:
	  FQDN                  FQDN of the LB to be created.
	  domain                Domain name containing the LB.
	  imgID                 ID of the Image to use when building the server.
	  flvrID                ID of the Flavor to use when building the server.
	  cfContainer           Container name to store the LB error page backup.

	optional arguments:
	  -h, --help            show this help message and exit
	  -c CONFIGFILE, --config CONFIGFILE
	                        Location of the config file
	  -k SSHKEYFILE, --key SSHKEYFILE
	                        Location of the ssh public key file to be uploaded to
	                        /root/.ssh/authorized_keys on the newly built server.
	                        (If one is not specified, then the one embedded in the
	                        script's 'pubKey' variable is used.)
	  -sn SVRBASENAME, --server-name SVRBASENAME
	                        Base name to use when creating the server hostnames
	                        (i.e. 'web-')
	  -dc {DFW,ORD,LON}
	  -v                    Show debug info, such as HTTP responses
	  -V, --version         show program's version number and exit
## Challenge 11 _(challenge11.py)_ ##
#### Cloud Networks, Cloud Servers, Cloud LB, ####
#### Cloud DNS, Cloud Block Storage ####

__Goal:__ Write an application that will:
- Create an SSL terminated load balancer (Create self-signed certificate.)
- Create a DNS record that should be pointed to the load balancer.
- Create Three servers as nodes behind the LB.
- Each server should have a CBS volume attached to it. (Size and type are irrelevant.)
- All three servers should have a private Cloud Network shared between them.
- Login information to all three servers returned in a readable format as the result of the script, including connection information.
	
	usage: challenge11.py [-h] [-c CONFIGFILE] [-sn SVRBASENAME] [-crt CRTFILE]
	                      [-key KEYFILE] [-dc {DFW,ORD,LON}] [-v] [-V]
	                      FQDN domain imgID flvrID

	Write an application that when passed the arguments FQDN, image, and flavor it
	creates a server of the specified image and flavor with the same name as the
	fqdn, and creates a DNS entry for the fqdn pointing to the server's public IP

	positional arguments:
	  FQDN                  FQDN of the LB to be created.
	  domain                Domain name containing the LB.
	  imgID                 ID of the Image to use when building the server.
	  flvrID                ID of the Flavor to use when building the server.

	optional arguments:
	  -h, --help            show this help message and exit
	  -c CONFIGFILE, --config CONFIGFILE
	                        Location of the config file
	  -sn SVRBASENAME, --server-name SVRBASENAME
	                        Base name to use when creating the server hostnames
	                        (i.e. 'web-')
	  -crt CRTFILE, --cert-file CRTFILE
	                        Location of the file containing the SSL CRT. If not
	                        defined, the value will default to 'challenge11.crt'.
	  -key KEYFILE, --key-file KEYFILE
	                        Location of the file containing the SSL KEY. If not
	                        defined, the value will default to 'challenge11.key'.
	  -dc {DFW,ORD,LON}
	  -v                    Show debug info, such as HTTP responses
	  -V, --version         show program's version number and exit
## Challenge 12 _(challenge12.rb)_ ##
#### Mailgun API ####

__Goal:__ Write an application that will create a route in mailgun so that when an email is sent to <YourSSO>@apichallenges.mailgun.org it calls your Challenge 1 script that builds 3 servers.
__Assumptions__: 
Assume that challenge 1 can be kicked off by accessing http://cldsrvr.com/challenge1 (I am aware this doesn't work. You just need to make sure that your message is getting posted to that URL)

	Usage: challenge12.rb [options]
	    -h, --help                       Help
	    -v, --version                    Version Info
	    -l, --list-routes                List Routes
	    -c, --create-route               Create Route
	    -k, --api-key APIKEY             API Key
	    -m, --mailbox MAILBOX            Mailbox name
## Requirements ##

- Rackspace Cloud Account
- Python 2.7 or higher
- Ruby (for Challenge 12)
- pyrax Python Module
- A pinch of swagger

## Miscellaneous ##

- When using a script that requires an Image ID, I used '__acf05b3c-5403-4cf0-900c-9b12b0db0644__' in my testing.  This is the Image ID for '_CentOS 5.8_'
- When using a script that requires a Flavor ID, I used '__2__' in my testing.  This is the Flavor ID for a 512MB cloud server.

## Status ##

Currently a work in progress