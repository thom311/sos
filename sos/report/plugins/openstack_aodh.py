# Copyright (C) 2017 Red Hat, Inc., Sachin Patil <psachin@redhat.com>
# Copyright (C) 2017 Red Hat, Inc., Martin Schuppert <mschuppert@redhat.com>

# This file is part of the sos project: https://github.com/sosreport/sos
#
# This copyrighted material is made available to anyone wishing to use,
# modify, copy, or redistribute it subject to the terms and conditions of
# version 2 of the GNU General Public License.
#
# See the LICENSE file in the source distribution for further information.

import os
from sos.report.plugins import Plugin, RedHatPlugin, DebianPlugin, UbuntuPlugin


class OpenStackAodh(Plugin):

    short_desc = 'OpenStack Alarm service'
    plugin_name = "openstack_aodh"
    profiles = ('openstack', 'openstack_controller')

    var_puppet_gen = "/var/lib/config-data/puppet-generated/aodh"

    def setup(self):
        self.add_copy_spec([
            "/etc/aodh/",
            self.var_puppet_gen + "/etc/aodh/*",
            self.var_puppet_gen + "/etc/httpd/conf/*",
            self.var_puppet_gen + "/etc/httpd/conf.d/*",
            self.var_puppet_gen + "/etc/httpd/conf.modules.d/wsgi.conf",
            self.var_puppet_gen + "/etc/my.cnf.d/tripleo.cnf"
        ])

        if self.get_option("all_logs"):
            self.add_copy_spec([
                "/var/log/aodh/*",
                "/var/log/httpd/aodh*",
            ])
        else:
            self.add_copy_spec([
                "/var/log/aodh/*.log",
                "/var/log/httpd/aodh*.log",
            ])

        vars_all = [p in os.environ for p in [
            'OS_USERNAME', 'OS_PASSWORD', 'OS_AUTH_TYPE'
        ]]

        vars_any = [p in os.environ for p in [
            'OS_TENANT_NAME', 'OS_PROJECT_NAME'
        ]]

        if not (all(vars_all) and any(vars_any)):
            self.soslog.warning("Not all environment variables set. Source "
                                "the environment file for the user intended "
                                "to connect to the OpenStack environment.")
        else:
            self.add_cmd_output([
                "aodh --version",
                "aodh capabilities list",
                "aodh alarm list"
            ])

    def postproc(self):
        self.do_file_sub(
            "/etc/aodh/aodh.conf",
            r"(password[\t\ ]*=[\t\ ]*)(.+)",
            r"\1********"
        )

        self.do_file_sub(
            "/etc/aodh/aodh.conf",
            r"(rabbit_password[\t\ ]*=[\t\ ]*)(.+)",
            r"\1********",
        )

        self.do_file_sub(
            self.var_puppet_gen + "/etc/aodh/aodh.conf",
            r"(password[\t\ ]*=[\t\ ]*)(.+)",
            r"\1********"
        )

        self.do_file_sub(
            self.var_puppet_gen + "/etc/aodh/aodh.conf",
            r"(rabbit_password[\t\ ]*=[\t\ ]*)(.+)",
            r"\1********",
        )


class DebianOpenStackAodh(OpenStackAodh, DebianPlugin, UbuntuPlugin):

    packages = (
        'aodh-api',
        'aodh-evaluator',
        'aodh-notifier',
        'aodh-listener',
        'python-aodhclient'
    )


class RedHatOpenStackAodh(OpenStackAodh, RedHatPlugin):

    packages = ('openstack-selinux',)

    def setup(self):
        super(RedHatOpenStackAodh, self).setup()
        if self.get_option("all_logs"):
            self.add_copy_spec([
                "/var/log/containers/httpd/aodh-api/*",
                "/var/log/containers/aodh/*"
            ])
        else:
            self.add_copy_spec([
                "/var/log/containers/httpd/aodh-api/*.log",
                "/var/log/containers/aodh/*.log"
            ])

# vim: set et ts=4 sw=4 :
