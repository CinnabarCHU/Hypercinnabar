classdef TestAnalysisSlices < matlab.unittest.TestCase
    % SPDX-License-Identifier: GPL-3.0-or-later

    methods (TestClassSetup)
        function addPoCPaths(testCase)
            root = fileparts(fileparts(mfilename('fullpath')));
            oldPath = path;
            addpath(fullfile(root,'matlab'));
            addpath(fullfile(root,'matlab','compat'));
            testCase.addTeardown(@()path(oldPath));
        end
    end

    methods (Test)
        function fixedDefaultsTrackDominantFftPeak(testCase)
            coordinate = (0:127)'*0.1;
            targetFrequency = 1.25;
            data = [coordinate,sin(2*pi*targetFrequency*coordinate)];
            defaults = acycle.helpers.fixedFilterDefaults(data);
            testCase.verifyLessThanOrEqual( ...
                abs(defaults.DominantFftFrequency-targetFrequency), ...
                defaults.RayleighFrequency);
            testCase.verifyLessThan( ...
                defaults.LowerFrequency,defaults.UpperFrequency);
            testCase.verifyLessThan( ...
                defaults.UpperFrequency,defaults.NyquistFrequency);
        end

        function fixedAdapterPreservesEngineOutput(testCase)
            coordinate = (0:15)';
            data = [coordinate,sin(2*pi*coordinate/8)];
            options = struct( ...
                'Method','gaussian', ...
                'LowerFrequency',0.05, ...
                'UpperFrequency',0.2);
            result = acycle.core.fixedBandpass( ...
                data,options,@fakeBandpassEngine);
            testCase.verifyEqual(result.Data(:,2),0.5*data(:,2));
            testCase.verifyEqual(result.Response,[0 0;0.25 1;0.5 0]);
            testCase.verifyEqual(result.Metadata.Engine,'fake');
        end

        function dynamicDefaultsAreExecutableParameters(testCase)
            coordinate = (0:99)';
            data = [coordinate,sin(2*pi*coordinate/20)];
            defaults = acycle.helpers.dynamicFilterDefaults(data);
            testCase.verifyGreaterThanOrEqual(defaults.WindowLength,7);
            testCase.verifyGreaterThanOrEqual(defaults.StepLength,1);
            testCase.verifyLessThanOrEqual( ...
                defaults.StepLength,defaults.WindowLength);
            testCase.verifyEqual( ...
                defaults.LowerControlPoints([1 end],1),coordinate([1 end]));
        end

        function dynamicAdapterPreservesCoverageContract(testCase)
            coordinate = (0:15)';
            data = [coordinate,sin(2*pi*coordinate/8)];
            lower = [0 0.05;15 0.05];
            upper = [0 0.2;15 0.2];
            result = acycle.core.dynamicFilter( ...
                data,lower,upper,struct( ...
                'WindowLength',8,'StepLength',2), ...
                @fakeDynamicEngine);
            testCase.verifySize(result.Data,[16 4]);
            testCase.verifyEqual(result.Data(:,3),ones(16,1));
            testCase.verifySize(result.Windows,[1 8]);
            testCase.verifyEqual(result.Metadata.Engine,'fake');
        end

        function mtmTaperRuleMatchesAcycle(testCase)
            testCase.verifyEqual(acycle.core.mtmTaperCount(1),2);
            testCase.verifyEqual(acycle.core.mtmTaperCount(2),3);
            testCase.verifyEqual(acycleMtmTaperCount(3.5),6);
        end

        function spectrumDefaultsChooseMethodFromSampling(testCase)
            regularX = (0:31)';
            regular = acycle.helpers.spectrumDefaults( ...
                [regularX,sin(regularX)]);
            unevenX = regularX;
            unevenX(17:end) = unevenX(17:end)+0.1;
            uneven = acycle.helpers.spectrumDefaults( ...
                [unevenX,sin(unevenX)]);
            testCase.verifyEqual(regular.Method,'mtm');
            testCase.verifyEqual(regular.TaperCount,3);
            testCase.verifyEqual(uneven.Method,'lomb');
            testCase.verifyTrue(uneven.IsUneven);
        end

        function periodogramCoreFindsKnownPeak(testCase)
            testCase.assumeEqual(exist('periodogram','file'),2, ...
                'Signal Processing Toolbox is not available.');
            coordinate = (0:255)'*0.1;
            targetFrequency = 1.25;
            data = [coordinate,sin(2*pi*targetFrequency*coordinate)];
            result = acycle.core.powerSpectrum(data,struct( ...
                'Method','periodogram', ...
                'Nfft',1024, ...
                'MinimumFrequency',0, ...
                'MaximumFrequency',5));
            [~,index] = max(result.Power);
            testCase.verifyEqual(result.Frequency(index), ...
                targetFrequency,'AbsTol',1/(1024*0.1));
            testCase.verifyEqual(result.Metadata.SideEffects,'none');
        end

        function plottersUseOnlySuppliedAxes(testCase)
            fig = figure('Visible','off');
            testCase.addTeardown(@()delete(fig));
            tiled = tiledlayout(fig,2,3);
            axesHandles = gobjects(1,5);
            for index = 1:5
                axesHandles(index) = nexttile(tiled,index);
            end
            coordinate = (0:15)';
            data = [coordinate,sin(2*pi*coordinate/8)];
            fixedResult = acycle.core.fixedBandpass( ...
                data,struct('Method','gaussian', ...
                'LowerFrequency',0.05,'UpperFrequency',0.2), ...
                @fakeBandpassEngine);
            dynamicResult = acycle.core.dynamicFilter( ...
                data,[0 0.05;15 0.05],[0 0.2;15 0.2], ...
                struct('WindowLength',8,'StepLength',2), ...
                @fakeDynamicEngine);
            spectrumResult = struct( ...
                'Frequency',[0;0.1;0.2], ...
                'Power',[1;4;2], ...
                'Metadata',struct('Method','fake'));
            before = findall(groot,'Type','figure');
            fixedGraphics = acycle.plot.fixedBandpass( ...
                axesHandles(1),axesHandles(2),data,fixedResult);
            dynamicGraphics = acycle.plot.dynamicFilter( ...
                axesHandles(3),axesHandles(4),data,dynamicResult);
            spectrumGraphics = acycle.plot.powerSpectrum( ...
                axesHandles(5),spectrumResult,struct('YScale','linear'));
            after = findall(groot,'Type','figure');
            testCase.verifyEqual(numel(after),numel(before));
            testCase.verifyEqual(fixedGraphics.TimeAxes,axesHandles(1));
            testCase.verifyEqual(dynamicGraphics.BandAxes,axesHandles(4));
            testCase.verifyEqual(spectrumGraphics.Axes,axesHandles(5));
        end
    end
end

function [payload,metadata] = fakeBandpassEngine(data,options)
payload = struct( ...
    'coordinate',data(:,1), ...
    'filtered',0.5*data(:,2), ...
    'envelope',abs(0.5*data(:,2)), ...
    'response_frequency',[0;0.25;0.5], ...
    'response_gain',[0;1;0], ...
    'method',options.method);
metadata = struct('Engine','fake');
end

function [result,windows,metadata] = fakeDynamicEngine( ...
        data,lowerControlPoints,upperControlPoints,options)
result = [data(:,1),0.5*data(:,2),ones(size(data,1),1), ...
    ones(size(data,1),1)];
center = mean(data(:,1));
lower = mean(lowerControlPoints(:,2));
upper = mean(upperControlPoints(:,2));
windows = [center,lower,upper,mean([lower upper]), ...
    data(1,1),data(end,1),1,size(data,1)];
metadata = struct('Engine','fake','Options',options);
end
