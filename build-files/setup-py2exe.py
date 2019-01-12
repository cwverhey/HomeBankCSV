"""

Usage:
    python setup.py py2exe
"""

from distutils.core import setup
import py2exe, sys, os

sys.argv.append('py2exe')

setup(
    author="Caspar Verhey",
    author_email="caspar@verhey.net",
    license="MIT",
    url="https://github.com/cwverhey/HomeBankCSV",
    windows=[{'script':'HomeBankCSV.py', "icon_resources":[(1,"icon.ico")]}],
    data_files=[],
    options = {'py2exe':
               {'bundle_files': 2,
                'compressed': True,
                excludes=['pyreadline', 'difflib', 'doctest', 'locale', 'optparse', 'pickle', 'calendar']
                }
            },
    zipfile = None,
)

# tcl\tk*\images
# tcl\tk*\demos
# tcl\dde*
# tcl\reg*
#? tcl\tdbc*
# tcl\tdbcodbc*
# tcl\tdbcsqlite*
# tcl\sqlite*
# tcl\tdbcmysql*
# tcl\tdbcpostgres*
# tcl\thread*
# tcl\tix*\demos
# tcl\tcl*\tzdata
# encoding
# msgs
