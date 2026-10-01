"""Cell-308 MB-S successor campaign (r1) -- re-pin tooling (non-holder builder5, research brief 50). Target-free; NOT
frozen. It never imports the driver (which would load the science modules); it reads and rewrites TEXT only, imports
nothing of the campaign but mbs308_host (for the same host readings the driver uses), and is DRY-RUN by default:
nothing is written without an explicit flag.

  helpers      recompute HELPER_SHA256 mechanically: the sha256 of each helper file named by the driver's table,
               compared with the pinned value; `--write` rewrites exactly the stale values of that table.
  platform     the PLATFORM_PINS the driver's platform_readings() would read on THIS host with THIS interpreter
               (realpath of sys.executable and its sha256, the pinned libpython path and its sha256, sys.version,
               `sw_vers -buildVersion`, `uname -m`), compared with the pins; `--write-platform` rewrites them (for the
               freeze, on the qualification host, with the pinned interpreter; refused when any reading fails).
  driver-diff  the DRIVER_DIFF.md generator: difflib.SequenceMatcher(autojunk=False), 3 lines of context, unified
               hunk headers; each hunk's touched top-level definitions from the AST line ranges of the CHANGED lines of
               both files; hunk classes and header text CARRIED from the committed DRIVER_DIFF.md. It first
               REPRODUCES the committed DRIVER_DIFF.md from the committed driver byte for byte (else it refuses,
               GENERATOR_NOT_VALIDATED); then it generates the file for the working driver; `--write` writes it.
               A class is carried from the committed hunk with the same touched-definition set (the i-th such hunk
               to the i-th); a hunk with no counterpart needs `--classes '{"<n>": "LIFECYCLE", ...}'`; a hunk touching
               a carried (text-identical) definition is SCIENCE-GLUE (MUST NOT OCCUR) and the tool fails.
  check        helpers + driver-diff, dry-run: exit 0 only when nothing is stale.

    python3.14 -I -S -B mbs308_repin.py helpers [--code DIR] [--write]
    python3.14 -I -S -B mbs308_repin.py platform [--code DIR] [--write-platform]
    python3.14 -I -S -B mbs308_repin.py driver-diff [--ns DIR] [--repo DIR] [--classes JSON] [--write]
    python3.14 -I -S -B mbs308_repin.py check [--ns DIR]
Exit codes: 0 up to date (or written), 1 stale (dry-run), 2 refused.
"""
from __future__ import annotations

import argparse
import ast
import difflib
import hashlib
import json
import os
import re
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve()
NS = HERE.parents[1]
REPO = HERE.parents[4]
NS_REL = "level4/closure_proofs/p5y_k5_cell308_mbs_r1"
DRIVER = "mbs308_driver.py"
DIFF_NAME = "DRIVER_DIFF.md"
MBR1_DRIVER_REL = "level4/closure_proofs/p5y_k5_cell308_mb_r1/code/mb308_driver.py"
MBR1_FREEZE_R3 = "c46434a399eca18a709616a4a4d51918d1a30298"
GENV = {"PATH": "/usr/bin:/bin", "LC_ALL": "C", "GIT_OPTIONAL_LOCKS": "0"}
CLASSES = ("IDENTITY", "IDENTITY + LIFECYCLE", "LIFECYCLE")
SCIENCE_GLUE_CLASS = "SCIENCE-GLUE (MUST NOT OCCUR)"


class Refused(Exception):
    def __init__(self, code: str, detail: str = ""):
        super().__init__(f"{code}: {detail}" if detail else code)
        self.code = code


