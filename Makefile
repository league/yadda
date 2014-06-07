# Makefile ▪ mostly just for the `clean` script
# ©2014 Christopher League <league@contrapunctus.net>

default:

clean:
	./setup.py clean
	sudo rm -rf build dist yadda.egg-info
	find . -type d -name __pycache__ | xargs rm -rf
	find . -name '*~' -or -name '*.pyc' | xargs rm -f
