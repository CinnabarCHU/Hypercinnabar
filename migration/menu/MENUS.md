# 按 Acycle 菜单查找接口

基于 master 的主窗口顺序；同一条目下的 GUIDE 选择值以 `_legacy` 结尾。表中 `X (两版)` 可展开为 `X` 和 `X_legacy`。只有某一版的选择逐字列出。前缀接 `_helper`、`_analyzer` 或 `_plotter`，具体角色见对应行。菜单标题只承担分组。验证脚本、核函数和输入示例列在对应菜单下，表示可独立调用的附属操作。

[调用与复现示例](README.zh-CN.md) · [完整机器清单](../../code/interface/catalogue.json)

## File

| 菜单路径及状态 | 公开函数前缀 / 角色 | 默认选择 | 全部 params.operation |
|---|---|---|---|
| File | 菜单标题 | — | — |
| File > New Folder | `acMenuFolder` · helper / plotter | Desktop | `Desktop` (两版) |
| File > New Text File | `acMenuNewtxt` · helper / plotter | Desktop | `Desktop` (两版) |
| File > Create Data Table | `acMenuNewDataTable` · helper / plotter | Desktop | `Desktop` (两版) |
| File > Save *.AC.fig | `acMenuSavefig` · helper / plotter | Desktop | `Desktop` (两版) |
| File > Extract Data | `acMenuExtract` · helper / analyzer / plotter | Columns | `Columns` (两版), `Desktop` (两版) |
| File > Open Directory（GUI 隐藏） | `acMenuOpendir` · helper / plotter | Desktop | `Desktop` (两版) |

## Edit

| 菜单路径及状态 | 公开函数前缀 / 角色 | 默认选择 | 全部 params.operation |
|---|---|---|---|
| Edit | 菜单标题 | — | — |
| Edit > Refresh | `acMenuRefreshlist` · helper / analyzer / plotter | Desktop | `Desktop` (两版), `ac_sort_dir_entries`, `strrep2` |
| Edit > Rename | `acMenuRename` · helper / plotter | Desktop | `Desktop` (两版) |
| Edit > Cut | `acMenuCut` · helper / plotter | Desktop | `Desktop` (两版) |
| Edit > Copy | `acMenuCopy` · helper / plotter | Desktop | `Desktop` (两版) |
| Edit > Paste | `acMenuPaste` · helper / plotter | Desktop | `Desktop` (两版) |
| Edit > Delete | `acMenuDelete` · helper / plotter | Desktop | `Desktop` (两版) |

## Plot

| 菜单路径及状态 | 公开函数前缀 / 角色 | 默认选择 | 全部 params.operation |
|---|---|---|---|
| Plot | 菜单标题 | — | — |
| Plot > Plot | `acMenuPlot` · helper / plotter | SimplePlot | `Desktop` (两版), `SimplePlot` (两版) |
| Plot > Plot Pro | `acMenuPlotpro2d` · helper / plotter | PlotPro | `Desktop` (两版), `PlotPro` (两版) |
| Plot > Plot Adv | `acMenuPlotadv` · helper / plotter | PlotAdv | `Desktop` (两版), `PlotAdv` (两版) |
| Plot > Plot Standardized | `acMenuPlotn` · helper / analyzer / plotter | SimplePlot | `Desktop` (两版), `SimplePlot` (两版), `Standardize` (两版) |
| Plot > Plot Standardized + 2 | `acMenuPlotn2` · helper / analyzer / plotter | SimplePlot | `Desktop` (两版), `SimplePlot` (两版), `Standardize` (两版) |
| Plot > Sampling Rate | `acMenuSamplerate` · helper / analyzer / plotter | SamplingRate | `Desktop` (两版), `SamplingRate` (两版), `SamplingGrid` |
| Plot > Data Distribution | `acMenuDatadistri` · helper / plotter | DataDistribution | `DataDistribution` (两版), `Desktop` (两版) |
| Plot > Convert to sound | `acMenuSound` · helper / analyzer / plotter | SeriesSound | `Desktop` (两版), `SeriesSound` (两版) |

## Basic Series

