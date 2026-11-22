function [retval, id] = helper(params, id)
% BootstrapSmooth.helper parameters: data.
% Source: https://github.com/mingsongli/acycle/blob/b52ea9f510f3be00bde9a0238b9898a1e2315b74/code/guicode/SmoothBootGUI.m#L52
% Source: https://github.com/mingsongli/acycle/blob/b52ea9f510f3be00bde9a0238b9898a1e2315b74/code/guicode/SmoothBootGUI.m#L77
if nargin < 2, id = []; end
[retval, id] = aclog.invoke('BootstrapSmooth-v1.0/helper', params, id, @execute);
end

function r = execute(p)
data=p.data;
%% Copied from mingsongli/acycle@b52ea9f510f3be00bde9a0238b9898a1e2315b74 code/guicode/SmoothBootGUI.m:L40-L43
x = data(:,1);
y = data(:,2);

xlen = max(x) - min(x);
%% End copied source
r=struct('x',x,'y',y,'method','lowess','span',.3,'bootn',1000);
end
