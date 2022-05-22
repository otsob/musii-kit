#   -*- coding: utf-8 -*-
from pybuilder.core import use_plugin, init

use_plugin("python.core")
use_plugin("python.unittest")
use_plugin("python.flake8")
use_plugin("python.distutils")

name = "musii_kit"
default_task = "publish"
description = "Musicology utilities"
long_description = "A collection of Python utilities for computational musicology."


@init
def set_properties(project):
    project.set_property("dir_source_main_python", "src/main")
    project.set_property("dir_source_unittest_python", "src/test")
