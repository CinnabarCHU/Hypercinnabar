function [retval, id] = helper(params, id)
% SWA.helper parameters: data_r.
% Source: https://github.com/mingsongli/acycle/blob/b52ea9f510f3be00bde9a0238b9898a1e2315b74/code/guicode/SWAgui.m#L115
if nargin < 2, id = []; end
[retval, id] = aclog.invoke('SWA-v1.0/helper', params, id, @execute);
end

function r = execute(p)
data_r = p.data_r;
%% Copied from mingsongli/acycle@b52ea9f510f3be00bde9a0238b9898a1e2315b74 code/guicode/SWAgui.m:L115-L117
data_r(any(isinf(data_r),2),:) = [];
data_r = sortrows(data_r);
diffx = diff(data_r(:,1));
%% End copied source
%% Copied from mingsongli/acycle@b52ea9f510f3be00bde9a0238b9898a1e2315b74 code/guicode/SWAgui.m:L70-L70
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
