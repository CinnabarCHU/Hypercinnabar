# Leg 138 prospectus and preliminary report collation

The Scientific Prospectus collation covers its cover, publication notice, complete narrative, proposed operations and bibliography. The Preliminary Report collation covers its scientific narrative and bibliography, its operations report for Sites 844–854, and the technical report on shipboard instruments, laboratory procedures and software. Title and personnel pages for the operations and technical reports are included.

| Digital print witness | One-based PDF pages | Printed line segments addressed | Reading blocks | Editorial entries |
| --- | --- | ---: | ---: | ---: |
| Scientific Prospectus (SP) | 1–7 | 240 | 66 | 17 |
| Preliminary Report (PR) | 6–28, 78–98, 101–109 | 2,126 | 515 | 98 |

The science sections use the program’s terminology as published in 1991. For example, PR pp. 104–108 describe how the split-core spectrometer, multisensor track, digital sonic velocimeter and logging tools produced different observations. The equipment, storage, processing and onboard comparisons appear separately in the technical report. This collation records what the participants said at the time. A reader tracing an instrument series to an archived data file still needs the relevant file’s own metadata.

## Witness and verification

1. Obtain the two publisher PDFs and name them `SP.pdf` and `PR.pdf` in one directory. [Scientific Prospectus No. 38](https://www-odp.tamu.edu/publications/prosp/digital/138prosp.pdf) · [Preliminary Report No. 38](https://www-odp.tamu.edu/publications/prelim/138PREL.PDF)
2. From this directory, run `python build.py /path/to/pdfs` with PyMuPDF installed (verified with 1.26.6). The program checks both complete-file SHA-256 digests before applying any reading. It writes three data files, or compares them byte for byte if invoked with `--check`.
3. Use the page record’s `source_url` for the original PDF page. Coordinates in `line_bboxes_pt` are in PDF points measured from the top left in the page’s unrotated coordinate system. For checking separate OCR fragments or personnel entries, `line_ordinals` gives the source PDF’s original extraction order. A block groups the fragments into the printed paragraph, heading or personnel entry. Hashes in the collation address the complete PDF and the bytes of its native page image as returned by PyMuPDF.

An AI editor read the native scans, tested disagreements against a second OCR of the PR scans, and used the print image to choose a reading. This workflow includes text that agreed between machine readings. Independent human sign-off is pending. In the two-column technician roster (PR p. 102), the names are reassociated with their printed roles. In the Site 854 heading (PR p. 25), the scan supplies the part entirely omitted by the publisher text layer. Its block bounding box therefore extends beyond the embedded OCR line’s bounding box.

`source_lines` preserves source line order within a block and `text` supplies reflowed reading text. Interline spacing is normalized and a lexical hyphen at a line break is retained. PR p. 109 has two PDF line fragments for the same line of type, joined without a space at its restored degree sign. Therefore the source-line counts above describe addressable fragments. Relative line positions and typography remain available in the witness. The transcribed styles record individual underlined, italic, bold and raised/lowered strings where needed. Some formulas encode subscripts as Unicode characters. Line coordinates and in-block offsets address different things. Offsets count Unicode code points in the exact output string, starting at zero, with exclusive end.

`variants.csv` records changes to the publisher text layer. Two entries on the prospectus cover discard OCR marks from paper noise and a manuscript signature. The three manuscript signatures are visible in the witness. The associated typeset signatories are transcribed. Additional variants concern spelling, punctuation, formula typography, headings and identifier errors. When an apparent error is present in the original type, its printed form is retained. The [editorial notes](source_anomalies.csv) identify several such cases and give their PDF and line addresses.

Figure labels and captions, operation summary tables and site cards outside these page ranges have separate treatment elsewhere in the Leg 138 edition. These products and the content of the full source PDFs are outside the reported proofreading denominator. This batch represents one digital print witness for each document. Other editions and physical impressions require a separate comparison.

## Original publication notices

SP p. 2 permits copying for library, abstract service, educational and personal research uses. It calls for written consent from the ODP Director and acknowledgment for republication of any portion. PR p. 2 describes an informal shipboard report assembled under time constraints and carries the publisher’s warning that the material was privileged proprietary information and could not be used for publication or quotation. These are the notices in the two 1991 witnesses. The digitization and its software do not confer additional reuse rights. Consult the edition’s publisher and its present permissions for republication. [SP notice](https://www-odp.tamu.edu/publications/prosp/digital/138prosp.pdf#page=2) · [PR notice](https://www-odp.tamu.edu/publications/prelim/138PREL.PDF#page=2)
