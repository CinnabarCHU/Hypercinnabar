function [retval, id] = helper(params, id)
% PlotPro.helper parameters: (none).
% Source: https://github.com/mingsongli/acycle/blob/b52ea9f510f3be00bde9a0238b9898a1e2315b74/code/guicode/PlotPro2DLineGUI.m#L947
if nargin < 2, id = []; end
[retval, id] = aclog.invoke('PlotPro-v1.0/helper', params, id, @execute);
end

function r = execute(p)
%% Copied from mingsongli/acycle@b52ea9f510f3be00bde9a0238b9898a1e2315b74 code/guicode/PlotPro2DLineGUI.m:L947-L948
PlotAdvSettingSeed = readtable('PlotAdvSettingSeed.xlsx');
PlotAdvSetting = PlotAdvSettingSeed;
%% End copied source
r = struct();
r.PlotAdvSetting = PlotAdvSetting;
end
