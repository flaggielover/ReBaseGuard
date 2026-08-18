from rebaseguard_certify.cli import main


def test_cli_reports_noncertified_before_certificate(tmp_path):
    assert main(["audit", str(tmp_path / "missing.json")]) != 0

