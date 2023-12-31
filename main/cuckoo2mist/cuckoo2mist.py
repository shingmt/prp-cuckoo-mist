#!/usr/bin/env python
# encoding: utf-8
"""
cuckoo2mist.py

Created by Dr. Philipp Trinius on 2013-11-10.
Copyright (c) 2013 pi-one.net .
Modified and updated by Navein Chanderan & Chang Si Ju on 2017-11-01.

This program is free software; you can redistribute it and/or modify it
under the terms of the GNU General Public License as published by the
Free Software Foundation; either version 2 of the License, or (at your option)
any later version.

This program is distributed in the hope that it will be useful, but
WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY
or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for
more details.

You should have received a copy of the GNU General Public License along with
this program; if not, see <http://www.gnu.org/licenses/>
"""

from __future__ import print_function

__author__ = "philipp trinius, navein chanderan, chang si ju"
__version__ = "0.4"

import os
import sys
import time
import argparse
import logging
import xml.etree.ElementTree as ET
from multiprocessing import cpu_count
from pymp import Parallel

from main.cuckoo2mist.class_mist import MIST

num_cpus = cpu_count()

CUCKOO2MIST_DIR = os.path.dirname(os.path.abspath(__file__))
conf_dir = os.path.join(CUCKOO2MIST_DIR, "conf")
input_dir = os.path.join(os.path.dirname(CUCKOO2MIST_DIR), "reports")
output_dir = os.path.join(os.path.dirname(CUCKOO2MIST_DIR), "reports")
print('conf_dir', conf_dir)

log = logging.getLogger()

def read_configuration(confdir=""):
    global conf_dir
    if confdir:
        conf_dir = confdir

    apis = ET.ElementTree()
    apis.parse(os.path.join(conf_dir, "cuckoo_elements2mist.xml"))

    default_values = ET.ElementTree()
    default_values.parse(os.path.join(conf_dir, "cuckoo_types2mist.xml"))

    return (apis, default_values)

def init_logging():
    log.setLevel(logging.DEBUG)
    formatter = logging.Formatter('%(levelname)s:%(message)s')

    # ch = logging.StreamHandler()
    # ch.setFormatter(formatter)
    # ch.setLevel(logging.INFO)
    # log.addHandler(ch)

    fh = logging.FileHandler(
             os.path.join(os.path.expanduser("~"), "cuckoo2mist.log"))
    fh.setFormatter(formatter)
    fh.setLevel(logging.INFO)
    log.addHandler(fh)

def print_(text):
    print('\r\x1b[K', end='')
    print('{}'.format(text), end='')
    sys.stdout.flush()

def _generate_mist_report(input_file, output_file, apis, default_values, log,
                          show_progress=True):
    if show_progress:
        print('Converting {:*>58s}'.format(input_file[-55:]))
    mist = MIST(input_file, apis=apis, default_values=default_values)
    # print('[_generate_mist_report] input_file', input_file)
    if mist.convert():
        mist.write(output_file)
    if len(mist.errormsg) > 0:
        log.warning(mist.errormsg)

def generate_mist_reports(files, outputdir, apis, default_values, logger=log,
                          show_progress=False):
    """Convert Cuckoo behaviour reports to MIST reports in multiple threads."""
    with Parallel(num_cpus) as p:
        for i in p.range(len(files)):
            fname_wext = os.path.basename(files[i])
            (fname, fext) = os.path.splitext(fname_wext)
            output_file = os.path.join(outputdir, fname + ".mist")
            # print('[generate_mist_reports] output_file', output_file)
            _generate_mist_report(files[i], output_file, apis, default_values,
                                  logger, show_progress)


def main():
    global conf_dir
    global input_dir
    global output_dir

    parser = argparse.ArgumentParser()
    parser.add_argument("-c", "--confdir", type=str, default="",
                        help="directory of configuration files")
    parser.add_argument("-i", "--inputdir", type=str, default="",
                        help="directory of Cuckoo behaviour reports")
    parser.add_argument("-o", "--outputdir", type=str, default="",
                        help="directory where MIST reports to be saved")
    args = parser.parse_args()

    init_logging()

    if args.confdir:
        conf_dir = args.confdir
    if args.inputdir:
        input_dir = args.inputdir
    if args.outputdir:
        output_dir = args.outputdir

    if not os.path.exists(conf_dir):
        log.warning("Configuration directory not valid")
        return

    files = []

    print('[main] input_dir', input_dir, os.path.exists(input_dir))
    if os.path.exists(input_dir):
        for file in os.listdir(input_dir):
            path = os.path.join(input_dir, file)
            if path.endswith(".json") or path.endswith(".gz"):
                files.append(path)
    else:
        log.warning("Input directory not valid")
        return

    if not os.path.exists(output_dir):
        log.warning("Output directory not valid")
        return

    (apis, default_values) = read_configuration(conf_dir)

    generate_mist_reports(files,
                          outputdir=output_dir,
                          apis=apis,
                          default_values=default_values,
                          logger=log)
