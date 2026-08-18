PYTHON := .venv/bin/python
PYTEST := .venv/bin/pytest

.PHONY: test diagnostic proof audit

test:
	$(PYTEST) -q

diagnostic:
	$(PYTHON) scripts/run_diagnostics.py

proof:
	$(PYTHON) -m rebaseguard_certify.cli prove --certificate proofs/certificate.json

audit:
	$(PYTHON) -m rebaseguard_certify.audit proofs/certificate.json

