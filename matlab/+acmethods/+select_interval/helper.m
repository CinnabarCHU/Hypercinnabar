function [retval, id] = helper(params, id)
% select_interval.helper parameters: data.
% Source: https://github.com/mingsongli/acycle/blob/b52ea9f510f3be00bde9a0238b9898a1e2315b74/code/guicode/AC.m#L2061
if nargin < 2, id = []; end
[retval, id] = aclog.invoke('select_interval-v1.0/helper', params, id, @execute);
end

function r = execute(p)
data = p.data;
%% Copied from mingsongli/acycle@b52ea9f510f3be00bde9a0238b9898a1e2315b74 code/guicode/AC.m:L2061-L2063
        time = data(:,1);
        value = data(:,2);
        npts = length(time);
%% End copied source
%% Copied from mingsongli/acycle@b52ea9f510f3be00bde9a0238b9898a1e2315b74 code/guicode/AC.m:L2072-L2072
        defaultans = {num2str(time(1)),num2str(time(npts)),'0'};
%% End copied source
t1=str2double(defaultans{1}); t2=str2double(defaultans{2});
r = struct();
r.data = data;
r.t1 = t1;
r.t2 = t2;
end