def sha(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()


def _write_atomic(path: Path, data: bytes) -> None:
    tmp = path.with_name(f".{path.name}.repin-{os.getpid()}")
    with open(tmp, "xb") as fh:
        fh.write(data)
        fh.flush()
        os.fsync(fh.fileno())
    os.replace(tmp, path)


def _dict_literal(src: str, name: str) -> tuple:
    """(the dict of string constants bound to the module-level `name`, its source segment). Exactly one binding."""
    found = [n for n in ast.parse(src).body if isinstance(n, ast.Assign) and
             [getattr(t, "id", None) for t in n.targets] == [name]]
    if len(found) != 1 or not isinstance(found[0].value, ast.Dict):
        raise Refused("TABLE_NOT_FOUND", f"{name} must be bound exactly once to a dict literal")
    d = {}
    for k, v in zip(found[0].value.keys, found[0].value.values):
        if not (isinstance(k, ast.Constant) and isinstance(k.value, str) and isinstance(v, ast.Constant) and
                isinstance(v.value, str)):
            raise Refused("TABLE_NOT_LITERAL", f"{name} must map string constants to string constants")
        d[k.value] = v.value
    return d, ast.get_source_segment(src, found[0])


def _rewrite_table(src: str, name: str, new: dict) -> str:
    """Replace the values of `name`'s dict literal for the keys in `new`, each `"key": "old"` pair exactly once inside
    the table's own source segment; every other byte of the file is unchanged."""
    old, seg = _dict_literal(src, name)
    out = seg
    for k, v in new.items():
        pair = f"{json.dumps(k)}: {json.dumps(old[k])}"
        if out.count(pair) != 1:
            raise Refused("TABLE_PAIR_AMBIGUOUS", f"{name}[{k}]")
        out = out.replace(pair, f"{json.dumps(k)}: {json.dumps(v)}")
    if src.count(seg) != 1:
        raise Refused("TABLE_SEGMENT_AMBIGUOUS", name)
    res = src.replace(seg, out)
    got, _ = _dict_literal(res, name)
    if got != dict(old, **new):
        raise Refused("TABLE_REWRITE_CHECK", name)
    return res


# ------------------------------------------------------------------ helpers
def helper_status(code: Path) -> dict:
    src = (code / DRIVER).read_text()
    pins, _ = _dict_literal(src, "HELPER_SHA256")
    rows = {}
    for name, pinned in sorted(pins.items()):
        p = code / name
        actual = sha(p.read_bytes()) if p.is_file() else None
        rows[name] = {"pinned": pinned, "actual": actual, "stale": actual != pinned}
    return {"code_dir": str(code), "helpers": rows, "stale": sorted(k for k, v in rows.items() if v["stale"]),
            "missing": sorted(k for k, v in rows.items() if v["actual"] is None)}


def repin_helpers(code: Path, write: bool) -> dict:
    st = helper_status(code)
    if st["missing"]:
        raise Refused("HELPER_MISSING", ", ".join(st["missing"]))
    st["written"] = False
    if write and st["stale"]:
        drv = code / DRIVER
        src = drv.read_text()
        new = _rewrite_table(src, "HELPER_SHA256", {k: st["helpers"][k]["actual"] for k in st["stale"]})
        _write_atomic(drv, new.encode())
        st["written"] = True
        st["after"] = helper_status(code)["stale"]
    return st


# ------------------------------------------------------------------ platform pins
def platform_readings(pins: dict) -> dict:
    """The driver's platform_readings(), on this host with this interpreter (same commands, same host helper)."""
    sys.path.insert(0, str(HERE.parent))
    import mbs308_host as HOST
    exe = os.path.realpath(sys.executable)
    lib = pins["libpython"]

    def fsha(p):
        try:
            return hashlib.sha256(Path(p).read_bytes()).hexdigest()
        except OSError:
            return None
    build = HOST._run(["/usr/bin/sw_vers", "-buildVersion"])
    arch = HOST._run(["/usr/bin/uname", "-m"])
    return {"python_executable": exe, "python_sha256": fsha(exe), "libpython": lib, "libpython_sha256": fsha(lib),
            "python_version": sys.version.split()[0], "python_sys_version": sys.version,
            "os_build": (build or "").strip() or None, "arch": (arch or "").strip() or None}


def platform_status(code: Path) -> dict:
    pins, _ = _dict_literal((code / DRIVER).read_text(), "PLATFORM_PINS")
    got = platform_readings(pins)
    if set(got) != set(pins):
        raise Refused("PLATFORM_KEYS", f"readings {sorted(got)} vs pins {sorted(pins)}")
    rows = {k: {"pinned": pins[k], "reading": got[k], "differs": got[k] != pins[k]} for k in sorted(pins)}
    return {"code_dir": str(code), "interpreter": sys.executable, "pins": rows,
            "differs": sorted(k for k, v in rows.items() if v["differs"]),
            "unreadable": sorted(k for k, v in got.items() if v is None)}


def repin_platform(code: Path, write: bool) -> dict:
    st = platform_status(code)
    st["written"] = False
    if write and st["differs"]:
        if st["unreadable"]:
            raise Refused("PLATFORM_READING_FAILED", ", ".join(st["unreadable"]))
        drv = code / DRIVER
        new = _rewrite_table(drv.read_text(), "PLATFORM_PINS", {k: st["pins"][k]["reading"] for k in st["differs"]})
        _write_atomic(drv, new.encode())
        st["written"] = True
        st["after"] = platform_status(code)["differs"]
    return st


# ------------------------------------------------------------------ the DRIVER_DIFF.md generator
def _node_label(n: ast.AST, first: bool) -> str:
    if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
        return n.name
    if isinstance(n, (ast.Import, ast.ImportFrom)):
        return "<imports>"
    if first and isinstance(n, ast.Expr) and isinstance(n.value, ast.Constant) and isinstance(n.value.value, str):
        return "<module docstring>"
    return "<module-level assignment / statement>"


def _line_owner(src: str) -> dict:
    """line number (1-based) -> the label of the top-level statement whose line range (decorators included) holds it."""
    out = {}
    body = ast.parse(src).body
    for i, n in enumerate(body):
        start = min([n.lineno] + [d.lineno for d in getattr(n, "decorator_list", [])])
        for ln in range(start, n.end_lineno + 1):
            out[ln] = _node_label(n, i == 0)
    return out


def carried_names(base: str, new: str) -> list:
    """Top-level definitions present in both files with text-identical source segments."""
    def segs(src):
        return {n.name: ast.get_source_segment(src, n) for n in ast.parse(src).body
                if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef))}
    a, b = segs(base), segs(new)
    return sorted(k for k in a if k in b and a[k] == b[k])


