# Minimal makefile for Sphinx documentation
#

# You can set these variables from the command line.
SPHINXOPTS    =
SPHINXBUILD   = python3 -msphinx
SPHINXPROJ    = hstrat
SOURCEDIR     = .
BUILDDIR      = _build

assets:
	mkdir -p $(BUILDDIR)/html/docs/
	cp -r assets $(BUILDDIR)/html/docs/

readme.rst:
	pandoc ../README.md --wrap=none --from markdown --to rst -s -o readme.rst

# Put it first so that "make" without argument is like "make help".
help:
	@$(SPHINXBUILD) -M help "$(SOURCEDIR)" "$(BUILDDIR)" $(SPHINXOPTS) $(O)

clean:
	rm -rf _autosummary _modules _build readme.rst

.PHONY: assets help Makefile clean

# Catch-all target: route all unknown targets to Sphinx using the new
# "make mode" option.  $(O) is meant as a shortcut for $(SPHINXOPTS).
%: assets Makefile readme.rst
	sphinx-apidoc -o _modules/ ../hstrat
	cp index_stage1.rst index.rst
	@$(SPHINXBUILD) -M $@ "$(SOURCEDIR)" "$(BUILDDIR)" $(SPHINXOPTS) $(O)
	cp index_stage2.rst index.rst
	@$(SPHINXBUILD) -M $@ "$(SOURCEDIR)" "$(BUILDDIR)" $(SPHINXOPTS) $(O)
