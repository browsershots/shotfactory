pep8 :
	pep8.py --filename=*.py --repeat .

pylint :
	pylint shotfactory04 \
	| grep -v "image/png\.py:" \
	| grep -v "Method could be a function" \
	| grep -v "defined outside __init__" \
	| grep -v "Too many public methods"

docstrings :
	-pylint shotserver04 \
	| grep "docstring"

doctest :
	grep -rl --include "*.py" "doctest.testmod()" . | xargs -n1 python

headers :
	find -name "*.py" \
	| xargs header.py shotfactory04/__init__.py

properties :
	find -name "*.py" | xargs svn propset svn:keywords "Rev Date Author"
	find -name "*.py" | xargs svn propset svn:eol-style native

documentation :
	wget -O - http://trac.browsershots.org/wiki/InstallFactory?format=txt \
	| sed s/InstallFactoryLinux/INSTALL.LINUX/ \
	| sed s/InstallFactoryWindows/INSTALL.WIN/ \
	| sed s/InstallFactoryMac/INSTALL.MAC/ \
	| fold -s -w 76 > INSTALL
	wget -O - http://trac.browsershots.org/wiki/InstallFactoryLinux?format=txt \
	| sed s/InstallFactory/INSTALL/ \
	| fold -s -w 76 > INSTALL.LINUX
	wget -O - http://trac.browsershots.org/wiki/InstallFactoryWindows?format=txt \
	| sed s/InstallFactory/INSTALL/ \
	| fold -s -w 76 > INSTALL.WIN
	wget -O - http://trac.browsershots.org/wiki/InstallFactoryMac?format=txt \
	| sed s/InstallFactory/INSTALL/ \
	| fold -s -w 76 > INSTALL.MAC
	wget -O - http://trac.browsershots.org/wiki/FrequentlyAskedQuestions?format=txt | fold -s -w 76 > FAQ
	wget -O - http://trac.browsershots.org/wiki/Authors?format=txt | fold -s -w 76 > AUTHORS