def _range(start: int, stop: int) -> str:
    """difflib's unified-diff range format (_format_range_unified)."""
    beginning, length = start + 1, stop - start
    if length == 1:
        return f"{beginning}"
    if not length:
        beginning -= 1
    return f"{beginning},{length}"


def hunks(base: str, new: str) -> list:
    a, b = base.splitlines(keepends=True), new.splitlines(keepends=True)
    own_a, own_b = _line_owner(base), _line_owner(new)
    out = []
    for group in difflib.SequenceMatcher(None, a, b, autojunk=False).get_grouped_opcodes(3):
        f, l = group[0], group[-1]
        lines = [f"@@ -{_range(f[1], l[2])} +{_range(f[3], l[4])} @@\n"]
        touched = set()
        for tag, i1, i2, j1, j2 in group:
            if tag == "equal":
                lines += [" " + x for x in a[i1:i2]]
                continue
            if tag in ("replace", "delete"):
                lines += ["-" + x for x in a[i1:i2]]
                touched |= {own_a[i + 1] for i in range(i1, i2) if i + 1 in own_a}
            if tag in ("replace", "insert"):
                lines += ["+" + x for x in b[j1:j2]]
                touched |= {own_b[j + 1] for j in range(j1, j2) if j + 1 in own_b}
        text = "".join(x if x.endswith("\n") else x + "\n\\ No newline at end of file\n" for x in lines)
        out.append({"text": text, "touched": sorted(touched)})
    return out


