"""NON-RESULT-BEARING environment qualification for the production server.

Executes NO frozen scientific production cell and creates no K1 evidence. Every
timing here uses a synthetic object of the same computational shape as a real
panel, never a cover cell.
"""
from __future__ import annotations

import json, multiprocessing as mp, os, platform, resource, shutil, sys, time
from datetime import datetime, timezone
from pathlib import Path

HERE = Path(__file__).resolve().parent
NS = HERE.parent
sys.path.insert(0, str(NS))
from k1prod import schema as S                                        # noqa: E402


def _synthetic_backend_timing() -> dict:
    """Same shape as a panel contraction, on synthetic data. Not a cover cell."""
    from flint import arb, arb_mat, ctx
    ctx.prec = 256
    n, z = 204, 21
    P = arb_mat(n, z); Q = arb_mat(n, z); Hk = arb_mat(z, z)
    for i in range(n):
        for k in range(z):
            P[i, k] = arb(i + 1) / arb(k + 3)
            Q[i, k] = arb(k + 1) / arb(i + 5)
    for a in range(z):
        for b in range(z):
            Hk[a, b] = arb(1) / arb(a + b + 2)
    t = time.process_time()
    Rm = P * Hk
    M = Rm * Q.transpose()
    dt = time.process_time() - t
    return {"synthetic_panel_op_seconds": dt, "matrix_shapes": [[n, z], [z, z]],
            "checksum_is_finite": bool(M[0, 0].is_finite())}


def _determinism() -> dict:
    from flint import arb, ctx
    ctx.prec = 256
    a = (arb(2).sqrt() * arb(3).sqrt() - arb(6).sqrt())
    reps = [(arb(1) / arb(7) + arb(1) / arb(11)).str(40, radius=True) for _ in range(3)]
    return {"identical_across_repeats": len(set(reps)) == 1,
            "sqrt_identity_contains_zero": a.contains(arb(0)),
            "sample": reps[0]}


def _spawn_probe(k: int) -> int:
    return sum(i * i for i in range(20000)) % 97


def qualify(workers: int = 64) -> dict:
    t0 = time.time()
    out = {"schema": "rebaseguard.p5y.k1.env_qualification.v1",
           "result_bearing": False, "creates_K1_evidence": False,
           "generated_utc": datetime.now(timezone.utc).isoformat()}
    try:
        import flint
        fv = getattr(flint, "__version__", "unknown")
    except Exception as ex:                                           # noqa: BLE001
        fv = f"IMPORT FAILED: {ex}"
    du = shutil.disk_usage(str(NS))
    out["environment"] = {
        "python": sys.version.split()[0],
        "python_flint": fv,
        "platform": platform.platform(),
        "machine": platform.machine(),
        "cpu_count": os.cpu_count(),
        "ram_gib": round(os.sysconf("SC_PAGE_SIZE") * os.sysconf("SC_PHYS_PAGES")
                         / 1024 ** 3, 2) if hasattr(os, "sysconf") else None,
        "disk_free_gib": round(du.free / 1024 ** 3, 2),
        "filesystem_writable": os.access(str(NS), os.W_OK),
    }
    try:
        with mp.Pool(min(workers, os.cpu_count() or 1)) as p:
            got = p.map(_spawn_probe, range(min(workers, os.cpu_count() or 1)))
        spawn = {"ok": len(got) > 0, "workers_spawned": len(got)}
    except Exception as ex:                                           # noqa: BLE001
        spawn = {"ok": False, "error": str(ex)}
    out["process_spawning"] = spawn
    out["scheduling"] = S.verify_conservation(
        len(S.enumerate_units(S.load_checkpoint())), workers)
    out["backend"] = _synthetic_backend_timing()
    out["interval_determinism"] = _determinism()
    try:
        ck = S.load_checkpoint()
        out["checkpoint"] = {"readable": True, "hash": S.checkpoint_hash(),
                             "frozen": ck["state"]["P5Y_K1_SUCCESSOR_CHECKPOINT_STATUS"]
                             == "FROZEN"}
    except Exception as ex:                                           # noqa: BLE001
        out["checkpoint"] = {"readable": False, "error": str(ex)}

    checks = {
        "python_ok": sys.version_info >= (3, 10),
        "flint_importable": not str(fv).startswith("IMPORT FAILED"),
        "cpu_count_sufficient": (os.cpu_count() or 0) >= 1,
        "filesystem_writable": out["environment"]["filesystem_writable"],
        "disk_free_ok": out["environment"]["disk_free_gib"] > 5,
        "process_spawning": spawn.get("ok", False),
        "scheduling_exact": out["scheduling"]["exact"] and out["scheduling"]["no_missing"],
        "backend_finite": out["backend"]["checksum_is_finite"],
        "determinism": out["interval_determinism"]["identical_across_repeats"],
        "sqrt_identity": out["interval_determinism"]["sqrt_identity_contains_zero"],
        "checkpoint_readable_and_frozen": out["checkpoint"].get("readable", False)
                                          and out["checkpoint"].get("frozen", False),
    }
    out["checks"] = checks
    out["ENVIRONMENT_QUALIFICATION"] = "PASS" if all(checks.values()) else "FAIL"
    out["failed_checks"] = [k for k, v in checks.items() if not v]
    out["K1_verdict_produced"] = None
    out["peak_rss_mib"] = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 1024 ** 2
    out["wall_seconds"] = time.time() - t0
    return out


if __name__ == "__main__":
    w = int(sys.argv[1]) if len(sys.argv) > 1 else 64
    r = qualify(w)
    print(json.dumps(r, indent=1))
    raise SystemExit(0 if r["ENVIRONMENT_QUALIFICATION"] == "PASS" else 1)
