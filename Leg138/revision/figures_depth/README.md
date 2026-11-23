# Shipboard sedimentation rates, Sites 844–854

[Compare all 22 originals and redraws](Sedimentation_Rate_Comparison.pdf). Each published station chapter contains one rate profile against age and a second against composite depth. The figures use the reported interval rates and the control points in the associated printed and distributed tables.

The 22 PDFs in [plots](plots) contain selectable labels and vector profiles. Serif captions retain the wording and line breaks in the printed figures. Axis titles and ticks use Helvetica and the captions use Times Roman. The frame dimensions, axis ranges, tick spacing, title orientation and caption position come from visual inspection of each print figure and are recorded in [layout.json](layout.json). The charts are independent reconstructions; their black traces are generated exclusively from numeric data.

## Sources and editorial decisions

[manifest.csv](manifest.csv) identifies the figure, table, physical PDF page, source links, input/output hashes and the evidence for each comparison. Eleven original TABLE byte streams can be reconstructed from the coordinate-preserving native lines already in the repository. The render step checks all eleven byte hashes before parsing.

[intervals.csv](intervals.csv) preserves 229 control-point intervals, with each upper anchor, lower anchor and rate tied to its original line number. The reported rate and the independently calculated depth increment divided by the age increment occupy separate columns. The profile always uses the reported value. The original tables use three distinct layouts. Some list the rates between anchor rows, most put the rate on the lower anchor, and Site 854 puts it on the upper anchor.

Site 845's electronic column headings reverse age and rate. The printed headings and tabulated positions resolve their meaning. The printed age at 166.83 mcd is 10.59 Ma, against 10.51 Ma in the electronic file. The editions preserve that difference. Site 844's composite-depth chart carries the original y-axis label “Depth (mbsf)”. Site 849's graphs omit the last fully tabulated interval. Site 854 has a blank forward rate at 47.47 mcd. Its last reported rate has no following endpoint and is retained in [unbounded_rates.csv](unbounded_rates.csv).

The per-figure outcomes are given in [observations.csv](observations.csv): eight figures consistent on the tested plateaus, five with small print differences, five with material differences, three with a documented restriction of the printed extent and one with a missing interval rate. A printed trace that diverges from its cited table is preserved alongside the independent table reconstruction. At Site 850 the table gives 122.00 m/m.y. outside the original 0–120 rate frame; the segment is present in the source data and clipped by the same frame in the redraw.

## Print comparison

[scan_comparison.csv](scan_comparison.csv) summarizes 14,509 plateau probes. [interval_comparison.csv](interval_comparison.csv) lists the eligible intervals individually. The source is rendered to grayscale at three pixels per PDF point. Each probe samples the interior of a table-supported vertical plateau, leaving two points away from each end, and measures the distance to the nearest dark scan pixel in a three-row window. The acceptable horizontal distance is 1.25% of the full rate-axis range. The frame edges and tick regions are masked. A scan match indicates local visual agreement. This one-way test cannot detect extra ink, independently resolve very short segments, or prove identity of the historical plotting code. Outside-frame, missing and ineligible intervals do not contribute to the percentages. The paired comparison PDF allows direct inspection of all figures including the excluded portions.

## Rebuild

Run these commands from the Leg138 directory. The renderer works offline with the files in the branch. For the optional comparison and atlas, SOURCE_ROOT must contain the original source PDFs at ir/primary/VOLUME/CHAPTERS. The comparison checks each original PDF hash.

```sh
python revision/figures_depth/render.py --out /tmp/rate-redraws
python revision/figures_depth/compare.py SOURCE_ROOT --out /tmp/rate-redraws
python revision/figures_depth/publish.py SOURCE_ROOT --out /tmp/rate-redraws
```

The output was verified with ReportLab 4.4.9, PyMuPDF 1.26.6 and NumPy 2.3.5. Two runs produced identical bytes for all 28 outputs. The 22 one-page redraws contain vector paths and text, with selectable complete captions and zero raster images. Each of the 22 comparison pages provides a link to the publisher's original page.
