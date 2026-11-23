classdef TestCoreOnly < matlab.unittest.TestCase
    % Verify that API facades do not alter preserved numerical results.
    % SPDX-License-Identifier: GPL-3.0-or-later

    methods (TestClassSetup)
        function addPackagePath(testCase)
            root = fileparts(fileparts(mfilename('fullpath')));
            testCase.applyFixture( ...
                matlab.unittest.fixtures.PathFixture(fullfile(root,'matlab')));
        end
    end

    methods (Test)
        function interpolationFacadeMatchesEngine(testCase)
            coordinate = (0:0.5:100)';
            coordinate(2:end-1) = coordinate(2:end-1) + ...
                0.02*sin((2:numel(coordinate)-1)');
            data = [coordinate,sin(2*pi*0.05*coordinate)];

            [throughApi,apiInfo] = acycle.core.interpolateSeries( ...
                data,struct('SamplingInterval',0.5,'Verbose',false));
            [throughEngine,engineInfo] = ...
                acycle.core.engine.acycleInterpolateSeries(data,0.5);

            testCase.verifyEqual(throughApi,throughEngine);
            testCase.verifyEqual(apiInfo.OutputRows,engineInfo.OutputRows);
            testCase.verifyEqual(apiInfo.Engine, ...
                'acycle.core.engine.acycleInterpolateSeries');
        end

        function bandpassFacadeMatchesEngine(testCase)
            coordinate = (0:0.5:100)';
            values = sin(2*pi*0.05*coordinate) + ...
                0.5*sin(2*pi*0.2*coordinate);
            data = [coordinate,values];
            apiOptions = struct( ...
                'Method','gaussian', ...
                'LowerFrequency',0.04, ...
                'UpperFrequency',0.06, ...
                'Verbose',false);
            engineOptions = struct( ...
                'method','gaussian', ...
                'lower_frequency',0.04, ...
                'upper_frequency',0.06);

            [throughApi,apiInfo] = ...
                acycle.core.fixedBandpass(data,apiOptions);
            [throughEngine,engineInfo] = ...
                acycle.core.engine.acycleBandpassFilter(data,engineOptions);

            expected = [throughEngine.coordinate,throughEngine.filtered];
            testCase.verifyEqual(throughApi,expected);
            testCase.verifyEqual(apiInfo.Response, ...
                [throughEngine.response_frequency,throughEngine.response_gain]);
            testCase.verifyEqual(apiInfo.nfft,engineInfo.nfft);
        end

        function spectrumFacadeMatchesSpectrumEstimator(testCase)
            coordinate = (0:0.5:100)';
            values = sin(2*pi*0.05*coordinate) + ...
                0.25*sin(2*pi*0.17*coordinate);
            data = [coordinate,values];
            nfft = 512;

            [throughApi,apiInfo] = acycle.core.powerSpectrum( ...
                data,struct( ...
                    'Method','periodogram', ...
                    'Nfft',nfft, ...
                    'Verbose',false));
            centered = values-mean(values);
            [power,frequency] = periodogram(centered,[],nfft,2);
            expected = [real(frequency(:)),real(power(:))];

            testCase.verifyEqual(throughApi,expected);
            testCase.verifyEqual(apiInfo.Source, ...
                'spectrum.m::computeSpectrum');
        end

        function coreCreatesNoFigures(testCase)
            coordinate = (0:0.5:100)';
            data = [coordinate,sin(2*pi*0.05*coordinate)];
            before = numel(findall(0,'Type','figure'));
            acycle.core.powerSpectrum(data,struct( ...
                'Method','periodogram','Verbose',false));
            after = numel(findall(0,'Type','figure'));
            testCase.verifyEqual(after,before);
        end
    end
end

