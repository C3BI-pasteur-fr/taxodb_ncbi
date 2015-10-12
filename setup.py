#!/usr/bin/env python
# -*- coding: utf-8 -*-
from distutils.core import setup
from distutils.command.install_egg_info import install_egg_info
from distutils.versionpredicate import VersionPredicate
from distutils.command.build import build
import sys


class nohup_egg_info(install_egg_info):
    def run(self):
        # there is nothing to install in sites-package
        # so I don't put any eggs in it
        pass


class check_and_build(build):
    def run(self):
        chk = True
        for req in require_pyt:
            chk &= self.chkpython(req)
        for req in require_mod:
            chk &= self.chkmodule(req)
        if not chk:
            sys.exit(1)
        build.run(self)

    def chkpython(self, req):
        chk = VersionPredicate(req)
        ver = '.'.join([str(v) for v in sys.version_info[:2]])
        if not chk.satisfied_by(ver):
            print >> sys.stderr, "Invalid python version, expected %s" % req
            return False
        return True

    def chkmodule(self, req):
        chk = VersionPredicate(req)
        try:
            mod = __import__(chk.name)
        except:
            print >> sys.stderr, "Missing mandatory %s python module" % chk.name
            return False
        for v in ['__version__', 'version']:
            ver = getattr(mod, v, None)
            break
        try:
            if ver and not chk.satisfied_by(ver):
                print >> sys.stderr, "Invalid module version, expected %s" % req
                return False
        except:
            pass
        return True

require_pyt = ['python (>=2.7, <3.0)']
require_mod = ['bsddb']


setup(name = "taxodb_ncbi",
      version="2.0",
      author="Corinne Maufrais",
      author_email="corinne.maufrais@pasteur.fr",
      license='GPLv3',
      description = ("""taxodb.py is a simple python program that it uses to format the NCBI Taxonomy Database (http://www.ncbi.nlm.nih.gov/taxonomy).  
It requires the bsddb python library (https://docs.python.org/2/library/bsddb.html) and Berkeley DB library (http://www.oracle.com/database/berkeley-db) to work."""),
      cmdclass={'install_egg_info': nohup_egg_info},
      package_dir={'': 'src'},
      install_requires = ['bsddb >=6.1.0',],
) 
