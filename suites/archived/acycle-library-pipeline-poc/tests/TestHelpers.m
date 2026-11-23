classdef TestHelpers < matlab.unittest.TestCase
    % SPDX-License-Identifier: GPL-3.0-or-later

    methods (TestClassSetup)
        function addPackagePath(testCase)
            root = fileparts(fileparts(mfilename('fullpath')));
            testCase.applyFixture( ...
                matlab.unittest.fixtures.PathFixture(fullfile(root,'matlab')));
        end
    end

    methods (Test)
        function recommendationsAreExplicitCoreOptions(testCase)
            coordinate = (0:0.5:100)';
            coordinate(2:end-1) = coordinate(2:end-1) + ...
                0.015*cos((2:numel(coordinate)-1)');
            data = [coordinate,sin(2*pi*0.05*coordinate)];
            quiet = struct('Verbose',false,'CoreVerbose',false);

            [interpolation,interpolationReport] = ...
                acycle.helpers.recommendInterpolation(data,quiet);
            testCase.verifyEqual(sort(fieldnames(interpolation)), ...
                sort({'SamplingInterval';'Verbose'}));
            testCase.verifyTrue(interpolationReport.IsUneven);

            regularCoordinate = (0:0.5:100)';
            regular = [regularCoordinate, ...
                sin(2*pi*0.05*regularCoordinate)];
            [spectrumOptions,spectrumReport] = ...
                acycle.helpers.recommendSpectrum(regular,quiet);
            testCase.verifyEqual(spectrumOptions.Method,'mtm');
            testCase.verifyEqual(spectrumOptions.TimeBandwidth,2);
            testCase.verifyGreaterThanOrEqual( ...
                spectrumOptions.Nfft,size(regular,1));
            testCase.verifyGreaterThan(spectrumReport.NyquistFrequency,0);
        end

        function bandRecommendationTracksDominantPeak(testCase)
            frequency = (0:0.001:0.5)';
            power = exp(-((frequency-0.05)/0.004).^2) + ...
                0.2*exp(-((frequency-0.15)/0.01).^2);
            [options,report] = acycle.helpers.recommendBandpass( ...
                [frequency,power],struct( ...
                    'Verbose',false,'CoreVerbose',false));

            testCase.verifyEqual(report.PeakFrequency,0.05,'AbsTol',0.001);
            testCase.verifyLessThan(options.LowerFrequency,0.05);
            testCase.verifyGreaterThan(options.UpperFrequency,0.05);
        end
    end
end
