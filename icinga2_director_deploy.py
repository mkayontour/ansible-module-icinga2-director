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
module: icinga2_director_deploy
short_description: Deploy configuration at your Icinga Web 2 Director
description: Use to deploy the configuration on you Director installation.
author: Thilo Wening (@mkayontour)
options
  host:
    description: The address and URI to the icingaweb2 UI.
    required: true
    type: string
  username:
    description: Username which is allowed to logon and use the director.
    required: true
    type: string
    aliases: name
  password:
    description: Password for the user to login.
    required: true
    type: string
  state:
    description: Present to actually deploy. (Default: Present)
    required: false
    type: string
    default: present
  name:
    description: no name
    required: false
    type: string

requirements:
  - requests
'''

EXAMPLES = r'''
# Create Host
- name: Create Host at Director
  icinga2_director_deploy:
    host: "http://icingaweb.localdomain/icingaweb2"
    username: 'icinga'
    password: 'icinga'
'''

RETURN = r'''
result:
  checksum: "checksum of the director configuration"
  status_code: "return value of the http request"
'''

import requests
import json
from ansible.module_utils.basic import AnsibleModule


class Icinga2DirectorDeploy(object):

    def __init__(self):
        self.host = module.params.get('host')
        self.username = module.params.get('username')
        self.password = module.params.get('password')
        self.headers = {'Accept': 'application/json'}

    def run(self):
        url = self.host + '/director'
        try:
            r = requests.post(url + '/config/deploy',
                              auth=(self.username, self.password),
                              headers=self.headers)

            if r.status_code == 200:
                res = dict(changed=True,
                           ansible_module_results=("successfully "
                                                   "deployed configuration"),
                           result=dict(r.json(), status_code=r.status_code))

            if r.status_code == 401:
                module.fail_json(msg=("Failed to login check "
                                      "username or password StatusCode: "
                                      + str(r.status_code)))
        except requests.exceptions.RequestException as e:
            module.fail_json(msg='Error: ' + str(e))

        return res


def main():
    global module
    module = AnsibleModule(
        argument_spec=dict(
            state=dict(required=False, default='present'),
            name=dict(required=False),
            host=dict(required=True),
            username=dict(required=True),
            password=dict(required=True, no_log=True)
        ),
        supports_check_mode=False,
    )

    result = Icinga2DirectorDeploy().run()
    module.exit_json(**result)


if __name__ == '__main__':
    main()