_HUNK_HDR = re.compile(r"^### Hunk (\d+): (.+?); (.*)$")


def parse_committed(md: str) -> dict:
    """The committed file's carried parts: its header lines (for the carried text) and each hunk's class and touched
    set, in order."""
    lines = md.split("\n")
    classes = []
    for ln in lines:
        m = _HUNK_HDR.match(ln)
        if m:
            classes.append({"n": int(m.group(1)), "class": m.group(2), "touched": m.group(3).split(", ")})
    head_end = lines.index("## Hunk index")
    return {"header": lines[:head_end], "hunks": classes}


def render(base: str, new: str, committed: dict, classes_override: dict | None = None) -> tuple:
    """(the DRIVER_DIFF.md text, the per-hunk class decisions). Refuses on a hunk without a class."""
    hs = hunks(base, new)
    glue = set(carried_names(base, new))
    by_set: dict = {}
    for h in committed["hunks"]:
        by_set.setdefault(tuple(h["touched"]), []).append(h["class"])
    used: dict = {}
    decisions = []
    for i, h in enumerate(hs, 1):
        key = tuple(h["touched"])
        k = used.get(key, 0)
        used[key] = k + 1
        if glue & set(h["touched"]):
            cls, how = SCIENCE_GLUE_CLASS, "touches a carried definition"
        elif classes_override and str(i) in classes_override:
            cls, how = classes_override[str(i)], "given (--classes)"
        elif k < len(by_set.get(key, [])):
            cls, how = by_set[key][k], "carried"
        else:
            raise Refused("HUNK_WITHOUT_CLASS", f"hunk {i} touches {list(key)}: give its class with --classes")
        if cls not in CLASSES + (SCIENCE_GLUE_CLASS,):
            raise Refused("UNKNOWN_CLASS", f"hunk {i}: {cls}")
        h["class"] = cls
        decisions.append({"hunk": i, "class": cls, "how": how, "touched": h["touched"]})
    counts: dict = {}
    for h in hs:
        counts[h["class"]] = counts.get(h["class"], 0) + 1
    hdr = []
    for ln in committed["header"]:
        if ln.startswith("* Base: "):
            ln = re.sub(r"sha256 `[0-9a-f]{64}`", f"sha256 `{sha(base.encode())}`", ln)
        elif ln.startswith("* New: "):
            ln = re.sub(r"sha256 `[0-9a-f]{64}`", f"sha256 `{sha(new.encode())}`", ln)
        elif ln.startswith("* Hunks: "):
            ln = f"* Hunks: {len(hs)}; by class: " + ", ".join(f"{c} {n}" for c, n in sorted(counts.items())) + "."
        elif ln.startswith("* The carried (text-identical) functions: "):
            ln = "* The carried (text-identical) functions: " + ", ".join(f"`{n}`" for n in sorted(glue)) + "."
        hdr.append(ln)
    out = ["\n".join(hdr), "## Hunk index\n", "| # | class | top-level definitions touched |", "|---|---|---|"]
    for i, h in enumerate(hs, 1):
        out.append(f"| {i} | {h['class']} | " + ", ".join(f"`{t}`" for t in h["touched"]) + " |")
    out.append("\n## Full diff, hunk by hunk\n")
    for i, h in enumerate(hs, 1):
        out.append(f"### Hunk {i}: {h['class']}; {', '.join(h['touched'])}\n")
        out.append("```diff\n" + h["text"] + "```\n")
    return "\n".join(out) + "\n", decisions


def git_show(repo: Path, rev: str, rel: str) -> bytes | None:
    p = subprocess.run(["/usr/bin/git", "-C", str(repo), "show", f"{rev}:{rel}"], capture_output=True, env=GENV,
                       stdin=subprocess.DEVNULL)
    return p.stdout if p.returncode == 0 else None