| 菜单路径及状态 | 公开函数前缀 / 角色 | 默认选择 | 全部 params.operation |
|---|---|---|---|
| Basic Series | 菜单标题 | — | — |
| Basic Series > Insolation | `acMenuInsol` · helper / analyzer / plotter | insoML | `Desktop` (两版), `InsolLatDayGif` (两版), `ellipse_s` (两版), `insoML` (两版), `mmdd2dayi` (两版), `monthday2dayi` (两版), `Insolation_legacy` |
| Basic Series > Astronomical Solution | `acMenuLaskar` · helper / analyzer / plotter | AstronomicalSolution | `AstronomicalSolution` (两版), `Desktop` (两版) |
| Basic Series > Milankovitch Calculator | `acMenuLOD` · helper / analyzer / plotter | MilankovitchCal | `Desktop` (两版), `MilankovitchCal` (两版), `getBerger89Period` (两版), `lodla04` (两版), `calculate_orbit9` |
| Basic Series > Signal/Noise Generator | `acMenuLinegenerator` · helper / analyzer / plotter | SeriesGenerator | `Desktop` (两版), `SeriesGenerator` (两版), `redmark` (两版) |
| Basic Series > LR04 Stack | `acMenuLR04` · helper / analyzer / plotter | LR04 | `Desktop` (两版), `LR04` (两版) |
| Basic Series > CENOGRID | `acMenuCenogrid` · helper / analyzer / plotter | CENOGRID | `CENOGRID` (两版), `Desktop` (两版) |
| Basic Series > Examples | 菜单标题 | — | — |
| Basic Series > Examples > Mauna Loa CO2 monthly mean | `acMenuExampleHawaiiCO2` · helper / analyzer / plotter | ExampleMaunaLoa | `Desktop` (两版), `ExampleMaunaLoa` (两版) |
| Basic Series > Examples > Insolation 0-2Ma 65N Jun22 | `acMenuExampleInso2Ma` · helper / analyzer / plotter | ExampleInsolation | `Desktop` (两版), `ExampleInsolation` (两版) |
| Basic Series > Examples > La2004 0-2Ma ETP | `acMenuExampleLa04etp` · helper / analyzer / plotter | ExampleLa2004 | `Desktop` (两版), `ExampleLa2004` (两版) |
| Basic Series > Examples > Red Noise rho=0.7 2000 points | `acMenuExampleRedp7` · helper / analyzer / plotter | ExampleRedNoise | `Desktop` (两版), `ExampleRedNoise` (两版) |
| Basic Series > Examples > PETM Svalbard logFe | `acMenuExamplePETM` · helper / analyzer / plotter | ExampleSvalbardPETM | `Desktop` (两版), `ExampleSvalbardPETM` (两版) |
| Basic Series > Examples > Late Triassic Newark Depth Rank | `acMenuExampleNewark` · helper / analyzer / plotter | ExampleNewark | `Desktop` (两版), `ExampleNewark` (两版) |
| Basic Series > Examples > Late Triassic Wayao gamma ray | `acMenuExampleWayao` · helper / analyzer / plotter | ExampleWayao | `Desktop` (两版), `ExampleWayao` (两版) |
| Basic Series > Examples > Middle Triassic Guandao2 gamma ray | `acMenuExampleGD2GR` · helper / analyzer / plotter | ExampleGuandao | `Desktop` (两版), `ExampleGuandao` (两版) |
| Basic Series > Examples > Image from Mars'' HiRISE camera | `acMenuExampleMarsimage` · helper / analyzer / plotter | ExampleMars | `Desktop` (两版), `ExampleMars` (两版) |
| Basic Series > Examples > Image Sphalerite | `acMenuExampleSphalerite` · helper / analyzer / plotter | ExampleSphalerite | `Desktop` (两版), `ExampleSphalerite` (两版) |
| Basic Series > Examples > Image for Plot Digitizer | `acMenuExamplePlotdigitizer` · helper / analyzer / plotter | ExampleDigitizer | `Desktop` (两版), `ExampleDigitizer` (两版) |
| Basic Series > Examples > Example extinction | `acMenuExtinctionCSA` · helper / analyzer / plotter | ExampleExtinction | `Desktop` (两版), `ExampleExtinction` (两版) |

## Math

