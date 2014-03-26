#! /usr/bin/env python

import argparse
from subprocess import call
from importlib import import_module

from proxmoxer import ProxmoxAPI
from jinja2 import Environment, FileSystemLoader
from paramiko import SSHClient, WarningPolicy

from settings.settings import proxmox
from settings.instance import instance


def instance_customize(instance, vmid, name, flavor_type):
    # retrieve flavour
    flavor_module = import_module('flavors.%s' % (flavor_type))
    flavor = flavor_module.flavor

    # configure instance custom details
    instance['hd_root'] = instance['hd_root'] % (vmid, vmid)
    instance['lvm_root'] = instance['lvm_root'] % (vmid)
    instance['hd_seed'] = instance['hd_seed'] % (vmid, vmid)

    for ifs in instance['ifs']:
        ifs['address'] = ifs['address'] % (vmid)

    instance['vmid'] = vmid
    instance['name'] = name

    return instance, flavor


def get_proxmox_ssh(proxmox):
    proxmox_ssh = SSHClient()
    proxmox_ssh.set_missing_host_key_policy(WarningPolicy())
    proxmox_ssh.connect(proxmox['host'],
                        username=proxmox['user'].split('@')[0])

    return proxmox_ssh


def seed(vmid, instance, proxmox):
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

    # sftp seed (paramiko)
    source = 'vm-%s-seed.raw' % (vmid)
    destination = '%s%s' % (proxmox['images'],
                            instance['hd_seed'].replace('local:', ''))

    proxmox_ssh = get_proxmox_ssh(proxmox)

    command = 'mkdir -p %s%s' % (proxmox['images'], vmid)

    stdin, stdout, stderr = proxmox_ssh.exec_command(command)

    proxmox_sftp = proxmox_ssh.open_sftp()
    proxmox_sftp.put(source, destination)

    proxmox_sftp.close()
    proxmox_ssh.close()


def dir_volume(vmid, instance, proxmox):
    # mv base image to current vmid (paramiko)
    command = 'cp -f %s%s %s%s' % (proxmox['images'],
                                   instance['os'],
                                   proxmox['images'],
                                   instance['hd_root'].replace('local:', ''))
    proxmox_ssh = get_proxmox_ssh(proxmox)
    stdin, stdout, stderr = proxmox_ssh.exec_command(command)
    proxmox_ssh.close()


def lvm_volume(vmid, instance, proxmox):
    
    command = 'qemu-img convert -O raw %s%s %s' % (proxmox['images'],
                                                   instance['os'],
                                                   instance['lvm_root'])

    proxmox_ssh = get_proxmox_ssh(proxmox)
    stdin, stdout, stderr = proxmox_ssh.exec_command(command)
    proxmox_ssh.close()


if __name__ == "__main__":

    # configuring and reading arguments
    parser = argparse.ArgumentParser(description='Create a proxmox kvm and \
                                     cloudinit it.')

    parser.add_argument('--vmid', '-v', type=int, help='Virtual machine id',
                        required=True)
    parser.add_argument('--name', '-n', type=str,
                        help='Virtual machine name/hostname',
                        required=True)
    parser.add_argument('--flavor', '-f', type=str,
                        default='small', choices=['micro', 'small'],
                        help='Virtual machine flavor')
    parser.add_argument('--storage', '-s', type=str,
                        default='dir', choices=['dir', 'lvm'],
                        help='Virtual machine storage backend')

    args = parser.parse_args()

    vmid = str(args.vmid)
    name = args.name
    flavor_type = args.flavor
    storage_type = args.storage

    # customize flavor
    instance, flavor = instance_customize(instance, vmid, name, flavor_type)

    # proxmoxer initialize
    proxmox_api = ProxmoxAPI(proxmox['host'], user=proxmox['user'],
                             password=proxmox['password'],
                             verify_ssl=proxmox['verify_ssl'])

    node = proxmox_api.nodes(proxmox['node'])

    # create kvm machine
    node.qemu.create(vmid=vmid, name=name, sockets=flavor['sockets'],
                     cores=flavor['cores'], balloon=flavor['balloon'],
                     memory=flavor['memory'], net0=instance['net'])

    # seeding
    seed(vmid, instance, proxmox)

    # set seed iso
    node.qemu(vmid).config.set(virtio1=instance['hd_seed'])

    # create root volume
    if storage_type == 'dir':
        dir_volume(vmid, instance, proxmox)
        # set root image
        node.qemu(vmid).config.set(virtio0=instance['hd_root'])
        # adjust root size
        node.qemu(vmid).resize.set(disk='virtio0', size=flavor['root_size'])
    elif storage_type == 'lvm':
        # initialize lvm volume
        node.qemu(vmid).config.set(virtio0='%s:%s' % ('vg0',
                                   flavor['root_size'].replace('G', '')))
        lvm_volume(vmid, instance, proxmox)

    # set boot device
    node.qemu(vmid).config.set(bootdisk='virtio0')

    # start virtual machine
    node.qemu(vmid).status.start.create()