def driver_diff(ns: Path, repo: Path, write: bool, classes_override: dict | None = None) -> dict:
    base_b = git_show(repo, MBR1_FREEZE_R3, MBR1_DRIVER_REL)
    head_drv = git_show(repo, "HEAD", f"{NS_REL}/code/{DRIVER}")
    head_md = git_show(repo, "HEAD", f"{NS_REL}/{DIFF_NAME}")
    if base_b is None or head_drv is None or head_md is None:
        raise Refused("GIT_READ_FAILED", "MB r1's driver at c46434a3, or the committed driver / DRIVER_DIFF.md")
    base = base_b.decode()
    committed = parse_committed(head_md.decode())
    # 1. validation: the committed file, regenerated from the committed driver with its own classes, byte for byte
    regen, _ = render(base, head_drv.decode(), committed)
    if regen.encode() != head_md:
        raise Refused("GENERATOR_NOT_VALIDATED", "the committed DRIVER_DIFF.md is not reproduced byte for byte")
    # 2. the working driver
    new = (ns / "code" / DRIVER).read_text()
    text, decisions = render(base, new, committed, classes_override)
    cur = (ns / DIFF_NAME).read_bytes() if (ns / DIFF_NAME).exists() else None
    out = {"validated_against_head": True, "hunks": len(decisions), "decisions": decisions,
           "science_glue_hunks": [d["hunk"] for d in decisions if d["class"] == SCIENCE_GLUE_CLASS],
           "stale": cur != text.encode(), "written": False, "sha256": sha(text.encode())}
    if out["science_glue_hunks"]:
        raise Refused("SCIENCE_GLUE_HUNK", json.dumps(out["science_glue_hunks"]))
    if write and out["stale"]:
        _write_atomic(ns / DIFF_NAME, text.encode())
        out["written"] = True
    return out


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("what", choices=("helpers", "platform", "driver-diff", "check"))
    ap.add_argument("--code", help="code directory (default: this namespace's code/)")
    ap.add_argument("--ns", help="namespace directory (driver-diff / check; default: this namespace)")
    ap.add_argument("--repo", help="repository (driver-diff; default: this namespace's repository)")
    ap.add_argument("--classes", help='JSON {"<hunk number>": "<class>"} for hunks without a committed counterpart')
    ap.add_argument("--write", action="store_true", help="helpers / driver-diff: write the stale values / file")
    ap.add_argument("--write-platform", action="store_true", help="platform: rewrite PLATFORM_PINS (the freeze)")
    a = ap.parse_args(argv)
    ns = Path(a.ns).resolve() if a.ns else NS
    code = Path(a.code).resolve() if a.code else ns / "code"
    try:
        if a.what == "helpers":
            r = repin_helpers(code, a.write)
            stale = bool(r["stale"]) and not r["written"]
        elif a.what == "platform":
            if a.write:
                raise Refused("FLAG", "platform pins are written only with --write-platform")
            r = repin_platform(code, a.write_platform)
            stale = bool(r["differs"]) and not r["written"]
        elif a.what == "driver-diff":
            r = driver_diff(ns, Path(a.repo).resolve() if a.repo else REPO, a.write,
                            json.loads(a.classes) if a.classes else None)
            stale = r["stale"] and not r["written"]
        else:
            if a.write or a.write_platform:
                raise Refused("FLAG", "check is dry-run only")
            r = {"helpers": helper_status(code), "driver_diff": driver_diff(ns, REPO, False)}
            stale = bool(r["helpers"]["stale"]) or r["driver_diff"]["stale"]
    except Refused as e:
        print(json.dumps({"refused": e.code, "detail": str(e)}))
        return 2
    print(json.dumps(r, indent=1, sort_keys=True))
    return 1 if stale else 0


if __name__ == "__main__":
    sys.exit(main())
