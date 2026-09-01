"""G2 - claim ledger schema."""
REQUIRED = {"id","priority","statement","status","evidence_type","source",
            "edges","parents","assumptions","scope","limitations","p9_may_use","note"}

def test_ids_unique(claims):
    ids = [c["id"] for c in claims]
    assert len(ids) == len(set(ids))

def test_required_fields(claims):
    for c in claims:
        assert REQUIRED <= set(c), (c["id"], REQUIRED - set(c))

def test_status_vocabulary(claims, ledger):
    vocab = set(ledger["status_vocabulary"])
    for c in claims:
        assert c["status"] in vocab, (c["id"], c["status"])

def test_every_claim_has_a_source(claims):
    for c in claims:
        assert c["source"].strip(), c["id"]

def test_parents_resolvable(claims, byid):
    for c in claims:
        for e in c["edges"]:
            assert e["parent"] in byid, (c["id"], e["parent"])

def test_edge_types_declared(claims):
    for c in claims:
        for e in c["edges"]:
            assert e["type"] in ("premise", "verifies", "diagnoses"), (c["id"], e)

def test_parents_field_is_premise_edges_only(claims):
    for c in claims:
        assert c["parents"] == [e["parent"] for e in c["edges"] if e["type"] == "premise"]

def test_generator_reports_no_validation_findings(ledger):
    assert ledger["validation_findings"] == []
