from proxmoxer import ProxmoxAPI
from subprocess import call
from jinja2 import Environment, FileSystemLoader
from paramiko import SSHClient, WarningPolicy

from settings import proxmox
from settings import instance

proxmox_api = ProxmoxAPI(proxmox['host'], user=proxmox['user'],
                         password=proxmox['password'],
                         verify_ssl=proxmox['verify_ssl'])

node = proxmox_api.nodes(proxmox['node'])

node.qemu.create(vmid=instance['vmid'], name=instance['name'],
                 sockets=instance['sockets'], cores=instance['cores'],
                 balloon=instance['balloon'], memory=instance['memory'],
                 net0=instance['net'])

# compile seed data
env = Environment(loader=FileSystemLoader('templates'))

metadata_j2 = env.get_template('meta-data.j2')
with open('meta-data', 'w') as metadata:
    metadata.write(metadata_j2.render(instance=instance))

userdata_j2 = env.get_template('user-data.j2')
with open('user-data', 'w') as userdata:
    userdata.write(userdata_j2.render(instance=instance))

# generate seed iso
call(['genisoimage', '-output', 'vm-%s-seed.raw' % (instance['vmid']),
     '-volid', 'cidata', '-joliet', '-rock', 'user-data', 'meta-data'])

# mv base image to current vmid (paramiko)
command = 'mkdir -p %s%s && cp -f %s%s %s%s' % (proxmox['images'],
                                                instance['vmid'],
                                                proxmox['images'],
                                                instance['os'],
                                                proxmox['images'],
                                                instance['hd_root'].replace('local:', ''))
proxmox_ssh = SSHClient()
proxmox_ssh.set_missing_host_key_policy(WarningPolicy())
proxmox_ssh.connect(proxmox['host'], username=proxmox['user'].split('@')[0])
stdin, stdout, stderr = proxmox_ssh.exec_command(command)

# sftp seed (paramiko)
source = 'vm-%s-seed.raw' % (instance['vmid'])
destination = '%s%s' % (proxmox['images'],
                        instance['hd_seed'].replace('local:', ''))

proxmox_sftp = proxmox_ssh.open_sftp()
proxmox_sftp.put(source, destination)

proxmox_sftp.close()
proxmox_ssh.close()

# set cloud image and seed iso
node.qemu(instance['vmid']).config.set(virtio0=instance['hd_root'])
node.qemu(instance['vmid']).config.set(virtio1=instance['hd_seed'])

# set boot device
node.qemu(instance['vmid']).config.set(bootdisk='virtio0')

# adjust root size
node.qemu(instance['vmid']).resize.set(disk='virtio0',
                                       size=instance['root_size'])

# start virtual machine
node.qemu(instance['vmid']).status.start.create()
