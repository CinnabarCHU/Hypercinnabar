# Kemp, Baldauf and Pearce (1995), SR chapter 30

The five original leaves, pp. 641–645, were read against rendered columns of the publisher's scan. The transcription covers the title, byline, affiliations, abstract, continuous prose, six figure captions, references, acknowledgments, dates, running headings, folios and two types of footnote. Each block has an address in the exact distribution PDF. This is a single visual editorial reading. Its status does not imply a second independent proof or verification of the authors' scientific claims.

[Official PDF, printed pp. 641–645](https://www-odp.tamu.edu/publications/138_SR/VOLUME/CHAPTERS/sr138_30.pdf)

| File | Use |
| --- | --- |
| `pages.jsonl` | One record per physical PDF page. Ordered blocks have reflowed text, original line endings and selected verified inline emphasis. Character ranges use Unicode code points and a half-open end. |
| `SR.C30.p001.txt` through `SR.C30.p005.txt` | Reader-independent text. Printed line-end hyphenation survives. Reading order joins the columns within a paragraph and sets captions and footnotes apart. |
| `line_evidence.csv` and `corrections.csv` | Source-to-edition comparison at line level, including all unchanged readings in the former and all changed readings in the latter. Boxes are PDF points from the top left. The native ordinal is zero-based among text lines in unsorted PDF content order. The omitted verso folios have approximate region boxes and an empty native ordinal. |
| `figure_labels.csv` | 134 label readings in 32 visually read groups, covering the six figures. Group boxes locate lettering for comparison. Entries in a group inventory text and do not encode plotted values or the marks' exact coordinates. |
| `continuations.csv` | Explicit links across the four original physical page boundaries. For `alterna-\|tions` both diplomatic fragments are retained. |

## Editorial decisions

- On p. 642 the text layer gives `I03 to I06` for cell abundance. The original typesetting reads `10³ to 10⁶` cells per liter. Concentration a few lines later is `4.4/m³`. Raised digits are Unicode characters so they retain their meaning in plain text. The footnote numbers on p. 641 use the same convention.
- The source distinguishes `La Niña` and `El Niño`. The accent above the second n is visible in the abstract and in the physical description of the Fall 1992 cruise. The reader restores it wherever printed.
- The citation on p. 643 twice prints `Muller`. The reference on p. 645 prints `Müller`. The two forms remain distinct. The age range in the latter reference prints `9.8–4.5 Ma`; the embedded layer gives `9.8^1.5 Ma`. The published bibliography also prints `Bliel`, lowercase `equatorial pacific` in the Chavez et al. reference, and Hay's volume as `30`. These author or publisher readings are retained.
- The meaning of `latitudinal extent … 90° to 133°W` (p. 641) may invite a scientific correction; the transcription preserves the word printed in the original. The three-em dash in the repeated Sancetta bibliography entry represents the printed long rule.
- Figure 2B prints two question marks beside the Site 158 interval. Figure 2A has a small isolated circular mark below its lower left frame. Its function is unclear and it is not counted as a labeled tick. Figure lettering is tabulated outside the article prose to preserve independent addresses for the graphics.

## Rebuild from the source witness

With PyMuPDF 1.26.6, the following regenerates the five page records, five text files, page index and two line ledgers. The command rejects any PDF whose SHA-256 differs from the reviewed witness. The figure lettering is hand transcribed in the separate CSV.

```sh
python build_ch30.py path/to/sr138_30.pdf --output check
```

Selection and correction are literal and page-specific. The reflow preserves the text across columns and removes printed discretionary hyphens within paragraphs; printed strings with line breaks can always be recovered from `source_lines`. In-figure text has independent evidence in `figure_labels.csv`. Scientific names, selected title italics, raised markers and the bold subpanel identifiers have explicit style information. Typeface shapes, exact spacing and line-rule geometry remain in the facsimile.

The shared page reader also includes all 19 leaves of the Site 846 isotope study, including every narrative passage and caption and the complete printed Tables 2, 4 and 8. Their evidence and boundaries are described in [CH15.md](CH15.md); chapter-specific line ledgers remain independent.
