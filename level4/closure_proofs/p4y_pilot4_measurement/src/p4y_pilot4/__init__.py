"""P4Y PILOT-4 -- heavy-tail precision MEASUREMENT feasibility gate.

NON-BINDING.  Not P4Y production, not a binding checkpoint, not an
allocation-rule pilot, not a cap-selection pilot, not a 96-cell campaign.

There is no Stage-1 sizing, no staged top-up, no cap design, no kappa
selection and no correspondence adjudication anywhere in this package.  The
sole question is whether the instrument those things would rely on is itself
reliable:

    does there exist an affordable (logical block size, reference block count)
    under which the t1p5 precision scale can be estimated to a predeclared
    multiplicative accuracy with a predeclared probability?

Pilot-3 stopped because it asserted a benchmark uncertainty of 0.79 % from
1/sqrt(2(n-1)) -- a normal-theory formula -- for a law in which one block in
8000 carried 29.3 % of the total squared deviation.  Pilot-4 uses no such
formula anywhere.  Its benchmark is admissible only if it passes empirical
stability criteria frozen before any result exists.
"""

__all__ = ["addressing4", "blocks4", "estimand", "design4"]
