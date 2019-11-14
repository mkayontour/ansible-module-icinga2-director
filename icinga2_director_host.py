#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# (c) 2019, Thilo Wening <thilo.wening@netways.de>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function
__metaclass__ = type


ANSIBLE_METADATA = {'metadata_version': '0.1',
                    'status': ['preview'],
                    'supported_by': 'community'}

DOCUMENTATION = r'''
module: icinga2_director
short_description: Manage objects in icingaweb2 director
description: Create, update, replace or delete host objects in icinga2 director
author: Thilo Wening (@mkayontour)
options:
  name:
    description: Name of the host object
    required: true
    type: string
  state:
    description: |
      Choose between present or absent,
      whether the host should be created or deleted
    required: true
    type: string
  host:
    description: The address and URI to the icingaweb2 UI.
    required: true
    type: string
  username:
    description: Username which is allowed to logon and use the director.
    required: true
    type: string
  password:
    description: Password for the user to login.
    required: true
    type: string
  update_if_exists:
    description: Update the host in director if the host already exists
    required: false
    default: false
    type: bool
  host_vars:
    description: |
      A hash containing all
      vars which are provided at a host object.
    required: false
    type: dict
  custom_vars:
    description: A hash containing all custom vars provided to the host object.
    required: false
    type: dict
  templates:
    description: A list containing all templates which should be imported
    required: false
    type: list
requirements:
  - requests
'''

EXAMPLES = r'''
# Create Host
- name: Create Host at Director
  icinga2_director:
    name: agent.localdomain
    host: "http://icingaweb.localdomain/icingaweb2"
    username: 'icinga'
    password: 'icinga'
    state: 'present'
    templates:
      - "basic-host"
    host_vars:
      address: "127.0.0.1"
      check_interval: "300"
      check_command: "hostalive"
    custom_vars:
      os: "Linux"
      application: "Apache"
'''

RETURN = r'''
 test blubber
'''

import requests
import json
from ansible.module_utils.basic import AnsibleModule


class Icinga2Director(object):

    def __init__(self):
        self.state = module.params.get('state')
        self.host = module.params.get('host')
        self.name = module.params.get('name')
        self.username = module.params.get('username')
        self.password = module.params.get('password')
        self.enable_ssl = module.params.get('enable_ssl')
        self.exists = module.params.get('update_if_exists')
        self.custom_vars = module.params.get('custom_vars')
        self.host_vars = module.params.get('host_vars')
        self.imports = module.params.get('templates')
        self.headers = {'Accept': 'application/json'}

    def run(self):
        url = self.host + '/director'

        if self.state == "present":
            c = Icinga2Director().manage_host(url, action="create")
            if c.status_code == 201:
                res = dict(changed=True,
                           ansible_module_results="created new host object",
                           return_code=c.status_code)
                return res
            if c.status_code == 422 and self.exists:
                u = Icinga2Director().manage_host(url, action="update")
                if u.status_code == 304:
                    res = dict(changed=False,
                               ansible_module_results=("host object did not "
                                                       "change"),
                               return_code=u.status_code)
                elif u.status_code == 200:
                    res = dict(changed=True,
                               ansible_module_results=("host object "
                                                       "successfully updated"),
                               return_code=u.status_code)
                else:
                    module.fail_json(msg='Failed to create/update host' + u.text)
            else:
                res = dict(changed=False,
                           ansible_module_results=("host object already "
                                                   "created"),
                           return_code=c.status_code)

        elif self.state == 'absent':
            d = Icinga2Director().manage_host(url, action="delete")
            if d.status_code == 200:
                res = dict(changed=True,
                           ansible_module_results=("host object successfully "
                                                   "deleted"),
                           return_code=d.status_code)
            else:
                res = dict(change=True,
                           ansible_module_results=("delete host "
                                                   "failed " + d.text),
                           return_code=d.status_code)
                module.fail_json(msg='Failed to delete host', **res)
        return res

    def manage_host(self, url, action):

        if action == 'create':
            payload = Icinga2Director().struct_data()
            try:
                r = requests.post(url + '/host',
                                  auth=(self.username, self.password),
                                  headers=self.headers,
                                  data=json.dumps(payload))
                if r.status_code == 401:
                    module.fail_json(msg=("Failed to login check "
                                          "username or password StatusCode: "
                                          + str(r.status_code)))
            except requests.exceptions.RequestException as e:
                module.fail_json(msg='Error: ' + str(e))

        elif action == 'update':
            payload = Icinga2Director().struct_data()
            try:
                r = requests.put(url + '/host?name=' + self.name,
                                  auth=(self.username, self.password),
                                  headers=self.headers,
                                  data=json.dumps(payload))
                if r.status_code == 401:
                    module.fail_json(msg=("Failed to login check "
                                          "username or password StatusCode: "
                                          + str(r.status_code)))
            except requests.exceptions.RequestException as e:
                module.fail_json(msg='Error: ' + str(e))
        elif action == 'delete':
            try:
                r = requests.delete(url + '/host?name=' + self.name,
                                    auth=(self.username, self.password),
                                    headers=self.headers)
                if r.status_code == 401:
                    module.fail_json(msg=("Failed to login check "
                                          "username or password StatusCode: "
                                          + str(r.status_code)))
            except requests.exceptions.RequestException as e:
                module.fail_json(msg='Error: ' + str(e))
        else:
            module.fail_json(msg=("unsupported action "
                                  "evaluated in manage_host()"))
        return r

    def struct_data(self):
        data = {
                "object_name": self.name,
                "object_type": "object",
                "vars": {},
               }

        if self.host_vars:
            vars = self.host_vars
            data.update(vars)

        if self.custom_vars:
            data['vars'].update(self.custom_vars)

        if self.imports:
            imports = {
              "imports": self.imports
            }
            data.update(imports)

        return data


def main():
    global module
    module = AnsibleModule(
        argument_spec=dict(
            name=dict(required=True),
            state=dict(required=True, choices=['present', 'absent']),
            host=dict(required=True),
            username=dict(required=True),
            password=dict(required=True, no_log=True),
            # enable_ssl=dict(required=False, default=False, type='bool'),
            custom_vars=dict(required=False, type='dict'),
            host_vars=dict(required=False, type='dict'),
            templates=dict(required=False, type='list'),
            update_if_exists=dict(type='bool')
        ),
        supports_check_mode=False,
    )

    result = Icinga2Director().run()
    module.exit_json(**result)


if __name__ == '__main__':
    main()
