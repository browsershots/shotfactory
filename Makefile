# Disable the following PyLint messages:
# R0903 - Not enough public methods
# W0142 - Used * or ** magic
# W0232 - Class has no __init__ method
DISABLE="R0903,W0142,W0232"

all : formatting doctest pylint

formatting :
	@echo Checking formatting...
	@find lib scripts -name "*.py" \
	    | grep -v scripts/xmlrpc_help.py \
	    | xargs scripts/shotfactory03_formatting.py

doctest :
	@echo Checking doctest...

pylint :
	@echo Checking pylint...
	@find lib scripts -name "*.py" \
	    | grep -v scripts/xmlrpc_help.py \
	    | xargs pylint --rcfile=conf/pylintrc --disable-msg=$(DISABLE) \
	    || exit 0

install :
	python setup.py install

clean :
	rm -rf build
