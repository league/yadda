# Makefile ▪ mostly just for the `clean` script
# ©2014 Christopher League <league@contrapunctus.net>

default:

%.pdf: %.dot
	dot -Tpdf <$< >$@

%.dot: %.sfood
	sfood-graph <$< >$@

depends.sfood:
	sfood -i yadda >$@

.PHONY: default clean flake

flake:
	pyflakes .

clean:
	./setup.py clean
	sudo rm -rf build dist yadda.egg-info
	find . -type d -name __pycache__ | xargs rm -rf
	find . -name '*~' -or -name '*.pyc' | xargs rm -f
