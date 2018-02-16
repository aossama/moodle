# Bootstrap Moodle

Bootstrap Moodle is a set of playbooks to prepare an infrastructure ready to host Moodle installation on either VMs or AWS.

## Overview

### Inventory

The inventory has several environments you can use them based on your need:

  * AWS: WIP
  * dev: Suited for the development environment in a multi-stage environment
  * stage: Suited for the development environment in a multi-stage environment
  * production: Suited for the development environment in a multi-stage environment
  * sandbox: The playground suited for a virtnualized infrastructure

### Playbooks

All playbooks are invoked from the base.yml playbooks.

 * infrastructure.yml
 * common.yml
 * webservers.yml
 * database.yml
 * moodle.yml

## Getting Started

### Prepare virtual machines

Prepare a set of virtual machines on your preferred virtualization platform (VirtualBox, libvirt)

### Prepare for AWS

1. First you need to have a virtualenv (just not to mess up your system)
```bash
$ virtualenv -p /usr/bin/python3 .env
$ source ./.env/bin/activate
$ pip install -r requirements.txt 
```

2. Set AWS_ACCESS_KEY_ID and AWS_SECRET_ACCESS_KEY environment variables
```bash
$ export AWS_ACCESS_KEY_ID=THISISNOTMYAWSACCESSKEY
$ export AWS_SECRET_ACCESS_KEY=THISISNOTMYAWSSECRETACCESSKEY
```

3. Create a new stack
```bash
$ ./aws.py --route53-hosted-zone moodle.local --keypair 'my-aws-kp'
```

Please note that this will create a stack with the default configuration and inccur charges as it'll provision a bastion 
server.