| 菜单路径及状态 | 公开函数前缀 / 角色 | 默认选择 | 全部 params.operation |
|---|---|---|---|
| Math | 菜单标题 | — | — |
| Math > Sort/Unique/Delete-empty | `acMenuSort` · helper / analyzer / plotter | SortUnique | `Desktop` (两版), `SortUnique` (两版), `datapreproc` (两版), `findduplicate` (两版) |
| Math > Interpolation | `acMenuInterp` · helper / analyzer / plotter | interpolate | `Desktop` (两版), `interpolate` (两版), `interpolate_rand` (两版), `RegularInterpolation` |
| Math > Interpolation Pro | `acMenuInterpolationGUI` · helper / analyzer / plotter | InterpolationPro | `Desktop` (两版), `InterpolationPro` (两版) |
| Math > Interpolate Series | `acMenuInterpseries` · helper / analyzer / plotter | InterpolateSeries | `Desktop` (两版), `InterpolateSeries` (两版) |
| Math > Select Parts | `acMenuSelectinterval` · helper / analyzer / plotter | select_interval | `Desktop` (两版), `select_interval` (两版) |
| Math > Remove Parts | `acMenuDesection` · helper / analyzer / plotter | RemoveSections | `Desktop` (两版), `RemoveSections` (两版) |
| Math > Add Gaps | `acMenuGap` · helper / analyzer / plotter | AddGaps | `AddGaps` (两版), `Desktop` (两版) |
| Math > Remove Peaks | `acMenuDepeaks` · helper / analyzer / plotter | depeaks | `Desktop` (两版), `depeaks` (两版) |
| Math > Clipping | `acMenuClip` · helper / analyzer / plotter | Clipping | `Clipping` (两版), `Desktop` (两版) |
| Math > Column Manipulate | `acMenuColman` · helper / analyzer / plotter | ColumnManipulation | `ColumnManipulation` (两版), `Desktop` (两版) |
| Math > Merge Series | `acMenuAdd` · helper / analyzer / plotter | MergeSeries | `Desktop` (两版), `MergeSeries` (两版) |
| Math > Multiply Series | `acMenuMultiply` · helper / analyzer / plotter | MultiplySeries | `Desktop` (两版), `MultiplySeries` (两版) |
| Math > Data Transformations | `acMenuDatatransf` · helper / analyzer / plotter | DataTransform | `DataTransform` (两版), `Desktop` (两版), `Log10` (两版), `Standardize` (两版), `boxcoxML` (两版) |
| Math > Simple Function | `acMenuFunction` · helper / analyzer / plotter | SimpleFunction | `Desktop` (两版), `SimpleFunction` (两版) |
| Math > Derivative | `acMenuDerivative` · helper / analyzer / plotter | Derivative | `Derivative` (两版), `Desktop` (两版) |
| Math > Find Max/Min | `acMenuMaxmin` · helper / analyzer / plotter | Extrema | `Desktop` (两版), `Extrema` (两版), `findnpk` (两版), `getpks` (两版) |
| Math > Changepoint | `acMenuCpt` · helper / analyzer / plotter | bayes_cpt | `Desktop` (两版), `bayes_cpt` (两版), `bayes_cpt_r2` (两版), `nCk` (两版), `partition_fn` (两版), `pick_k1` (两版) |
| Math > Principal Component | `acMenuPca` · helper / analyzer / plotter | PCA | `Desktop` (两版), `PCA` (两版) |
| Math > Image | 菜单标题 | — | — |
| Math > Image > Show Image | `acMenuImshow` · helper / plotter | ShowImage | `Desktop` (两版), `ShowImage` (两版), `imscrollpanel_ac` (两版) |
| Math > Image > RGB to Grayscale | `acMenuRgb2gray` · helper / analyzer / plotter | RGBToGray | `Desktop` (两版), `RGBToGray` (两版) |
| Math > Image > RGB to CIE Lab | `acMenuRgb2lab` · helper / analyzer / plotter | RGBToLab | `Desktop` (两版), `RGBToLab` (两版) |
| Math > Image > Image Profile | `acMenuImprofile` · helper / analyzer / plotter | ImageTransect | `Desktop` (两版), `ImageProfile` (两版), `ImageTransect` (两版) |
| Math > Plot Digitizer | `acMenuDigitizer` · helper / analyzer / plotter | Digitize | `Desktop` (两版), `Digitize` (两版), `DigitizeTrace` (两版) |
| Math > menu_log10（GUI 隐藏） | `acMenuLog10` · helper / analyzer / plotter | Log10 | `Log10` (两版), `Desktop` |
| Math > menu_norm（GUI 隐藏） | `acMenuNorm` · helper / analyzer / plotter | Standardize | `Standardize` (两版), `Desktop` |
| Math > menu_utilities（GUI 隐藏） | 菜单标题 | — | — |

