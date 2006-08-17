# Disable the following PyLint messages:
# R0903 - Not enough public methods
# W0142 - Used * or ** magic
# W0232 - Class has no __init__ method
DISABLE="R0903,W0142,W0232"

all : formatting doctest pylint

formatting :
	@find lib -name "*.py" > check-formatting
	@find scripts -type f -perm /a+x | grep -v xmlrpc >> check-formatting
	@echo "Checking formatting on "`wc -l < check-formatting`" files..."
	@xargs -a check-formatting devtools/formatting.py

doctest :
	@echo lib/image/hashmatch.py > check-doctest
	@echo "Running doctest on "`wc -l < check-doctest`" files..."
	@xargs -a check-doctest -n 1 python

pylint :
	@find lib scripts -name "*.py" > check-pylint
	@find scripts -type f -perm /a+x >> check-pylint
	@echo devtools/formatting.py >> check-pylint
	@echo "Running PyLint on "`wc -l < check-pylint`" files..."
	@xargs -a check-pylint pylint \
		--rcfile=devtools/pylintrc --disable-msg=$(DISABLE)

install :
	python setup.py install

clean :
	rm -rf build dist *.ppm *.pbm

