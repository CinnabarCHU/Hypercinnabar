# Independent visual check of 30 lines

An AI reviewer read each line on the source scan before seeing either stored transcription. The blinded sheet shows the exact 240 dpi strip used for OCR, an expanded crop with neighboring lines, and a page overview with the target marked. The selector checks the SHA-256 of the source PDF and the grayscale strip before making a sheet. The CSV records the PDF page (one-based), stage role, publisher segment ID, rectangles in PDF points, both machine readings and the independent visual reading. Individual cases can be reopened at their source addresses.

Each comparison stratum contains ten distinct documents. Within each stratum the sample has one prospectus line, one preliminary report line, four IR lines and four SR lines. Selection uses fixed SHA-256 order within series and stratum. These quotas and the upstream choice of lines prevent interpreting the counts as a volume-wide error rate.

| Digital comparison | Both exact | Publisher only | Second OCR only | Neither exact | Illegible |
| --- | ---: | ---: | ---: | ---: | ---: |
| Literal agreement | 10 | 0 | 0 | 0 | 0 |
| Disagreement | 0 | 5 | 2 | 3 | 0 |
| Empty second reading | 0 | 8 | 0 | 2 | 0 |

Exactness concerns the characters on the addressed line. Whitespace is collapsed. Italics and type weight are outside this score. Subscripts and visibly distinct dash forms are retained. For rows 19 and 20 the publisher preserved the scientific wording with a flattened range dash and baseline chemical subscript respectively. The printed double colon in row 11 is preserved, and row 14 records a numeral in a magnetochron name and the approximation sign before a depth. In row 18 the second reader dropped one digit from Site 844. Rows 27 and 30 expose defects in the surviving publisher text after the second reader returned an empty result. This review did not change the report texts.

Run from the Leg138 directory with the same PyMuPDF version used to generate the strips. Pillow renders the local contact sheets. Supply the directory that contains the source paths listed in the CSV.

```sh
python revision/triage/select_independent_sample.py --sources /path/to/source-root --contact-sheets /tmp/leg138-triage-sheets
```
