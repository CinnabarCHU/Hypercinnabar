function [retval,id] = helper(params,id)
% PlotPro.helper parameters: (none).
% Source: https://github.com/mingsongli/acycle/blob/dcba4279168745b563e0535b954297023dd62fc7/code/guicode/PlotPro2DLineGUI.m
if nargin < 2, id = []; end
[retval,id] = accompat.masterInvoke('PlotPro-v3.1.1+dcba427/helper',params,id,@execute);
end

function r = execute(p)
%% Copied from mingsongli/acycle@dcba4279168745b563e0535b954297023dd62fc7 code/guicode/PlotPro2DLineGUI.m:L947-L948
PlotAdvSettingSeed = readtable('PlotAdvSettingSeed.xlsx');
PlotAdvSetting = PlotAdvSettingSeed;
%% End copied source
r = struct();
r.PlotAdvSetting = PlotAdvSetting;
end
