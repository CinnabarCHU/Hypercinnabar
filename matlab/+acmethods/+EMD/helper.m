function [retval, id] = helper(params, id)
% EMD.helper parameters: data_filterout.
% Source: https://github.com/mingsongli/acycle/blob/b52ea9f510f3be00bde9a0238b9898a1e2315b74/code/guicode/AC.m#L8976
if nargin < 2, id = []; end
[retval, id] = aclog.invoke('EMD-v1.0/helper', params, id, @execute);
end

function r = execute(p)
data_filterout = p.data_filterout;
%% Copied from mingsongli/acycle@b52ea9f510f3be00bde9a0238b9898a1e2315b74 code/guicode/AC.m:L8976-L8976
defaultans = {num2str(10),'1','pchip'};
%% End copied source
goal=str2double(defaultans{1});
extrema=str2double(defaultans{2});
intp=defaultans{3};
r = struct();
r.intp=intp;
r.data_filterout = data_filterout;
r.goal = goal;
r.extrema = extrema;
end
