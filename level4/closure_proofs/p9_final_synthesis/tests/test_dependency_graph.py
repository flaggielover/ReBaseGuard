"""G3 acyclicity over ALL edge types; G4 no-inflation over premise edges."""
def test_no_cycles_over_all_edges(claims, byid):
    colour = {}
    def dfs(n, stack):
        if colour.get(n) == 2: return
        assert colour.get(n) != 1, "cycle: " + " -> ".join(stack + [n])
        colour[n] = 1
        for e in byid[n]["edges"]: dfs(e["parent"], stack + [n])
        colour[n] = 2
    for c in claims: dfs(c["id"], [])

def test_no_inflation_along_premise_edges(claims, byid, ledger):
    rank = ledger["strength_rank"]
    for c in claims:
        if not c["parents"]: continue
        worst = min(rank[byid[p]["status"]] for p in c["parents"])
        assert rank[c["status"]] <= worst, (
            f"{c['id']} ({c['status']}) exceeds weakest premise rank {worst}")

def test_graph_json_matches_ledger(claims, graph):
    assert {n["id"] for n in graph["nodes"]} == {c["id"] for c in claims}
    expected = {(e["parent"], c["id"], e["type"]) for c in claims for e in c["edges"]}
    assert {(e["from"], e["to"], e["type"]) for e in graph["edges"]} == expected

def test_verifies_edges_exist_and_are_excluded_from_bound(claims, byid, ledger):
    """The verifies type must be load-bearing, not decorative: at least one
    verifies edge must connect a node that WOULD violate the bound as premise."""
    rank = ledger["strength_rank"]
    load_bearing = []
    for c in claims:
        for e in c["edges"]:
            if e["type"] == "verifies" and rank[c["status"]] > rank[byid[e["parent"]]["status"]]:
                load_bearing.append((c["id"], e["parent"]))
    assert load_bearing, "no load-bearing verifies edge; the distinction would be decorative"
