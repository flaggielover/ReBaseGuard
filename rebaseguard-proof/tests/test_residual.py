from rebaseguard_certify.residual import (
    certify_continuum_residuals,
    construct_candidate_payloads,
)


def test_residual_certificate_covers_complete_reachable_parameterization():
    payload = construct_candidate_payloads(degree=4, quadrature_order=40, scale_bits=40)
    result = certify_continuum_residuals(
        payload, phi_order=12, subdivision_depth=0, bits=128
    )
    assert result["coverage"]["reachable_continuum_complete"] is True
    assert result["coverage"]["gaussian_tail_truncation"] == "none"
    assert result["coverage"]["bernstein_patches"] == 4
