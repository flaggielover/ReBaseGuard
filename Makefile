PYTHON := .venv/bin/python
PYTEST := .venv/bin/pytest

.PHONY: test diagnostic pregate pregate-audit phase4b-pathwise phase4b-calibrate phase4b-diagnostic phase4b-multicycle phase4b-audit proof audit

test:
	$(PYTEST) -q

diagnostic:
	$(PYTHON) scripts/run_diagnostics.py

pregate:
	$(PYTHON) scripts/run_phase4_pregate_diagnostics.py --samples 1000000

pregate-audit:
	$(PYTHON) -m rebaseguard_certify.pregate_audit

phase4b-pathwise:
	$(PYTHON) scripts/run_phase4b_pathwise.py

phase4b-calibrate:
	$(PYTHON) scripts/calibrate_phase4b_sr.py

phase4b-diagnostic:
	$(PYTHON) scripts/run_phase4b_diagnostics.py --samples 1000000

phase4b-multicycle:
	$(PYTHON) scripts/run_phase4b_multicycle.py

phase4b-audit:
	$(PYTHON) scripts/audit_phase4b.py

proof:
	$(PYTHON) -m rebaseguard_certify.cli prove --certificate proofs/certificate.json

audit:
	$(PYTHON) -m rebaseguard_certify.audit proofs/certificate.json
