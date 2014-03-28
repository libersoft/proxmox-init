# proxmox-init

Python script to deploy GNU/Linux cloud images (tested with [Ubuntu](http://cloud-images.ubuntu.com/)), cloud-style, on Proxmox KVM.
Based on Proxmox API Python (proxmoxer) and cloud-init.
Hardware templating of KVM instances is possible by flavors configuration file (inspired by OpenStack flavors).
Only local storage support, both directory and LVM Group.
Cloud-init is linked to Qemu-KVM machines by [NoCloud datasource] (http://cloudinit.readthedocs.org/en/latest/topics/datasources.html#no-cloud).

## Installation

    $ git clone https://github.com/libersoft/proxmox-init.git proxmox-init
    $ cd proxmox-init
    $ pip install requirements.txt

You need also to install `genisoimage`, needed to create the cloudinit seed datasource.

## Configuration

You have to copy proxmox settings from `settings/settings.py.dist` to `settings/settings.py` and edit it to reflect your current proxmox configuration.

You can add and modify your hardware flavors in `flavors/`.
In this case you have also to update choices for `--flavor` cmdline switch in the main script.

You have to copy instance configuration from `settings/instance.py.dist` to `settings/instance.py` and edit it to reflect your need.

Current format for configuration is quite rough and not very flexible.

The script assumes you have your ssh key in the authorized_keys of the proxmox node,
for the user specified in the settings file.

## Usage
    usage: proxvm-deploy.py [-h] --vmid VMID --name NAME [--flavor {micro,small}]
                        [--storage {dir,lvm}]

    Create a proxmox kvm and cloudinit it.

    optional arguments:
        -h, --help            show this help message and exit
        --vmid VMID, -v VMID  Virtual machine id
        --name NAME, -n NAME  Virtual machine name/hostname
        --flavor {micro,small}, -f {micro,small}
                        Virtual machine flavor
        --storage {dir,lvm}, -s {dir,lvm}
                        Virtual machine storage backend

## Status

Rough working proof of concept.

## Possible Improvements

*   Puppet and chef section in cloudinit template.
*   Ansible-pull launch on instance customization.
*   Support to proxmox remote storage.
*   Settings refactoring, especially network interfaces
*   Extend cmdline arguments to choose base os image, proxmox node, proxmox host anb other.
*   Code reorganization

## Random Ideas and maybe

*   Proxmox KVM Ansible module ?

## License

[Gnu General Public License 3.0](https://www.gnu.org/licenses/gpl.html)

## Credits
*   [Proxmoxer](https://github.com/swayf/proxmoxer)
*   [Cloud-init](http://cloudinit.readthedocs.org/en/latest/index.html)
*   [Proxmox API](http://pve.proxmox.com/pve2-api-doc/)
*   [Local Ubuntu vm provisioning with cloud-init](http://qa.ubuntu.com/2012/06/19/local-ubuntu-vm-provisioning-with-cloud-init/)
*   [Copying an image to a physical device](https://en.wikibooks.org/wiki/QEMU/Images#Copying_an_image_to_a_physical_device)
*   [API-Create-KVM-with-logical-Volume](http://forum.proxmox.com/threads/12059-API-Create-KVM-with-Logical-Volume)
