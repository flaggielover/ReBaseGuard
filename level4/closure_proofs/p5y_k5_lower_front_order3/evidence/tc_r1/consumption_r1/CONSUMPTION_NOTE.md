# Consumption note (theorem-TC successor)

Two consumptions from a fresh clone at the seal commit `bc4235d0` (`/root/work/k5lf-consume` on rebaseguard-vultr-02),
outputs written outside the checkout: byte-identical, sha256 `1fa8d8de…`.

**Interpreter setting.** The adopted, frozen consumption adapter serialises exact rationals with `str(Fraction)`
(`consumption_adapter.row_json`). CPython 3.12 refuses an int→str conversion beyond 4300 digits, and the theorem-TC
enclosures carry larger exact numerators than the adopted Perron ones, so the first invocation raised
`ValueError: Exceeds the limit (4300 digits)` BEFORE writing any output. The consumption was repeated with
`PYTHONINTMAXSTRDIGITS=0` in the environment. This changes no frozen file, no computed value and no comparison: it only
lifts CPython's decimal-printing guard. Disclosed here for the adjudication.
