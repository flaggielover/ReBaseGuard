PYTHON := .venv/bin/python
PYTEST := .venv/bin/pytest

.PHONY: test diagnostic pregate pregate-audit phase4b-pathwise phase4b-calibrate phase4b-diagnostic phase4b-multicycle phase4b-audit phase4c-analytic phase4c-approximate phase4c-spectral phase4c-interval phase4c-contraction phase4c-budget phase4c-audit proof audit

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

phase4c-analytic:
	$(PYTHON) scripts/run_phase4c_analytic_audit.py

phase4c-approximate:
	$(PYTHON) scripts/run_phase4c_approximate.py

phase4c-spectral:
	$(PYTHON) scripts/run_phase4c_spectral.py

phase4c-interval:
	$(PYTHON) scripts/run_phase4c_interval_prototype.py

phase4c-contraction:
	$(PYTHON) scripts/run_phase4c_contraction_prototype.py

phase4c-budget:
	$(PYTHON) scripts/run_phase4c_error_budget.py

phase4c-audit:
	$(PYTHON) scripts/audit_phase4c.py

proof:
	$(PYTHON) -m rebaseguard_certify.cli prove --certificate proofs/certificate.json

audit:
	$(PYTHON) -m rebaseguard_certify.audit proofs/certificate.json
