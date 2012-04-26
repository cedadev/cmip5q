#
# Metafor Project
#
# @author P J Kershaw 08/07/09
#
# Make all eggs
#
# @copyright: (C) 2009 STFC
#
# @license: BSD - see LICENSE file
#
# $Id$
EGG_DIRS=cmip5q

# Override on the command line for alternative path
PYTHON=python

egg:
	@${PYTHON} setup.py bdist_egg

clean:
	rm -f dist/*.egg
	rm -rf *.egg-info
	rm -rf build

replace: clean egg

# Convenient alias
force: replace

NDG_EGG_DIST_USER=
NDG_EGG_DIST_HOST=
NDG_EGG_DIST_DIR=

install_egg: egg
	scp dist/*.egg ${NDG_EGG_DIST_USER}@${NDG_EGG_DIST_HOST}:${NDG_EGG_DIST_DIR}