## Univariate

| 菜单路径及状态 | 公开函数前缀 / 角色 | 默认选择 | 全部 params.operation |
|---|---|---|---|
| Univariate | 菜单标题 | — | — |
| Univariate > Stat Summary | `acMenuStatsummary` · helper / analyzer / plotter | SummaryStatistics | `CE_NS70` (两版), `Desktop` (两版), `SummaryStatistics` (两版), `invprctile` (两版) |
| Univariate > t-Test | `acMenuTtest` · helper / analyzer / plotter | OneSampleT | `Desktop` (两版), `OneSampleT` (两版) |

## Bivariate

| 菜单路径及状态 | 公开函数前缀 / 角色 | 默认选择 | 全部 params.operation |
|---|---|---|---|
| Bivariate | 菜单标题 | — | — |
| Bivariate > 1-2 Sample Test | `acMenuUni2SamTest` · helper / analyzer / plotter | TwoSampleTests | `AnDarksamtest` (两版), `Desktop` (两版), `TwoSampleTests` (两版) |
| Bivariate > ANOVA | `acMenuAnova` · helper / analyzer / plotter | ANOVA | `ANOVA` (两版), `Desktop` (两版) |
| Bivariate > Normality Test | `acMenuNormaltest` · helper / analyzer / plotter | Normality | `Desktop` (两版), `Normality` (两版), `swtest` (两版) |
| Bivariate > Chi-square GOF | `acMenuChi2gof` · helper / analyzer / plotter | DistributionTest | `Desktop` (两版), `DistributionTest` (两版) |
| Bivariate > Correlation | `acMenuCorr` · helper / analyzer / plotter | Correlation | `Correlation` (两版), `Desktop` (两版) |
| Bivariate > Covariance | `acMenuCovariance` · helper / analyzer / plotter | Covariance | `Covariance` (两版), `Desktop` (两版) |
| Bivariate > Linear Regression | `acMenuLinearReg` · helper / analyzer / plotter | LinearRegression | `Desktop` (两版), `LinearRegression` (两版) |

## Multivariate

| 菜单路径及状态 | 公开函数前缀 / 角色 | 默认选择 | 全部 params.operation |
|---|---|---|---|
| Multivariate（GUI 隐藏） | 菜单标题 | — | — |

## Timeseries

