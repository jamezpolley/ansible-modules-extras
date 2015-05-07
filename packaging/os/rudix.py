#!/usr/bin/python
# -*- coding: utf-8 -*-

# (c) 2015, James Polley <jp@jamezpolley.com>
# Based on macports (Jimmy Tang <jcftang@gmail.com), okpg (Patrick
# Pelletier <pp.pelletier@gmail.com>), pacman (Afterburn) and pkgin
# (Shaun Zinck) modules
#
# This module is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This software is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this software.  If not, see <http://www.gnu.org/licenses/>.

DOCUMENTATION = '''
---
module: rudix
author: James Polley
short_description: Package manager for Rudix
description:
    - Manages Rudix (http://rudix.org) packages
version_added: "2.0"
options:
    name:
        description:
            - name(s) of package(s) to install/remove
        required: true
    state:
        description:
            - state of the package
        choices: [ 'present', 'absent' ]
        required: false
        default: present
notes:  []
'''
EXAMPLES = '''
- rudix: name=foo state=present
- rudix: name=foo state=absent
- rudix: name=foo,bar state=present
'''

import pipes

def query_package(module, rudix_path, name):
    """ Returns whether a package is installed or not. """

    rc, out, err = module.run_command("%s --list | grep -q ^.*%s" % (pipes.quote(rudix_path), pipes.quote(name)), use_unsafe_shell=True)
    if rc == 0:
        return True
    else:
        return False


def remove_packages(module, rudix_path, packages):
    """ Uninstalls one or more packages if installed. """

    remove_c = 0
    # Using a for loop incase of error, we can report the package that failed
    for package in packages:
        # Query the package first, to see if we even need to remove
        if not query_package(module, rudix_path, package):
            continue

        rc, out, err = module.run_command("%s --remove %s" % (rudix_path, package))

        if query_package(module, rudix_path, package):
            module.fail_json(msg="failed to remove %s: %s" % (package, out))

        remove_c += 1

    if remove_c > 0:

        module.exit_json(changed=True, msg="removed %s package(s)" % remove_c)

    module.exit_json(changed=False, msg="package(s) already absent")


def install_packages(module, rudix_path, packages):
    """ Installs one or more packages if not already installed. """

    install_c = 0

    for package in packages:
        if query_package(module, rudix_path, package):
            continue

        rc, out, err = module.run_command("%s --install %s" % (rudix_path, package))

        if not query_package(module, rudix_path, package):
            module.fail_json(msg="failed to install %s: %s" % (package, out))

        install_c += 1

    if install_c > 0:
        module.exit_json(changed=True, msg="installed %s package(s)" % (install_c))

    module.exit_json(changed=False, msg="package(s) already present")


def main():
    module = AnsibleModule(
        argument_spec = dict(
            name = dict(aliases=["pkg"], required=True, type='list'),
            state = dict(default="present", choices=["present", "installed", "absent", "removed"]),
        )
    )

    rudix_path = module.get_bin_path('rudix', True, ['/usr/local/bin'])

    p = module.params

    pkgs = p["name"].split(",")

    if p["state"] in ["present", "installed"]:
        install_packages(module, rudix_path, pkgs)

    elif p["state"] in ["absent", "removed"]:
        remove_packages(module, rudix_path, pkgs)

# import module snippets
from ansible.module_utils.basic import *

main()
