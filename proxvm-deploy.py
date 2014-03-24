#! /usr/bin/env python

import argparse
from subprocess import call
from importlib import import_module

from proxmoxer import ProxmoxAPI
from jinja2 import Environment, FileSystemLoader
from paramiko import SSHClient, WarningPolicy

from settings.settings import proxmox
from settings.instance import instance

# configuring and reading arguments
parser = argparse.ArgumentParser(description='Create a proxmox kvm and \
                                 cloudinit it.')

parser.add_argument('--vmid', '-v', type=int, help='Virtual machine id',
                    required=True)
parser.add_argument('--name', '-n', type=str,
                    help='Virtual machine name/hostname',
                    required=True)
parser.add_argument('--flavor', '-f', type=str,
                    default='small',
                    help='Virtual machine flavor')

args = parser.parse_args()

vmid = str(args.vmid)
name = args.name
flavor_type = args.flavor

# retrieve flavour
flavor_module = import_module('flavors.%s' % (flavor_type))
flavor = flavor_module.flavor

# configure instance custom details
instance['hd_root'] = instance['hd_root'] % (vmid, vmid)
instance['hd_seed'] = instance['hd_seed'] % (vmid, vmid)

for ifs in instance['ifs']:
    ifs['address'] = ifs['address'] % (vmid)

instance['vmid'] = vmid
instance['name'] = name

# proxmoxer initialize
proxmox_api = ProxmoxAPI(proxmox['host'], user=proxmox['user'],
                         password=proxmox['password'],
                         verify_ssl=proxmox['verify_ssl'])

node = proxmox_api.nodes(proxmox['node'])

# create kvm machine
node.qemu.create(vmid=vmid, name=name, sockets=flavor['sockets'],
                 cores=flavor['cores'], balloon=flavor['balloon'],
                 memory=flavor['memory'], net0=instance['net'])

# compile seed data
env = Environment(loader=FileSystemLoader('templates'))

metadata_j2 = env.get_template('meta-data.j2')
with open('meta-data', 'w') as metadata:
    metadata.write(metadata_j2.render(instance=instance))

userdata_j2 = env.get_template('user-data.j2')
with open('user-data', 'w') as userdata:
    userdata.write(userdata_j2.render(instance=instance))

# generate seed iso
call(['genisoimage', '-output', 'vm-%s-seed.raw' % (vmid),
     '-volid', 'cidata', '-joliet', '-rock', 'user-data', 'meta-data'])

# mv base image to current vmid (paramiko)
command = 'mkdir -p %s%s && cp -f %s%s %s%s' % (proxmox['images'],
                                                vmid,
                                                proxmox['images'],
                                                instance['os'],
                                                proxmox['images'],
                                                instance['hd_root'].replace('local:', ''))
proxmox_ssh = SSHClient()
proxmox_ssh.set_missing_host_key_policy(WarningPolicy())
proxmox_ssh.connect(proxmox['host'], username=proxmox['user'].split('@')[0])
stdin, stdout, stderr = proxmox_ssh.exec_command(command)

# sftp seed (paramiko)
source = 'vm-%s-seed.raw' % (vmid)
destination = '%s%s' % (proxmox['images'],
                        instance['hd_seed'].replace('local:', ''))

proxmox_sftp = proxmox_ssh.open_sftp()
proxmox_sftp.put(source, destination)

proxmox_sftp.close()
proxmox_ssh.close()

# set cloud image and seed iso
node.qemu(vmid).config.set(virtio0=instance['hd_root'])
node.qemu(vmid).config.set(virtio1=instance['hd_seed'])

# set boot device
node.qemu(vmid).config.set(bootdisk='virtio0')

# adjust root size
node.qemu(vmid).resize.set(disk='virtio0', size=flavor['root_size'])

# start virtual machine
node.qemu(vmid).status.start.create()
