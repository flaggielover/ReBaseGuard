import math

from flint import arb
from scipy.special import ndtr

from rebaseguard_certify.arb_backend import (
    ball_record,
    gaussian_cdf,
    gaussian_mass,
    gaussian_phi,
    gaussian_tail_second_moment,
    workprec,
)


def test_arb_gaussian_primitives_contain_float_references():
    with workprec(192):
        x = arb(5) / arb(4)
        assert abs(float(gaussian_phi(x).mid()) - math.exp(-1.25**2 / 2) / math.sqrt(2 * math.pi)) < 1e-15
        assert abs(float(gaussian_cdf(x).mid()) - ndtr(1.25)) < 1e-15
        mass = gaussian_mass(-x, x)
        assert abs(float(mass.mid()) - (ndtr(1.25) - ndtr(-1.25))) < 1e-15


def test_tail_second_moment_is_positive_and_symmetric():
    with workprec(192):
        x = arb(11) / arb(2)
        upper = gaussian_tail_second_moment(x, upper=True)
        lower = gaussian_tail_second_moment(-x, upper=False)
        assert upper > 0
        assert (upper - lower).contains(0)


def test_ball_record_round_trip_contains_original():
    with workprec(192):
        value = gaussian_cdf(arb(1) / arb(3))
        record = ball_record(value, digits=70)
        restored = arb(record["ball"])
        assert restored.contains(value)
