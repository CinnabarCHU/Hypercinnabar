function [retval, id] = helper(params, id)
% InterpolationPro.helper parameters: data.
% Source: https://github.com/mingsongli/acycle/blob/b52ea9f510f3be00bde9a0238b9898a1e2315b74/code/guicode/interpolationGUI.m#L126
if nargin < 2, id = []; end
[retval, id] = aclog.invoke('InterpolationPro-v1.0/helper', params, id, @execute);
end

function r = execute(p)
data = p.data;
%% Copied from mingsongli/acycle@b52ea9f510f3be00bde9a0238b9898a1e2315b74 code/guicode/interpolationGUI.m:L130-L132
data = sortrows(data);

dt = median(diff(data(:,1)));
%% End copied source
method=1; gap2zero=0; gapdt=10;
x1=min(data(:,1)); x2=max(data(:,1)); y1=min(data(:,2)); y2=max(data(:,2));
r = struct();
r.data = data;
r.dt = dt;
r.method = method;
r.gap2zero = gap2zero;
r.gapdt = gapdt;
r.x1 = x1;
r.x2 = x2;
r.y1 = y1;
r.y2 = y2;
end
