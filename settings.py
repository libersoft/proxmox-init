# proxmox settings
proxmox = {}

proxmox['host'] = 'proxmox'
proxmox['user'] = 'root@pam'
proxmox['password'] = '***REMOVED***'
proxmox['images'] = '/var/lib/vz/images/'
proxmox['verify_ssl'] = False
proxmox['node'] = 'proxmox'

# instance data
instance = {}

instance['vmid'] = '108'
instance['name'] = 'trac'

instance['os'] = 'trusty-server-cloudimg-amd64-disk1.qcow2'
instance['sockets'] = '1'
instance['cores'] = '1'
instance['balloon'] = '0'
instance['memory'] = '512'
instance['net'] = 'virtio,bridge=vmbr0'
instance['root_size'] = '20G'
instance['hd_root'] = 'local:%s/vm-%s-disk-1.qcow2' % (instance['vmid'],
                                                       instance['vmid'])
instance['hd_seed'] = 'local:%s/vm-%s-seed.raw' % (instance['vmid'],
                                                   instance['vmid'])

instance['locale'] = 'en_US.UTF-8'
instance['timezone'] = 'Europe/Rome'
instance['kb_layout'] = 'it'
instance['resize_rootfs'] = 'True'

instance['ifs'] = []
instance['ifs'].append({})
instance['ifs'][0]['name'] = 'eth0'
instance['ifs'][0]['type'] = 'static'
instance['ifs'][0]['address'] = '192.168.42.%s' % (instance['vmid'])
instance['ifs'][0]['network'] = '192.168.42.0'
instance['ifs'][0]['netmask'] = '255.255.255.0'
instance['ifs'][0]['broadcast'] = '192.168.42.255'
instance['ifs'][0]['gateway'] = '192.168.42.1'
instance['ifs'][0]['dnss'] = []
instance['ifs'][0]['dnss'].append('192.168.42.1')

instance['users'] = []
instance['users'].append({})
instance['users'][0]['name'] = 'libersoft'
instance['users'][0]['groups'] = ['adm', 'users']
instance['users'][0]['shell'] = '/bin/bash'
instance['users'][0]['ssh_keys'] = ['ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAABAQC/CnT9nN/acqX13EPMDKUFuKng1rZ3Jc47BiGmBg+ESFGQxltzG48kdHp7FievbtLGhP1igG45XNINkS1ySBGAjG/QhlGgUewS2OXGmlFS/GvkcFDiSyBjL2Mg0xjnPSa29P9F4zlp1txInZDhsAAq/fVVWMTS8rJTc+D8M5tY0eK41f9blsImHvzhCcNZNAzzxi5iYbt0ayObp0q3OcODRBxivmSO/h52sULbF/T+CLMwUacQhOQl3SMuxrL048vGJGlS6ABI9feY3q8bVnc0e1c9pKWEbQ4x8/ScO1r2iD9Wn5VG60aBrXciFL12JBok0A17wx7jmWG9BglywW7J lg@thule',
                                    'ssh-rsa AAAAB3NzaC1yc2EAAAABIwAAAQEAlztGLOE+8OMs30KNohtMe8QYT3aqhUoleGMSNWmoh3cM1TSdKPzpmhKDu/rZkKl26ax1TUX0VO3nGvAvjjVOs6y6vJtOJcw8fSCJMt7yUHTOx1zHhvnm8Eyc4DN8e+lyNvijA4l6GfpPNOEwC3DvZ/TGZeHqjFJz7Z+5zXueCi0yKQwn3KS6E4CeBe5g/yMJOn7iI8WXPV2Wu9PB2aVzx+87VTnmk6Rrm0vJUzXO3G17phEX+yiMkVQ9ihYnFKbnPe2du9oEkVs8qy7UeIxtwraTdlnuW2pzQI19QlFwvicL2wrq92VihNddbZ5vmMYR28ie4NND+7APypBX5JyYaw== malte@maltebook',
                                    'ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAABAQCuE2M2oBLgLIxIAZFWoJUGs5vqKt6VYKe+6xYii9WdWUuh30CIdleu1yPRXa81feotHcfYiXeBxxlPrRBLw1vF9g/u4l8ezPSDqJ72gfWQVJ9IgSF9PTUZQxnNQmN3fW9bSu7J21EoMFT/LbDwXlm4zGFyhjWkgLHG8mLxRPgPbsY4Nx+rLL4YCz/HUuOBnOu1iVb9rWhzFWX0jewZmGSnKI+jBcSK1IvTzXNvy3hAlc6Aq9siEmFGFqsHd0r1fvn/CnDB4BQgmTnFdBfMTx5ISIids1JqC8UidZWaAKSijNuFL7wQVBnX0o9AnjHXjd2ph+wymX4eM4v6DcHP6C+x lappone@khorne']

instance['password_expire'] = 'False'
instance['ssh_pass_auth'] = 'True'
instance['apt_update'] = 'False'
instance['apt_upgrade'] = 'False'
instance['packages'] = []

instance['runcmds'] = []
