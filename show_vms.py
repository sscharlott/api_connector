import requests
import urllib3

# remove some of the noise
requests.packages.urllib3.disable_warnings()
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# performs a simple get request against the Nutanix API to get a list of all the VMs
def get_vms(username, password, base_url):

  s = requests.Session()
  s.auth = (username, password)
  s.headers.update({'Content-Type': 'application/json; charset=utf-8'})

  vm_data = s.get(base_url + 'vms', verify=False).json()

  return vm_data
