function [retval, id] = helper(params, id)
% Extrema.helper parameters: data.
% Source: https://github.com/mingsongli/acycle/blob/b52ea9f510f3be00bde9a0238b9898a1e2315b74/code/guicode/AC.m#L3787
if nargin < 2, id = []; end
[retval, id] = aclog.invoke('Extrema-v1.0/helper', params, id, @execute);
end

function r = execute(p)
data = p.data;
x=data(:,1);
%% Copied from mingsongli/acycle@b52ea9f510f3be00bde9a0238b9898a1e2315b74 code/guicode/AC.m:L3787-L3787
            defaultans = {num2str(min(x)),num2str(max(x)),'1','2'};
%% End copied source
t1=str2double(defaultans{1}); t2=str2double(defaultans{2}); maxmin=str2double(defaultans{3}); ind=str2double(defaultans{4});
r = struct();
r.data = data;
r.t1 = t1;
r.t2 = t2;
r.maxmin = maxmin;
r.ind = ind;
end
