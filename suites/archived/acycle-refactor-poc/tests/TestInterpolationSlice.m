classdef TestInterpolationSlice < matlab.unittest.TestCase
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
        function helperRecommendsMedianSpacing(testCase)
            data = [0 0;0.9 1;2.0 4;3.0 9];
            defaults = acycle.helpers.interpolationDefaults(data);
            testCase.verifyEqual(defaults.SamplingInterval,1,'AbsTol',1e-12);
            testCase.verifyTrue(defaults.IsUneven);
            testCase.verifyEqual(defaults.Method,'linear');
        end

        function coreProducesKnownLinearResult(testCase)
            data = [0 0;1 2;3 6];
            result = acycle.core.interpolateSeries(data, ...
                struct('SamplingInterval',1));
            expected = [0 0;1 2;2 4;3 6];
            testCase.verifyEqual(result.Data,expected,'AbsTol',1e-12);
            testCase.verifyEqual(result.Metadata.Method,'linear');
        end

        function coreCanApplyExplicitZeroGapPolicy(testCase)
            data = [0 1;1 2;10 3];
            result = acycle.core.interpolateSeries(data,struct( ...
                'SamplingInterval',1, ...
                'GapPolicy','zero', ...
                'GapThresholdMultiple',3));
            testCase.verifyEqual(result.Data(3:10,2),zeros(8,1));
            testCase.verifyEqual(result.Metadata.GapPairs,[1 10]);
        end

        function legacyFacadeDelegatesWithoutNumericChange(testCase)
            data = [0 0;1 2;3 6];
            direct = acycle.core.interpolateSeries(data, ...
                struct('SamplingInterval',1));
            [legacy,meta] = acycleInterpolateSeries(data,1);
            testCase.verifyEqual(legacy,direct.Data,'AbsTol',0);
            testCase.verifyEqual(meta,direct.Metadata);
        end

        function plotterUsesSuppliedAxes(testCase)
            fig = figure('Visible','off');
            testCase.addTeardown(@()delete(fig));
            ax = axes(fig);
            data = [0 0;1 2;3 6];
            result = acycle.core.interpolateSeries(data, ...
                struct('SamplingInterval',1));
            before = findall(groot,'Type','figure');
            graphics = acycle.plot.interpolation(ax,data,result);
            after = findall(groot,'Type','figure');
            testCase.verifyEqual(numel(after),numel(before));
            testCase.verifyEqual(graphics.Axes,ax);
            testCase.verifyTrue(isgraphics(graphics.Raw));
            testCase.verifyTrue(isgraphics(graphics.Interpolated));
        end
    end
end

