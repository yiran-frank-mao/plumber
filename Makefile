LATEX ?= pdflatex
LATEXFLAGS = -interaction=nonstopmode -halt-on-error
export TEXINPUTS := $(CURDIR)//:$(TEXINPUTS)

.PHONY: all doc examples test clean

all: doc examples

doc: plumber-doc.pdf

examples: examples/frobenius.pdf

plumber-doc.pdf: plumber-doc.tex plumber.sty
	$(LATEX) $(LATEXFLAGS) $<
	$(LATEX) $(LATEXFLAGS) $<

examples/frobenius.pdf: examples/frobenius.tex plumber.sty
	cd examples && $(LATEX) $(LATEXFLAGS) frobenius.tex

test:
	python3 tests/check_reduce.py 1
	python3 tests/check_reduce.py 2
	python3 tests/check_standalone.py

clean:
	rm -f *.aux *.log *.out *.toc examples/*.aux examples/*.log tests/*.aux tests/*.log
