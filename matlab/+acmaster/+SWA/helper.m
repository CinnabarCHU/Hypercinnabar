function [retval,id] = helper(params,id)
% SWA.helper parameters: data_r.
% Source: https://github.com/mingsongli/acycle/blob/dcba4279168745b563e0535b954297023dd62fc7/code/guicode/SWAgui.m
if nargin < 2, id = []; end
[retval,id] = accompat.masterInvoke('SWA-v3.1.1+dcba427/helper',params,id,@execute);
end

function r = execute(p)
data_r = p.data_r;
%% Copied from mingsongli/acycle@dcba4279168745b563e0535b954297023dd62fc7 code/guicode/SWAgui.m:L115-L117
data_r(any(isinf(data_r),2),:) = [];
data_r = sortrows(data_r);
diffx = diff(data_r(:,1));
%% End copied source
%% Copied from mingsongli/acycle@dcba4279168745b563e0535b954297023dd62fc7 code/guicode/SWAgui.m:L70-L70
defaultVal = [0, 1, 1, 0, 1, 1, 0, 0];
%% End copied source
curves=logical(defaultVal); figure_count=1; log_y=true; log_x=false; period_axis=false;
r = struct();
r.data_r = data_r;
r.curves = curves;
r.figure_count = figure_count;
r.log_y = log_y;
r.log_x = log_x;
r.period_axis = period_axis;
end
