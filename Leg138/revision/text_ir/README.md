# Site 846 Initial Reports text collation

This edition covers the narrative, headings, printed captions, table notes, references, running heads and folios of all 69 pages of the publisher’s Site 846 chapter (pp. 265–333). The text was read against the photographed type in the digital witness. The reviewer was an AI editor. Independent human verification remains open.

The two landscape table pages, rotated marginal type and source sections that resume several pages after a graph spread follow the chapter as issued. Original print errors and discrepancies appear in the reading text. Selected decisions affecting scientific interpretation are listed in [notes.csv](notes.csv).

## Witness and scope

[Publisher chapter PDF](https://www-odp.tamu.edu/publications/138_IR/VOLUME/CHAPTERS/ir138_11.pdf) · SHA-256 `9029db07c07283a3d30eb8ddb9ed4c075771f31cc48927876a5d6ee9f4cbc268`.

Five pages were checked in full, including the five-row epoch boundary table on printed p. 285. For the other 64 pages, each entry in [pages.csv](pages.csv) specifies the uncollated chart, table, photograph or log interior. The 71 caption blocks include continuation captions. Figure 21 is explicitly referenced on printed p. 293 as a back-pocket enclosure. That enclosure, electronic tables on the accompanying disc, Part 2 microfiche, barrel sheets and separate core-photo forms require their own witnesses. This chapter collation does not certify their contents.

## Files

| File | Contents |
| --- | --- |
| [pages.jsonl](pages.jsonl) | Reader blocks in editorial reading order. Each page gives its source URL, PDF digest, embedded scan digest and pixel size, folio, scope and review method. |
| [lines.csv](lines.csv) | Publisher text segment and checked reading side by side, with physical page, PDF coordinates, segment address, ordinal in the reading sequence and the exact witness digest. |
| [variants.csv](variants.csv) | Individual changed readings, each tied to a reader block and, where present, a publisher PDF line. A damaged letter supplied from context has its own decision type. |
| [epoch_boundaries.csv](epoch_boundaries.csv) | The five rows of the unnumbered table on p. 285, with printed boundary names, hole, two independent depth columns, biostratigraphic marker and links to the exact collated reader blocks. |
| [verification.json](verification.json) | Scope and counts reproduced from this witness. |
| [notes.csv](notes.csv) | Source contradictions, an explicitly restored letter, and release-version and sample-attribution caveats encountered in the chapter. |

The source address is `[block, line, part]` in the publisher’s positioned layer as emitted by the shared `edition2/page_text.py` extractor. Line and part start at one. Coordinates are PDF points from the upper-left of the unrotated source-page rectangle. Negative block numbers `-1` and `-2` identify running heads and folios actually absent from the publisher text layer. Those have an original scan bounding box and an empty publisher line ordinal. Checked publisher segments can be fragments of a printed line.

Reader text joins line wraps within paragraphs, preserves lexical hyphens and identifiers, and keeps page boundaries for citation. Unicode and character-offset styles retain scientific typography, including the alkenone index, chemical formulae, and italic taxon names. For the single editorial restoration, the bound source line retains an explicit missing-glyph marker while the reading text gives the reconstructed word. Source conflict notes are separate from the publication text. Every reader block has source addresses and point coordinates for renewed inspection.

## Rebuild

From the repository root, supply the exact publisher PDF to the project Python environment with PyMuPDF installed.

```sh
python Leg138/revision/text_ir/build.py /path/to/ir138_11.pdf --check
```

Omitting `--check` regenerates the six derived data files. The SHA-256 guard prevents applying these readings to a different release. [build.py](build.py) and [additional.py](additional.py) contain the page order, source-address selections and explicit glyph decisions.