| 菜单路径及状态 | 公开函数前缀 / 角色 | 默认选择 | 全部 params.operation |
|---|---|---|---|
| Timeseries | 菜单标题 | — | — |
| Timeseries > Detrending \| Curve Fitting | `acMenuPrewhiten` · helper / analyzer / plotter | Detrending | `Desktop` (两版), `DetrendSignalPP` (两版), `Detrending` (两版) |
| Timeseries > Smoothing | 菜单标题 | — | — |
| Timeseries > Smoothing > Bootstrap | `acMenuBootstrap` · helper / analyzer / plotter | BootstrapSmooth | `BootstrapSmooth` (两版), `Desktop` (两版), `smoothbestSpan` (两版), `smoothbestSpanRand` (两版), `smoothci` (两版), `smoothciML` (两版) |
| Timeseries > Smoothing > Moving Average | 菜单标题 | — | — |
| Timeseries > Smoothing > Moving Average > Fixed Bandwidth | `acMenuMovmeanfbw` · helper / analyzer / plotter | FixedMovingMean | `Desktop` (两版), `FixedMovingMean` (两版), `movmeanfbw` (两版) |
| Timeseries > Smoothing > Moving Average > Fixed Count (K-point) | `acMenuSmooth` · helper / analyzer / plotter | MovingMean | `Desktop` (两版), `MovingMean` (两版), `movemean` (两版) |
| Timeseries > Smoothing > Moving Median | 菜单标题 | — | — |
| Timeseries > Smoothing > Moving Median > Fixed Bandwidth | `acMenuMovmedianfbw` · helper / analyzer / plotter | FixedMovingMedian | `Desktop` (两版), `FixedMovingMedian` (两版) |
| Timeseries > Smoothing > Moving Median > Fixed Count (K-point) | `acMenuMovmedian` · helper / analyzer / plotter | MovingMedian | `Desktop` (两版), `MovingMedian` (两版), `moveMedian` (两版) |
| Timeseries > Smoothing > Moving Gaussian | `acMenuMovGauss` · helper / analyzer / plotter | MovingGaussian | `Desktop` (两版), `MovingGaussian` (两版) |
| Timeseries > Pre-whitening | `acMenuWhiten` · helper / analyzer / plotter | AR1Prewhitening | `AR1Prewhitening` (两版), `Desktop` (两版), `prewhitening` (两版) |
| Timeseries > Spectral Analysis | `acMenuPower` · helper / analyzer / plotter | PowerSpectrum | `Desktop` (两版), `PowerSpectrum` (两版), `SWA` (两版), `SpectralBendingPowerLaw` (两版), `SpectralPowerLaw` (两版), `ftestmtm` (两版), `ftestmtmML` (两版), `minirho` (两版), `minirhos0` (两版), `mtmdofs` (两版), `plomb_robustar1` (两版), `redconfML` (两版), `redconf_any` (两版), `redconfchi2` (两版), `redconftabtchi` (两版), `spectralswafdr` (两版), `MtmTaperCount` |
| Timeseries > Spectral Analysis (SWA) | `acMenuSwa` · helper / analyzer / plotter | SWA | `Desktop` (两版), `SWA` (两版), `gammcf` (两版), `gammln` (两版), `gammp` (两版), `gamser` (两版), `getchi2` (两版), `hpsort` (两版), `period` (两版), `rho` (两版), `solve` (两版), `specswa` (两版), `spectralswafdr` (两版), `strAssign` (两版) |
| Timeseries > Evolutionary Spectral Analysis | `acMenuPeriod` · helper / analyzer / plotter | EvolutionarySpectrum | `Desktop` (两版), `EvolutionarySpectrum` (两版), `evofft` (两版), `evofftML` (两版), `evoperiodogram` (两版), `evoplomb` (两版), `evopmtm` (两版), `evopmtmML` (两版), `zeropad2` (两版), `EvolutionaryWorkbook` |
| Timeseries > Wavelet | `acMenuWaveletGUI` · helper / analyzer / plotter | WaveletSpectrum | `Desktop` (两版), `MatlabWaveletCoherence` (两版), `WaveletCoherence` (两版), `WaveletSpectrum` (两版), `ar1nv` (两版), `ar1spectrum` (两版), `boxpdf` (两版), `chisquare_inv` (两版), `chisquare_solve` (两版), `formatts` (两版), `rednoise` (两版), `smoothwavelet` (两版), `wave_bases` (两版), `wave_signif` (两版), `wavelet` (两版), `wtcsignif` (两版) |
| Timeseries > Circular Spectral Analysis | `acMenuCSA` · helper / analyzer / plotter | CircularSpectrum | `CircularSpectrum` (两版), `Desktop` (两版), `circularspec` (两版) |
| Timeseries > Bispectral Analysis | `acMenuBispectral` · helper / analyzer / plotter | Bispectral | `Bispectral`, `BispectralExport`, `BispectralView`, `Desktop`, `bispectralEstimate`, `bispectralLocalDataValidation`, `bispectralPreprocess`, `bispectralReadDataFile`, `bispectralSelfTest`, `bispectralSignificance`, `bispectralSurrogate`, `bispectralValidateExamples` |
| Timeseries > Recurrence Plot | `acMenuRecplot` · helper / analyzer / plotter | Recurrence | `Desktop` (两版), `Recurrence` (两版), `crp_core` (两版), `crp_pdist` (两版), `dl_all` (两版), `recplot` (两版) |
| Timeseries > Coherence & Phase | `acMenuCoh` · helper / analyzer / plotter | Coherence | `Coherence` (两版), `Desktop` (两版), `cohac` (两版) |
| Timeseries > Lead-lag Relationship | `acMenuLeadlag` · helper / analyzer / plotter | LeadLag | `Desktop` (两版), `rmse4leadlag` (两版), `LeadLag` |
| Timeseries > Filtering | `acMenuFilter` · helper / analyzer / plotter | Bandpass | `Bandpass` (两版), `Desktop` (两版), `PassFilter` (两版), `gaussfilter` (两版), `gaussmf` (两版), `tanerhilbertML` (两版) |
| Timeseries > Dynamic Filtering | `acMenuDynfilter` · helper / analyzer / plotter | DynamicFiltering | `Desktop` (两版), `DynamicFiltering` (两版), `dynamic_filter`, `dynamic_filter_lang` |
| Timeseries > Empirical Mode Decomposition | 菜单标题 | — | — |
| Timeseries > Empirical Mode Decomposition > Empirical Mode Decomposition (EMD) | `acMenuEmd` · helper / analyzer / plotter | EMD | `Desktop` (两版), `EMD` (两版), `emdNL` (两版), `find_extrema` (两版) |
| Timeseries > Empirical Mode Decomposition > Ensemble Empirical Mode Decomposition (EEMD) | `acMenuEemd` · helper / analyzer / plotter | EnsembleEMD | `Desktop` (两版), `EnsembleEMD` (两版), `eemd` (两版), `find_extrema` (两版) |
| Timeseries > Amplitude Modulation | `acMenuAM` · helper / analyzer / plotter | AmplitudeModulation | `AmplitudeModulation` (两版), `Desktop` (两版) |
| Timeseries > Build Age Model | `acMenuAgebuild` · helper / analyzer / plotter | BuildAgeModel | `BuildAgeModel` (两版), `Desktop` (两版) |
| Timeseries > Sed. Rate to Age Model | `acMenuSr2age` · helper / analyzer / plotter | SedimentationRateToAge | `Desktop` (两版), `SedimentationRateToAge` (两版) |
| Timeseries > Undatable | `acMenuUndatable` · helper / analyzer / plotter | Undatable | `Desktop` (两版), `Undatable` (两版) |
| Timeseries > Age Scale \| Tuning | `acMenuAge` · helper / analyzer / plotter | AgeScale | `AgeScale` (两版), `Desktop` (两版), `depthtotime` (两版), `domaintrans` (两版) |
| Timeseries > Stratigraphic Correlation | `acMenuCorrelation` · helper / analyzer / plotter | StratigraphicCorrelation | `Desktop` (两版), `StratigraphicCorrelation` (两版) |
| Timeseries > Power Decomposition Analysis | `acMenuPda` · helper / analyzer / plotter | PowerDecomposition | `Desktop` (两版), `PowerDecomposition` (两版), `pda` (两版) |
| Timeseries > Sedimentary Noise Model | 菜单标题 | — | — |
| Timeseries > Sedimentary Noise Model > Dynamic noise after orbital tuning (DYNOT) | `acMenuDynos` · helper / analyzer / plotter | DYNOT | `DYNOT` (两版), `Desktop` (两版), `pdan` (两版), `dynotIterationWorker`, `dynotPercentilePlan` |
| Timeseries > Sedimentary Noise Model > Lag-1 autocorrelation coefficient (\rho1) | `acMenuRho` · helper / analyzer / plotter | Lag1 | `Desktop` (两版), `Lag1` (两版), `Lag1MonteCarlo` (两版), `erhoAR1` (两版), `rhoAR1` (两版), `rhoAR1ML` (两版), `Lag1V2MonteCarlo_legacy`, `Lag1V2_legacy`, `calculateRhoM` |
| Timeseries > Correlation Coefficient (COCO/eCOCO) | `acMenuEcoco` · helper / analyzer / plotter | ecoco | `Desktop` (两版), `corrcoefsig` (两版), `corrcoefslices` (两版), `corrsig` (两版), `cyclecorr` (两版), `cyclecorr4` (两版), `cyclecorr4sig` (两版), `cyclecorr5` (两版), `cyclecorr_rank` (两版), `cyclesig_rank` (两版), `data_slices` (两版), `ebrief` (两版), `eccount` (两版), `eccpeaks` (两版), `ecoco` (两版), `ecocoplot` (两版), `ecocoplots` (两版), `ecocos` (两版), `ecocotrack` (两版), `ecocotrackn` (两版), `findperct` (两版), `gentarget` (两版), `norbits` (两版), `numorbit` (两版), `period2spectrum` (两版), `randspec_sin` (两版), `targetadj_real` (两版), `targetrebuilt` (两版), `theoredar1ML` (两版), `cocoAdaptiveEvaluate`, `cocoAdaptivePublicationReport`, `cocoAllPeriodRateRange`, `cocoConclusionReport`, `cocoFixedTargetWeights`, `cocoGetPower`, `cocoGetPowerNew`, `cocoIsNonfatalResolutionError`, `cocoNonnegativeLeakageSolve`, `cocoOrbitGroups`, `cocoPrepareRegularData`, `cocoPublicationPrepareData`, `cocoResolvedDetrendedVariance`, `cocoSamplingTolerance`, `cocoTargetSpectrum`, `corrcoefslices_rankNew`, `corrcoefslices_rank_legacy`, `cvcoco`, `cvcoco2`, `cvcoco9`, `cvcoco9A`, `cvcoco9B`, `cvcocoLegacy`, `cyclecorrNew`, `cyclecorrsigNew`, `cyclecorrsig_legacy`, `ecocoAdaptiveCore`, `ecocoCrossfitCore`, `ecocoEstimateAr1`, `ecocoInterleavedCore`, `ecocoPhysicalCenters`, `ecocoPhysicalWindowValues`, `ecocoWindowSpectra`, `freq2targetFixed`, `freq2targetNew`, `freq2target_legacy`, `interleavedcvcoco`, `period2spectrumB_legacy`, `plotAdaptiveCocoPublication`, `plotcvcoco`, `redNoisePeriodogramMC`, `reexportCocoPublicationPdfs`, `runCocoEightMethodExperiment`, `runCocoPublicationValidation`, `runEcocoTwoMethodExperiment`, `runInterleavedCvCocoComparison`, `runSyn3FourMethodPublicationStudy`, `validateCocoPublicationValidation` |
| Timeseries > Spectral Moments | `acMenuSpecmoments` · helper / analyzer / plotter | SpectralMoments | `Desktop` (两版), `spectralmoments` (两版), `SpectralMoments` |

