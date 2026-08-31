"""Level-4 Priority 4: general location-family generalization of the closed
ReBaseGuard derivative and stability mechanism.

The package is deliberately small and separable:

``families``    innovation densities with their analytic location scores;
``detectors``   the frozen CUSUM and SR recursions, applied verbatim to
                non-Gaussian innovations, plus two validation rules;
``simulate``    stopped-path simulation with exact common random numbers;
``quadrature``  the deterministic reference route with no sampling error;
``estimators``  batch-level Route A / Route B estimators.

Nothing here reads or writes any frozen artifact.
"""
