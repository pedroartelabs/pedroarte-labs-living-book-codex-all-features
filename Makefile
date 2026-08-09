PYTHON ?= python
BOOK ?= books/antes-que-as-criancas-crescam
SLUG ?= antes-que-as-criancas-crescam

validate-engine:
	$(PYTHON) engine/scripts/livingbook.py validate-engine

validate-book:
	$(PYTHON) engine/scripts/livingbook.py validate-book --book $(BOOK)

compose:
	$(PYTHON) engine/scripts/livingbook.py compose --book $(BOOK)

smoke:
	$(PYTHON) engine/scripts/livingbook.py smoke-test --runtime runtime/$(SLUG)

ready:
	$(PYTHON) engine/scripts/livingbook.py ready --runtime runtime/$(SLUG)
