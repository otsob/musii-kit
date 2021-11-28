#   -*- coding: utf-8 -*-
from pybuilder.core import use_plugin, init, task

use_plugin("python.core")
use_plugin("python.unittest")
use_plugin("python.flake8")
use_plugin("python.distutils")


name = "musii_kit"
default_task = "publish"


@init
def set_properties(project):
    project.set_property("dir_source_main_python", "src/musii_kit")
    project.set_property("dir_source_unittest_python", "src/test")
