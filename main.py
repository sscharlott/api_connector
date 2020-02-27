#!/usr/local/Cellar/python/3.7.6_1/bin/python3
import json
import warnings
import errno
import os
import requests
import shutil
import traceback
import urllib
import uuid
import time
import sys
import urllib3
import re

# include other python script so we can use their code
import show_vms
import powerstate

# remove some of the noise
requests.packages.urllib3.disable_warnings()
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

#username = 'stefansch@ntnx.test'
#password = 'nutanix/4u'
#cluster_ip = '172.23.1.110'

username = 'stefan'
password = 'Scharly83!'
cluster_ip = '10.38.6.71'
base_url = ("https://%s:9440/PrismGateway/services/rest/v2.0/" % (cluster_ip))
new_state = "off"

# list of VMs that should be ignored as part of the actions below
# list accepts regular expressions
ignorelist = [".*PRISM.*", ".*prism.*", ".*CVM.*", ".*cvm.*", "test1", ".*files.*"]

# get a list of all VMs tat are running on the above specified cluster
vm_data = show_vms.get_vms(username, password, base_url)

# comment this out if you simply want to print the list
#for e in vm_data["entities"]:
#    print e["name"]

# this section will call the powerstate function and perform an on or off depending
# on what has been specified in the new_state variable
for e in vm_data["entities"]:
    temp = '(?:%s)' % '|'.join(ignorelist)
    if re.match(temp, e["name"]):
      print ("skipping %s as specified in the ignore list" % (e["name"]))
    else:
      powerstate.change_powerstate(cluster_ip, username, password, e["name"], new_state, base_url)
