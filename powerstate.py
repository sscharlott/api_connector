import requests
import time
import json
import urllib
import urllib3

# remove some of the noise
requests.packages.urllib3.disable_warnings()
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

## usage: python  powerstate_v2.py <vmname> <ON|OFF>

class RestApiClient():

  def __init__(self, cluster_ip, username, password, base_url):
    self.cluster_ip = cluster_ip
    self.username = username
    self.password = password
    self.base_pg_url = base_url
    self.session = self.get_server_session(self.username, self.password)


  def get_server_session(self, username, password):
    session = requests.Session()
    session.auth = (username, password)
    session.verify = False
    session.headers.update(
        {'Content-Type': 'application/json; charset=utf-8'})
    return session


  def resolve_vm_uuid(self, vm_name, base_url):
    url = base_url + "/vms/"
    r = self.session.get(url)

    if r.status_code != requests.codes.ok:
      raise Exception("GET %s: %s" % (url, r.status_code))

    obj = r.json()
    uuid = [x["uuid"] for x in obj["entities"] if x["name"] == vm_name]
    powerstate = [x["power_state"] for x in obj["entities"] if x["name"] == vm_name]

    return uuid[0], powerstate[0]


  def _strip_empty_fields(self, proto_dict):
    def strip_dict(d):
      if type(d) is dict:
        return dict((k, strip_dict(v))\
                    for k,v in d.iteritems() if v and strip_dict(v))
      if type(d) is list:
        return [strip_dict(v) for v in d if v and strip_dict(v)]
      else:
        return d
    return strip_dict(proto_dict)


  def construct_vm_power_proto(self, vm_uuid, powerstate):
    return {"transition": powerstate}


  def poll_task(self, task_uuid, base_url):
    url = base_url+"tasks/poll"

    specs = []
    specs.append(task_uuid)
    uuidSpec = {}
    uuidSpec["completed_tasks"] = specs

    while True:
      print("Polling task %s for completion" % (task_uuid,))
      r = self.session.post(url, data=json.dumps(uuidSpec))
      if r.status_code != 201:
        raise Exception("GET %s: %s" % (url, r.status_code))

      obj = r.json()
      for entry in obj['completed_tasks_info']:
        mr = entry['meta_response']['error_code']

      if mr is None:
        continue
      if mr is 0:
        break
      else:
        raise Exception("Task %s failed with error code: %s" %
            (task_uuid, mr))


  def set_power_state(self, vm_uuid, base_url, powerstate):
    cloneSpec = self.construct_vm_power_proto(vm_uuid, powerstate)
    url = base_url + "vms/"+str(vm_uuid)+"/set_power_state/"

    print ("TASK START TIME", time.strftime("%H:%M:%S"))
    r = self.session.post(url, data=json.dumps(cloneSpec))
    if r.status_code != 201:
      raise Exception("POST %s: %s" % (url, r.status_code))

    task_uuid = r.json()["task_uuid"]
    self.poll_task(task_uuid, base_url)
    print ("TASK END TIME", time.strftime("%H:%M:%S"))


def change_powerstate(cluster_ip, username, password, vm_name, powerstate, base_url):
  c = RestApiClient(cluster_ip, username, password, base_url)
  vm_uuid, current_powerstate = c.resolve_vm_uuid(vm_name, base_url)

  if current_powerstate == powerstate:
      print ("%s is already in powerstate %s, skipping" % (vm_name, powerstate))
  else:
      c.set_power_state(vm_uuid, base_url, powerstate)
