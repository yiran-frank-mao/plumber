# plumber — 2d TQFT cobordisms in LaTeX

A LaTeX package (built on TikZ and expl3) that draws surfaces built from the generators of the
2-dimensional cobordism category — cylinders, pairs of pants, caps, crossings and U-turns — from a
layer-by-layer description:

```latex
\usepackage{plumber}
...
\[ \PL{2,3}{pant, id}\PL{3,2}{id, copant}
   = \PL[reduce]{2,3}{pant, id}\PL{3,2}{id, copant} \]
```

`\PL{m,n}{...}` is one layer going from `m` to `n` circles, the tensor product of the listed
generators. Consecutive `\PL` commands are composed into one surface. The package places the
circles on every seam and draws each seam as a circle with a solid front half and a dashed back
half.

## Features

- **Composition**: write a chain like `\PL{2,3}{pant, id}\PL{3,2}{id, copant}`.
  The numbers of circles may change from layer to layer, and the counts are checked.
  Generators: `id`, `pant` (1→2), `copant` (2→1), `unit` (0→1), `counit` (1→0), `swap` (a crossing
  with no tube in front), `twist`/`itwist` (crossings, the second/first tube in front), `pair` (2→0)
  and `copair` (0→2), with aliases such as `cyl`, `birth`, `death`, `ev`, `coev`. `id^3` means three copies.
- **Horizontal or vertical**: `horizontal` (the default, read left to right) or `vertical` (read top to
  bottom). `reverse` flips the direction.
- **Reduced form**: `reduce` computes the connected components and their genera, then draws the
  normal form: permute, merge, add handles, split, and permute again (`crossing=twist` uses twists instead of
  swaps for the permutations).
  Closed components are drawn as separate factors, or written as `Z(\Sigma_g)` with
  `closed=factor` (customisable with `closed value`). `\PLlastcomponents`, `\PLlastgenus`,
  `\PLlasteuler`, `\PLlastclosed` and `\PLlastnormalform` return the invariants and the normal form.
- **Names**: `names` writes `\Delta \otimes \mathrm{id}` (and so on) under each layer.
  `symbols={pant=m^*, ...}` changes the symbols. `\PLgenerators[names]` draws all generators.
- **Standalone pictures**: with `\documentclass[tikz]{standalone}`, every `\[...\]` or `\(...\)`
  that contains diagrams becomes one cropped page.
- **Appearance**: `circle sep`, `radius`, `length`, `perspective`, `crotch`, `scale`, `fill`, `seams`,
  `outline style`, `hidden style`, … and TikZ styles (`pl surface`, `pl outline`, `pl seam`,
  `pl hidden`, …).

The option names follow the sister package
[temperleylieb](https://github.com/yiran-frank-mao/temperleylieb) (`horizontal`/`vertical`,
`reverse`, `reduce`, `names`, `separator`, `scale`, `baseline`, `tikz`, `\plset`, …).

```latex
\PLgenerators[names]
\PL[vertical, names]{2,3}{pant, id}\PL{3,2}{id, copant}
\PL{1,3}{id, copair}\PL{3,1}{pair, id} = \PL{1,1}{id}               % snake identity
\PL[reduce, closed=factor]{0,2}{copair}\PL{2,0}{pair}               % Z(\Sigma_1)
```

See [`plumber-doc.pdf`](plumber-doc.pdf) for the full manual and
[`examples/frobenius.pdf`](examples/frobenius.pdf) for the relations of a commutative Frobenius
algebra drawn with the package.

## Installation

Copy `plumber.sty` next to your document, or into your local `texmf` tree
(for example `~/texmf/tex/latex/plumber/`). It needs a LaTeX kernel from 2020-10
or newer and TikZ, and is tested with pdfLaTeX and LuaLaTeX. If another package
already defines `\PL`, use the synonym `\PLlayer`.

## Building the documentation and running tests

```sh
make            # builds plumber-doc.pdf and examples/frobenius.pdf
make test       # checks the topology and normal form against a Python reference on random words,
                # and checks the pages produced with the standalone class
```

On Debian/Ubuntu the required TeX packages are
`texlive-latex-base texlive-latex-recommended texlive-latex-extra texlive-pictures`.

## Files

| File | Purpose |
| --- | --- |
| `plumber.sty` | the package |
| `plumber-doc.tex` / `.pdf` | user manual with live examples |
| `examples/frobenius.tex` / `.pdf` | the relations of 2Cob (Frobenius, snake, …), horizontal and vertical |
| `tests/check_reduce.py` | randomized test of the composition analysis and the normal form |
| `tests/check_standalone.py` | compiles diagrams with the `standalone` class and checks the pages |

Licensed under the LaTeX Project Public License 1.3c.