## Help

| 菜单路径及状态 | 公开函数前缀 / 角色 | 默认选择 | 全部 params.operation |
|---|---|---|---|
| Help | 菜单标题 | — | — |
| Help > Setting... | `acMenuSettings` · helper / plotter | Desktop | `Desktop` |
| Help > What''s New | `acMenuRead` · helper / plotter | Desktop | `Desktop` (两版) |
| Help > Manual | `acMenuManuals` · helper / plotter | Desktop | `Desktop` (两版) |
| Help > Find Updates | `acMenuFindupdates` · helper / plotter | Desktop | `Desktop` (两版) |
| Help > Copyright | `acMenuContact` · helper / plotter | Desktop | `Desktop` (两版) |
| Help > Contact | `acMenuEmail` · helper / plotter | Desktop | `Desktop` (两版) |

## 仅 GUIDE 保留

| 菜单路径及状态 | 公开函数前缀 / 角色 | 默认选择 | 全部 params.operation |
|---|---|---|---|
| Timeseries > Sedimentary Noise Model > Dynamic noise after orbital tuning (DYNOT) v2 | `acMenuDynotV2` · helper / analyzer / plotter | DYNOT_legacy | `DYNOT_legacy`, `Desktop_legacy` |
| Timeseries > eTimeOpt | `acMenuETimeOpt` · helper / analyzer / plotter | EvolutionaryTimeOpt_legacy | `Desktop_legacy`, `EvolutionaryTimeOpt_legacy` |
| Help > 文A/语言选择(language) | `acMenuLang` · helper / plotter | Desktop_legacy | `Desktop_legacy` |
| Timeseries > Sedimentary Noise Model > Lyapunov exponent | `acMenuLyapunov` · helper / analyzer / plotter | Lyapunov_legacy | `Desktop_legacy`, `LyapunovMonteCarlo_legacy`, `Lyapunov_legacy` |
| File > Open *.fig File | `acMenuOpen` · helper / plotter | Desktop_legacy | `Desktop_legacy` |
| Timeseries > Sedimentary Noise Model > Lag-1 autocorrelation coefficient (ρ1) v2 | `acMenuRhov2` · helper / analyzer / plotter | Lag1V2_legacy | `Desktop_legacy`, `Lag1V2MonteCarlo_legacy`, `Lag1V2_legacy` |
| Timeseries > TimeOpt | `acMenuTimeOpt` · helper / analyzer / plotter | TimeOpt_legacy | `Desktop_legacy`, `TimeOpt_legacy` |

## Toolbar

| 菜单路径及状态 | 公开函数前缀 / 角色 | 默认选择 | 全部 params.operation |
|---|---|---|---|
| Toolbar > Mini-Robot | `acMenuRobot` · helper / plotter | Robot | `Robot` (两版) |
