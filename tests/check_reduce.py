"""Cross-check the package's analysis and normal form against Python.

For random words of layers, the package prints (via \\PLlastnormalform etc.)
the number of components, the total genus, the Euler characteristic and the
reduced word.  A 2d cobordism is determined up to diffeomorphism by how its
components partition the boundary circles and by their genera, so the test
checks that the reduced word has exactly the same invariants as the input
word, and that it really is in normal form.

Run from the repository root:  python3 tests/check_reduce.py [seed] [count]
"""
import os
import random
import re
import subprocess
import sys
import tempfile
from collections import Counter

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)

ARITY = {
    "id": (1, 1), "pant": (1, 2), "copant": (2, 1), "unit": (0, 1),
    "counit": (1, 0), "swap": (2, 2), "twist": (2, 2), "itwist": (2, 2), "pair": (2, 0),
    "copair": (0, 2),
}
CHI = {"pant": -1, "copant": -1, "unit": 1, "counit": 1}


def invariants(factors):
    """Components of a list of words (each word a list of layers).

    Returns (open, closed): open is a sorted list of
    (inputs, outputs, genus) of the components of the first word that has
    boundary, closed a sorted list of genera of closed components.
    """
    open_parts, closed = [], []
    for word in factors:
        parent = {}

        def find(x):
            while parent.setdefault(x, x) != x:
                x = parent[x]
            return x

        def union(x, y):
            parent[find(x)] = find(y)

        pieces = []
        counts = [sum(ARITY[g][0] for g in word[0])] if word else [0]
        for k, layer in enumerate(word, start=1):
            i = o = 0
            for g in layer:
                a, b = ARITY[g]
                ins = [(k - 1, i + t) for t in range(a)]
                outs = [(k, o + t) for t in range(b)]
                for node in ins + outs:
                    find(node)
                if g in ("swap", "twist", "itwist"):
                    union(ins[0], outs[1])
                    union(ins[1], outs[0])
                else:
                    nodes = ins + outs
                    for node in nodes[1:]:
                        union(nodes[0], node)
                    pieces.append((nodes[0], CHI.get(g, 0)))
                i, o = i + a, o + b
            counts.append(o)
        last = len(word)
        chi = Counter()
        for node, c in pieces:
            chi[find(node)] += c
        comps = {}
        for node in list(parent):
            comps.setdefault(find(node), ([], []))
        for i in range(counts[0]):
            comps[find((0, i))][0].append(i + 1)
        for j in range(counts[-1]):
            comps[find((last, j))][1].append(j + 1)
        for root, (ins, outs) in comps.items():
            b = len(ins) + len(outs)
            twice_g = 2 - chi[root] - b
            assert twice_g >= 0 and twice_g % 2 == 0, (word, root)
            if b:
                open_parts.append((tuple(ins), tuple(outs), twice_g // 2))
            else:
                closed.append(twice_g // 2)
    return sorted(open_parts), sorted(closed)


def random_word(rng, max_width=5, max_layers=5):
    width = rng.randint(0, 3)
    word = []
    for _ in range(rng.randint(1, max_layers)):
        layer, left, out = [], width, 0
        while left > 0 or (rng.random() < 0.15 and out < max_width):
            choices = [g for g, (a, b) in ARITY.items()
                       if a <= left and out + b <= max_width + 1]
            if left == 0:
                choices = [g for g in choices if ARITY[g][0] == 0]
            weights = [6 if g == "id" else 2 for g in choices]
            g = rng.choices(choices, weights)[0]
            layer.append(g)
            left -= ARITY[g][0]
            out += ARITY[g][1]
        if not layer:
            layer = ["unit"]
            out = 1
        word.append(layer)
        width = out
    return word


def tex_word(word, options=""):
    out = []
    for k, layer in enumerate(word):
        a = sum(ARITY[g][0] for g in layer)
        b = sum(ARITY[g][1] for g in layer)
        opt = "[%s]" % options if k == 0 and options else ""
        out.append(r"\PL%s{%d,%d}{%s}" % (opt, a, b, ", ".join(layer)))
    return "".join(out)


PL_RE = re.compile(r"\\PL\{(\d+),(\d+)\}\{([^}]*)\}")


def parse_normal_form(text):
    factors = []
    for part in text.split(r"\cdot"):
        layers = []
        for m, n, gens in PL_RE.findall(part):
            layer = [g.strip() for g in gens.split(",") if g.strip()]
            assert sum(ARITY[g][0] for g in layer) == int(m), part
            assert sum(ARITY[g][1] for g in layer) == int(n), part
            layers.append(layer)
        if layers:
            factors.append(layers)
    return factors


def check_normal(main):
    """A normal form is: swaps, then merges, handles, splits, then swaps.

    In the middle part, every component is a tree of copants, then
    pant/copant pairs (handles), then a tree of pants, so reading the
    generators that are not id or swap gives at most one block of copants
    (with units/pairs), then handles, then pants (with counits/copairs).
    """
    if len(main) == 1 and set(main[0]) == {"id"}:
        return None
    phase = 0  # 0: swaps, 1: merges, 2: handles, 3: splits, 4: swaps
    for layer in main:
        kinds = set(layer) - {"id"}
        if kinds <= {"swap"} and kinds:
            if phase in (1, 2, 3):
                phase = 4
            continue
        if not kinds:
            return "identity layer inside a non-trivial word"
        if phase == 4:
            return "generators after the output permutation"
        if kinds <= {"copant", "unit", "pair"}:
            if phase > 1 and not (phase == 2 and kinds == {"copant"}):
                return "merge after handles/splits"
            phase = max(phase, 1)
        elif kinds <= {"pant", "counit", "copair"}:
            if kinds == {"pant"} and phase <= 2:
                phase = 2  # may be the first half of a handle or a split
            else:
                phase = 3
        else:
            return "mixed layer %r" % layer
    return None


DOC = r"""\documentclass{article}
\usepackage{plumber}
\begin{document}
%s
\end{document}
"""


def main():
    seed = int(sys.argv[1]) if len(sys.argv) > 1 else 1
    count = int(sys.argv[2]) if len(sys.argv) > 2 else 150
    rng = random.Random(seed)
    words = [random_word(rng) for _ in range(count)]
    body = []
    for k, w in enumerate(words):
        body.append(tex_word(w, "reduce" if k % 2 else ""))
        body.append(r"\typeout{RESULT %d|\PLlastcomponents|\PLlastgenus|"
                    r"\PLlasteuler|\PLlastnormalform|}" % k)
        body.append(r"\par")
    with tempfile.TemporaryDirectory() as tmp:
        src = os.path.join(tmp, "t.tex")
        with open(src, "w") as f:
            f.write(DOC % "\n".join(body))
        env = dict(os.environ, TEXINPUTS=ROOT + "//:", max_print_line="100000")
        proc = subprocess.run(
            ["pdflatex", "-interaction=nonstopmode", "-halt-on-error", "t.tex"],
            cwd=tmp, env=env, capture_output=True, text=True)
        log = open(os.path.join(tmp, "t.log"), errors="replace").read()
        if proc.returncode != 0:
            print(log[-3000:])
            print("pdflatex failed")
            return 1
    results = {}
    for line in log.splitlines():
        if line.startswith("RESULT "):
            k, comps, genus, euler, nf, _ = line[len("RESULT "):].split("|")
            results[int(k)] = (int(comps), int(genus), int(euler), nf)
    failures = 0
    for k, w in enumerate(words):
        expected = invariants([w])
        comps, genus, euler, nf = results[k]
        open_parts, closed = expected
        m = sum(ARITY[g][0] for g in w[0])
        n = sum(ARITY[g][1] for g in w[-1])
        exp_comps = len(open_parts) + len(closed)
        exp_genus = sum(p[2] for p in open_parts) + sum(closed)
        exp_euler = 2 * exp_comps - 2 * exp_genus - m - n
        factors = parse_normal_form(nf)
        problems = []
        if (comps, genus, euler) != (exp_comps, exp_genus, exp_euler):
            problems.append("invariants %r != %r"
                            % ((comps, genus, euler),
                               (exp_comps, exp_genus, exp_euler)))
        got = invariants(factors) if factors else ([], [])
        if got != expected:
            problems.append("normal form %r has invariants %r, expected %r"
                            % (nf, got, expected))
        main_factors = [f for f in factors
                        if sum(ARITY[g][0] for g in f[0]) or
                        sum(ARITY[g][1] for g in f[-1])]
        if len(main_factors) > 1:
            problems.append("more than one main factor in %r" % nf)
        for f in main_factors:
            err = check_normal(f)
            if err:
                problems.append("%s: %r" % (err, nf))
        if problems:
            failures += 1
            print("word %d: %s" % (k, tex_word(w)))
            for p in problems:
                print("   ", p)
    print("%d words checked (seed %d), %d failures" % (count, seed, failures))
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
