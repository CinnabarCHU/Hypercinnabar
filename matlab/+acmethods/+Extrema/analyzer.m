function [retval, id] = analyzer(params, id)
% Extrema.analyzer parameters: data t1 t2 maxmin ind.
% Source: https://github.com/mingsongli/acycle/blob/b52ea9f510f3be00bde9a0238b9898a1e2315b74/code/guicode/AC.m#L3795
if nargin < 2, id = []; end
[retval, id] = aclog.invoke('Extrema-v1.0/analyzer', params, id, @execute);
end

function r = execute(p)
data = p.data;
t1 = p.t1;
t2 = p.t2;
maxmin = p.maxmin;
ind = p.ind;
%% Copied from mingsongli/acycle@b52ea9f510f3be00bde9a0238b9898a1e2315b74 code/guicode/AC.m:L3795-L3801
                [dat] = select_interval(data,t1,t2);
                y = dat(:,ind);
                if maxmin == 1  
                    [m,i] = max(y);
                else
                    [m,i] = min(y);
                end
%% End copied source
row=dat(i,:);
r = struct();
r.m = m;
r.i = i;
r.row = row;
end
