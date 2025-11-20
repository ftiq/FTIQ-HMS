# -*- coding: utf-8 -*-
# Part of AlmightyCS. See LICENSE file for full copyright and licensing details.

from . import controllers
from . import models
from . import wizard

def create_lab_test_checkbox_view(env):
    env['acs.lab.test']._update_lab_test_groups_view()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: