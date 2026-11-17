# 第一批计算入口核对表

这是迁移规划表，包含计算入口及共享的采样／taper 策略 Helper；不是已通过 MATLAB 运行验证的功能列表。19 个入口的保守依赖共 29 个 MATLAB 文件。

| 入口 | 输入参数（原函数签名） | 输出 | 当前桌面图可达 |
|---|---|---|---|
| [acycleAmplitudeModulation](https://github.com/mingsongli/acycle/blob/dcba4279168745b563e0535b954297023dd62fc7/code/seriesanalysis/acycleAmplitudeModulation.m#L1) | `data` | `result, meta` | 是 |
| [acycleBandpassFilter](https://github.com/mingsongli/acycle/blob/dcba4279168745b563e0535b954297023dd62fc7/code/seriesanalysis/acycleBandpassFilter.m#L1) | `data, options` | `result, meta` | 是 |
| [acycleCircularSpectrum](https://github.com/mingsongli/acycle/blob/dcba4279168745b563e0535b954297023dd62fc7/code/seriesanalysis/acycleCircularSpectrum.m#L1) | `eventCoordinates, periodMinimum, periodMaximum, periodCount, gridMode` | `result, meta` | 是 |
| [acycleCoherencePhase](https://github.com/mingsongli/acycle/blob/dcba4279168745b563e0535b954297023dd62fc7/code/seriesanalysis/acycleCoherencePhase.m#L1) | `reference, target, options` | `result, meta` | 是 |
| [acycleDynamicFilter](https://github.com/mingsongli/acycle/blob/dcba4279168745b563e0535b954297023dd62fc7/code/seriesanalysis/acycleDynamicFilter.m#L1) | `data, lowerControlPoints, upperControlPoints, options` | `result, windows, meta` | 是 |
| [acycleEmpiricalModeDecomposition](https://github.com/mingsongli/acycle/blob/dcba4279168745b563e0535b954297023dd62fc7/code/seriesanalysis/acycleEmpiricalModeDecomposition.m#L1) | `data, options` | `result, meta` | 是 |
| [acycleEvolutionaryRho1](https://github.com/mingsongli/acycle/blob/dcba4279168745b563e0535b954297023dd62fc7/code/seriesanalysis/acycleEvolutionaryRho1.m#L1) | `data, samplingInterval, windowLength` | `result, meta` | 是 |
| [acycleFixedBandwidthSummary](https://github.com/mingsongli/acycle/blob/dcba4279168745b563e0535b954297023dd62fc7/code/seriesanalysis/acycleFixedBandwidthSummary.m#L1) | `data, method, options` | `result, meta` | 是 |
| [acycleFixedCountMovingSummary](https://github.com/mingsongli/acycle/blob/dcba4279168745b563e0535b954297023dd62fc7/code/seriesanalysis/acycleFixedCountMovingSummary.m#L1) | `data, statistic, windowPoints` | `result, meta` | 是 |
| [acycleGaussianMovingAverage](https://github.com/mingsongli/acycle/blob/dcba4279168745b563e0535b954297023dd62fc7/code/seriesanalysis/acycleGaussianMovingAverage.m#L1) | `data, windowPoints` | `result, meta` | 是 |
| [acycleInterpolateSeries](https://github.com/mingsongli/acycle/blob/dcba4279168745b563e0535b954297023dd62fc7/code/seriesanalysis/acycleInterpolateSeries.m#L1) | `data, samplingInterval, varargin` | `interpolated, meta` | 是 |
| [acycleLeadLagRmse](https://github.com/mingsongli/acycle/blob/dcba4279168745b563e0535b954297023dd62fc7/code/seriesanalysis/acycleLeadLagRmse.m#L1) | `reference, target, maximumLag, lagStep, coordinateDirection` | `result, meta` | 是 |
| [acycleMtmTaperCount](https://github.com/mingsongli/acycle/blob/dcba4279168745b563e0535b954297023dd62fc7/code/seriesanalysis/acycleMtmTaperCount.m#L1) | `nw` | `taperCount` | 是 |
| [acyclePowerDecomposition](https://github.com/mingsongli/acycle/blob/dcba4279168745b563e0535b954297023dd62fc7/code/seriesanalysis/acyclePowerDecomposition.m#L1) | `data, targetBands, options` | `result, bandPowers, meta` | 否；独立数值约定 |
| [acyclePrewhitenSeries](https://github.com/mingsongli/acycle/blob/dcba4279168745b563e0535b954297023dd62fc7/code/seriesanalysis/acyclePrewhitenSeries.m#L1) | `data, options` | `result, meta` | 是 |
| [acycleSamplingIsUneven](https://github.com/mingsongli/acycle/blob/dcba4279168745b563e0535b954297023dd62fc7/code/seriesanalysis/acycleSamplingIsUneven.m#L1) | `coordinate, relativeTolerance` | `isUneven, info` | 是 |
| [acycleSedimentationRateAgeModel](https://github.com/mingsongli/acycle/blob/dcba4279168745b563e0535b954297023dd62fc7/code/seriesanalysis/acycleSedimentationRateAgeModel.m#L1) | `data, depthUnit, firstAgeKyr` | `result, meta` | 是 |
| [acycleSpectralMoments](https://github.com/mingsongli/acycle/blob/dcba4279168745b563e0535b954297023dd62fc7/code/seriesanalysis/acycleSpectralMoments.m#L1) | `data, options` | `result, meta` | 是 |
| [bispectralAnalyze](https://github.com/mingsongli/acycle/blob/dcba4279168745b563e0535b954297023dd62fc7/code/package/bispectral/bispectralAnalyze.m#L1) | `data, varargin` | `result` | 是 |

这里的 `varargin` 尚需按各函数参数契约细化；随机数、窗口端点、缺失值与采样规则不能由通用数组接口代替。`acyclePowerDecomposition` 应与桌面/DYNOT 的 `pdan` 区分。

## 该集合的完整 MATLAB 依赖

- [code/package/bispectral/bispectralAnalyze.m](https://github.com/mingsongli/acycle/blob/dcba4279168745b563e0535b954297023dd62fc7/code/package/bispectral/bispectralAnalyze.m)
- [code/package/bispectral/bispectralDefaults.m](https://github.com/mingsongli/acycle/blob/dcba4279168745b563e0535b954297023dd62fc7/code/package/bispectral/bispectralDefaults.m)
- [code/package/bispectral/bispectralEstimate.m](https://github.com/mingsongli/acycle/blob/dcba4279168745b563e0535b954297023dd62fc7/code/package/bispectral/bispectralEstimate.m)
- [code/package/bispectral/bispectralPreprocess.m](https://github.com/mingsongli/acycle/blob/dcba4279168745b563e0535b954297023dd62fc7/code/package/bispectral/bispectralPreprocess.m)
- [code/package/bispectral/bispectralSignificance.m](https://github.com/mingsongli/acycle/blob/dcba4279168745b563e0535b954297023dd62fc7/code/package/bispectral/bispectralSignificance.m)
- [code/package/bispectral/bispectralSurrogate.m](https://github.com/mingsongli/acycle/blob/dcba4279168745b563e0535b954297023dd62fc7/code/package/bispectral/bispectralSurrogate.m)
- [code/seriesanalysis/acycleAmplitudeModulation.m](https://github.com/mingsongli/acycle/blob/dcba4279168745b563e0535b954297023dd62fc7/code/seriesanalysis/acycleAmplitudeModulation.m)
- [code/seriesanalysis/acycleBandpassFilter.m](https://github.com/mingsongli/acycle/blob/dcba4279168745b563e0535b954297023dd62fc7/code/seriesanalysis/acycleBandpassFilter.m)
- [code/seriesanalysis/acycleCircularSpectrum.m](https://github.com/mingsongli/acycle/blob/dcba4279168745b563e0535b954297023dd62fc7/code/seriesanalysis/acycleCircularSpectrum.m)
- [code/seriesanalysis/acycleCoherencePhase.m](https://github.com/mingsongli/acycle/blob/dcba4279168745b563e0535b954297023dd62fc7/code/seriesanalysis/acycleCoherencePhase.m)
- [code/seriesanalysis/acycleDynamicFilter.m](https://github.com/mingsongli/acycle/blob/dcba4279168745b563e0535b954297023dd62fc7/code/seriesanalysis/acycleDynamicFilter.m)
- [code/seriesanalysis/acycleEmpiricalModeDecomposition.m](https://github.com/mingsongli/acycle/blob/dcba4279168745b563e0535b954297023dd62fc7/code/seriesanalysis/acycleEmpiricalModeDecomposition.m)
- [code/seriesanalysis/acycleEvolutionaryRho1.m](https://github.com/mingsongli/acycle/blob/dcba4279168745b563e0535b954297023dd62fc7/code/seriesanalysis/acycleEvolutionaryRho1.m)
- [code/seriesanalysis/acycleFixedBandwidthSummary.m](https://github.com/mingsongli/acycle/blob/dcba4279168745b563e0535b954297023dd62fc7/code/seriesanalysis/acycleFixedBandwidthSummary.m)
- [code/seriesanalysis/acycleFixedCountMovingSummary.m](https://github.com/mingsongli/acycle/blob/dcba4279168745b563e0535b954297023dd62fc7/code/seriesanalysis/acycleFixedCountMovingSummary.m)
- [code/seriesanalysis/acycleGaussianMovingAverage.m](https://github.com/mingsongli/acycle/blob/dcba4279168745b563e0535b954297023dd62fc7/code/seriesanalysis/acycleGaussianMovingAverage.m)
- [code/seriesanalysis/acycleInterpolateSeries.m](https://github.com/mingsongli/acycle/blob/dcba4279168745b563e0535b954297023dd62fc7/code/seriesanalysis/acycleInterpolateSeries.m)
- [code/seriesanalysis/acycleLeadLagRmse.m](https://github.com/mingsongli/acycle/blob/dcba4279168745b563e0535b954297023dd62fc7/code/seriesanalysis/acycleLeadLagRmse.m)
- [code/seriesanalysis/acycleMtmTaperCount.m](https://github.com/mingsongli/acycle/blob/dcba4279168745b563e0535b954297023dd62fc7/code/seriesanalysis/acycleMtmTaperCount.m)
- [code/seriesanalysis/acyclePowerDecomposition.m](https://github.com/mingsongli/acycle/blob/dcba4279168745b563e0535b954297023dd62fc7/code/seriesanalysis/acyclePowerDecomposition.m)
- [code/seriesanalysis/acyclePrewhitenSeries.m](https://github.com/mingsongli/acycle/blob/dcba4279168745b563e0535b954297023dd62fc7/code/seriesanalysis/acyclePrewhitenSeries.m)
- [code/seriesanalysis/acycleSamplingIsUneven.m](https://github.com/mingsongli/acycle/blob/dcba4279168745b563e0535b954297023dd62fc7/code/seriesanalysis/acycleSamplingIsUneven.m)
- [code/seriesanalysis/acycleSedimentationRateAgeModel.m](https://github.com/mingsongli/acycle/blob/dcba4279168745b563e0535b954297023dd62fc7/code/seriesanalysis/acycleSedimentationRateAgeModel.m)
- [code/seriesanalysis/acycleSpectralMoments.m](https://github.com/mingsongli/acycle/blob/dcba4279168745b563e0535b954297023dd62fc7/code/seriesanalysis/acycleSpectralMoments.m)
- [code/seriesanalysis/emdNL.m](https://github.com/mingsongli/acycle/blob/dcba4279168745b563e0535b954297023dd62fc7/code/seriesanalysis/emdNL.m)
- [code/seriesanalysis/find_extrema.m](https://github.com/mingsongli/acycle/blob/dcba4279168745b563e0535b954297023dd62fc7/code/seriesanalysis/find_extrema.m)
- [code/seriesanalysis/minirhos0.m](https://github.com/mingsongli/acycle/blob/dcba4279168745b563e0535b954297023dd62fc7/code/seriesanalysis/minirhos0.m)
- [code/seriesanalysis/moveMedian.m](https://github.com/mingsongli/acycle/blob/dcba4279168745b563e0535b954297023dd62fc7/code/seriesanalysis/moveMedian.m)
- [code/seriesanalysis/rhoAR1ML.m](https://github.com/mingsongli/acycle/blob/dcba4279168745b563e0535b954297023dd62fc7/code/seriesanalysis/rhoAR1ML.m)
