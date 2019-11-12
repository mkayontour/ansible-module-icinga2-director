# Ansible Module Icinga2 Director

## Description

This module can create, update, or delete hosts at the director. 

This is the first, go for this Ansible Module. For the parameter documentation check the ansible-doc

`ansible-doc icinga2_director_host`

## Todos

Create as much objects at possible within these modules or this module.

We should be able to create anything ad-hoc with ansible on the director. 


## Installation

First two things to mention:

I will try to officially push this to Ansible, but this needs much more testing than a smoketest.

I could try to put everything into a collection, then it could be easier to install for ansible. (maybe?) 

Otherwise

Clone this repository onto your Ansible Host, and provide the folder in your **ANSIBLE_MODULE_PATH** variable.

You can also set it as environment variable.

```
export ANSIBLE_LIBRARY=$ANSIBLE_LIBRARY:/path/to/local/repository
```

Afterwards you should be getting the documentation for the module!

```
ansible-doc icigna2_director_host
```

And then use it as every plugin in your playbooks or roles.

```yaml
- name: create simple Host
  icinga2_director_host:
    name: simple.plan.localdomain
    host: http://icingaweb2.local/icingaweb2
    username: icinga
    password: secret
    update_if_exists: true
    host_vars:
      address: "127.0.0.1"
      check_command: "hostalive"
    custom_vars:
      os: "Linux"
    templates:
      - "basic-host"

```
