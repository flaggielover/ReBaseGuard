PYTHON := .venv/bin/python
PYTEST := .venv/bin/pytest

.PHONY: test diagnostic pregate pregate-audit proof audit

test:
	$(PYTEST) -q

diagnostic:
	$(PYTHON) scripts/run_diagnostics.py

pregate:
	$(PYTHON) scripts/run_phase4_pregate_diagnostics.py --samples 1000000

pregate-audit:
	$(PYTHON) -m rebaseguard_certify.pregate_audit

proof:
	$(PYTHON) -m rebaseguard_certify.cli prove --certificate proofs/certificate.json

audit:
	$(PYTHON) -m rebaseguard_certify.audit proofs/certificate.json
