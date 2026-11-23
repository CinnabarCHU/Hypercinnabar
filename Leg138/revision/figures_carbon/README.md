# Downhole carbonate and organic carbon in Initial Reports

Eleven vector figures follow the downhole carbon series in the eleven site chapters (21 panels). Percentages and ODP depth in mbsf come from the contemporaneous IR analytical tables. Depth in mcd is retained in the point ledger for comparison. CaCO₃ is reported as a calculated weight percentage. The organic-carbon method and the population plotted depend on the site. Site 851, for example, describes carbonate calculated from inorganic carbon and Corg determined in treated Coulometer residues on printed p.921.

[manifest.csv](manifest.csv) links each graphic to its code, its numerical table and the exact physical PDF page. [plot_layout.json](plot_layout.json) records the printed panel frames on a 950 × 1240 page grid, scales, symbols and caption lines. The digital drawings use Helvetica and Times as metrically practical substitutes, follow the original monochrome styles and retain printed chemistry subscripts. `points.csv.gz` preserves source lines, holes, sample identifiers, field literals, qualifiers, depth types and selection decisions. Site 854 only publishes carbonate in this figure.

**Site 846.** Figure 28 uses 318 carbonate and 147 organic-carbon values from Hole 846B. One organic-carbon value exceeds the printed 2% axis. Recreating the full range of source values and clipping the drawing to its original bounding box preserves both. The 437 interior vertices are all within five reference-grid pixels of print ink.

**Site 851.** Figure 33 contains 31 identifiable organic-carbon points. The chapter associates the profile with Table 12. The download includes 67 Corg values and a note about unpublished late additions. Core-section identity, depth and plotted concentrations support the 31-row subset in [figure33_organic_subset851.csv](figure33_organic_subset851.csv). These are section-2 samples, including the early shallow rows at 2.53, 10.13 and 19.53 mbsf. All 28 interior vertices of this subset fall within five pixels of print ink. The three edge vertices cannot be tested independently of border ink. All 67 values remain in the ledger. Removing carbonate rows from the inferred 36 excluded organic samples changes the two curve-distance metrics in opposite directions, so the carbonate redraw uses the full published numeric series. Its remaining differences are retained.

**Site 852.** Table 13 note a explicitly excludes 33 late additions from the historical figures. This leaves 11 Corg points. The annotation sits in the Corg column. We evaluated two carbonate selections against the printed curve separately. Omitting carbonate on those same 33 rows reduces the mean candidate-curve-to-scan-ink distance from 0.899 to 0.535 reference-grid pixels and the inverse distance from 0.685 to 0.674. Maximum forward distance falls from 10.30 to 4.12 pixels. The redraw uses those 154 carbonate rows. The associated carbonate omission is recorded as an inference. [carbonate_subset_comparison.csv](carbonate_subset_comparison.csv)

**Site 853.** The tabulated Corg at 6.83 mbsf is 0.009%. The printed symbol appears near 0.09%. The redraw uses 0.009% and shows the resulting change in profile shape. This symbol lies too close to the axis for the simple nearest-ink test to diagnose the discrepancy. At Site 847 one negative organic-carbon value is preserved and clipped at the printed zero axis.

`geometry_checks.csv.gz` and [geometry_summary.csv](geometry_summary.csv) independently compare each potential vertex against the scan. Of the 2,856 published numerical vertices selected and on-scale, 246 lie within eight pixels of a frame boundary. Among the other 2,610 vertices, 2,586 are within five pixels of scan ink and 24 fall farther away. The position test can also encounter connecting lines and dense nearby observations. It does not certify individual marker identity or the last digit of a published value. Marks are kept at the tabulated values. Table rounding, version-dependent row membership and small geometric offsets can all affect a match. Raw scan coordinates and output SHA-256 hashes are supplied for review.

Regenerate the plots and ledgers from the Leg138 directory using Python 3 and ReportLab.

```sh
python revision/figures_carbon/render.py
```

With the hash-matched IR chapter PDFs and chapter tables in the source directory, rerun the position and selection tests using PyMuPDF, Pillow, NumPy and SciPy.

```sh
python revision/figures_carbon/compare.py --sources /path/to/Leg138
```

[IR_Chemistry_Comparison_Atlas.pdf](IR_Chemistry_Comparison_Atlas.pdf) presents all 33 water and 11 carbon figures in site and source-page order. Each sheet juxtaposes a grayscale JPEG review crop of the original scan with the vector reconstruction, its scope note, and a link to the source PDF page. The two embedded plots use a common page grid. The separate reconstructed PDFs retain vector text and paths. Rebuild the atlas with `python revision/figures_carbon/build_atlas.py --sources /path/to/Leg138`.

The per-sample compressed ledgers are generated by the scripts above. They are also included in the offline edition under `revision_evidence/`. The public figure files, source identifiers and numerical summaries can be inspected independently.
