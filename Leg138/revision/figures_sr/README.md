# Scientific Results figure reconstruction

The 18 single-page PDFs in [pdf/](pdf/) draw scientific marks directly from five author-distributed numerical tables. [comparison.pdf](comparison.pdf) places each reconstruction beside the original printed figure and its caption. All 18 reconstruction PDFs contain vector marks and embedded text. The left column of the comparison book is a cropped facsimile.

| Chapter | Figures | Numerical witness and processing |
| --- | --- | --- |
| Shackleton, Hall & Pate, Site 846 | 1, 2 | Table 3. All individual analyses with a usable revised composite depth and adjusted isotope value in the plotted interval; repeated analyses remain separate. Five depth panels of 40 m each. |
| Shackleton, Hall & Pate, Site 846 | 5, 6 | Table 5. The authors’ selected and replicate-averaged isotope values, with their assigned ages. Six age panels of 1 Myr each. |
| Farrell et al., Site 847 | 2 | Appendix B. Three laboratory series of opal weight percentage, with the original distinction between lines and filled squares. |
| Farrell et al., all 11 sites | 5–8 | Appendix C. Abundance, preservation, etching and overgrowth scores connected in publication order. |
| Farrell et al., all 11 sites | 9–14 | Appendices A and B. Published carbonate, opal and estimated terrigenous percentages and mass accumulation rates, including the open Site 854 hiatus. MAR is a computed product in the original publication. |
| Farrell et al., Sites 845, 844, 846, 849 | 15 | Appendix A. Percent carbonate and carbonate MAR use a centered five-record moving mean. |
| Farrell et al., Sites 846 and 850 | 26, 27 | Appendices A and B. Opal MAR and its age-bin histogram, followed by six concentration, density, rate and flux panels. |

## Editorial evidence

**Site 846 isotope fields.** The results prose of Chapter 15 (printed p. 339) calls the carbon series in Figure 2 “raw”. Table 3 distinguishes raw, species-adjusted and selected columns. In the print’s coordinate system, 99.70% of 2,294 adjusted carbon values lie within two display pixels of ink, compared with 34.69% of 2,661 raw carbon values. The median raw-field distance is 9 px. The oxygen diagnostic for Figure 1 favors the adjusted values as well (99.21% of 2,653 adjusted, 70.69% of 2,661 raw). Coordinates coincide with printed text, axes and neighboring marks in some cases. These tests evaluate which published field accounts for the cloud overall. They cannot identify every individual printed dot. Figures 5 and 6 use the separate, author-averaged Table 5 age series. The plotted age range excludes older values that occur in the full distributed table.

**One decimal reading resolved against print.** Table 3, analysis P91/2374, 846B-7H-3, 124–126 cm, 67.030 rmcd, carries the string `--0.19` in the adjusted carbon column of CD lines 82–83. The actual print visibly gives −0.19 for both raw and adjusted carbon on PDF page 4, printed p. 340. The duplicate sample label on the line above belongs to analysis P91/2373 and carries different values. The drawing selector reads P91/2374 as −0.19 and leaves the distributed record untouched. [Printed Table 3](https://www-odp.tamu.edu/publications/138_SR/VOLUME/CHAPTERS/sr138_15.pdf#page=4)

**Gaussian guide curves.** Figures 1 and 2 specify 0.10 m output spacing and 0.5999 m full window. Figures 5 and 6 specify 0.003 Ma and 0.00899 Ma. We evaluate a weighted mean of the published values in that support, with sigma equal to one sixth of the full window, and leave an empty window as a gap. The separately published Table 7 corresponds to the smaller 5.99 kyr analytical window. Testing seven kernel shapes against those distributed numerical values favors σ = full width / 6. On 1,085 multi-input oxygen gridpoints and 950 carbon gridpoints, respectively 87.93% and 86.95% fall within 0.006‰ of the tabulated values under this kernel, versus 36.77% and 36.84% for width / 4. A simple in-window availability rule differs from the author’s analytical missing-code mask in 59 oxygen and 93 carbon rows out of 1,463. The test supports the width ratio. Its transfer to the printed guides and the grid origins (60 m and 1.763 Ma) remain reconstruction choices. [Numerical filter comparison](kernel_calibration.json) The numerical ink diagnostic for the four isotope figures measures the point layer. The historical guide curves have not been exactly reconstructed.

**Site 847 opal.** Figure 2 shows ages through 3.0 Ma. Appendix B contains 655 Murray, 63 Janecek and 10 Levitan records in this window. Farrell et al. report 62 Janecek records in their top-98-m calculation. The 63rd record falls at 98.28 mcd and 2.993 Ma. Both counts are recoverable. Numeric suffix `s` means the author flagged a suspect value. The plotting layer keeps the value with that flag in the source. Appendix B records 940 and 2052 use the field alignments supported by the pre-existing row apparatus.

**Site 854 and the stacked series.** Appendix C spans the age jump from 3.988 to 5.478 Ma, Appendix A from 3.275 to 6.015 Ma, Appendix B from 3.275 to 6.150 Ma. Their lines stop and restart at the respective real observations. For Figure 9 the Site 854 polyline lies about three 1.25× display pixels left of the coordinates predicted by the common age axis in part of the original. Keeping the common age axis gives 76.04% proximity to ink for that site. The renderer keeps every site's age unchanged. Individual vertical translations and scales in the stacked composite approximate the print; original annotations and caption are independently typeset. Text uses DejaVu Sans, the captions DejaVu Serif. Different text metrics account for small placement and wrapping differences.

**Five-point means.** Figure 15 specifies a five-point moving average. The centered, equal-weight reconstruction yields 96.49–100% near-ink agreement across eight curves, with the full unfiltered series retained. Figure 26 explicitly specifies the same moving average; its inset matches sample-wise arithmetic means in bins [0,1), [1,2), …, [11,12) Ma. These calculations weight each published row once. Figure 27’s caption does not specify the filter. The six-panel reconstruction uses the corresponding five-point mean, Appendix A for its LSR, CaCO₃, CaCO₃ MAR and dry bulk density fields and Appendix B for opal and opal MAR. Source-ink agreement across its twelve traces is 92.55–100.00% using the declared two-pixel comparison; [validation.json](validation.json) includes the unsmoothed alternative.

## Rebuild and inspect

From the Leg138 directory, run

```sh
python revision/figures_sr/redraw.py
python revision/figures_sr/verify.py /path/to/source-directory --comparison
```

The redraw uses only NumPy, Matplotlib and checked local catalogue rows. Verification additionally needs PyMuPDF, Pillow and SciPy. The source directory must contain `sr/primary/official/VOLUME/CHAPTERS/` and `sr/primary/official/VOLUME/DATA/`. All relevant numerical witnesses and the two chapter PDF witnesses are checked against SHA-256 before comparing pixels. In [manifest.csv](manifest.csv), each figure includes the figure ID, exact original page, data source, dataset IDs, selected columns, source and output hashes, and relative recipe and PDF paths. The deposited originals and their separate editions remain individually identifiable.

[farrell_layout.json](farrell_layout.json) records the publication-space calibrations and the figure/siting labels. They position the curves; all heights and sample ages come from the numerical records. [verify.py](verify.py) samples these paths and reports proximity to any original dark ink with a displaced-curve control. Vertical coordinates were calibrated against the same scanned chart. This is a descriptive registration check, not an out-of-sample accuracy statistic or an exact match of historic type and pen strokes. Source scans occur only in the visual comparison book. The scientific PDF layers can be regenerated without them.
