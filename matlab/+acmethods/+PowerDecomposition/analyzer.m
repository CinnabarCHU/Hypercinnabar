function [retval, id] = analyzer(params, id)
% PowerDecomposition.analyzer parameters: data f3 window nw ftmin fterm step pad padtype.
% Source: https://github.com/mingsongli/acycle/blob/b52ea9f510f3be00bde9a0238b9898a1e2315b74/code/guicode/AC.m#L6136
if nargin < 2, id = []; end
[retval, id] = aclog.invoke('PowerDecomposition-v1.0/analyzer', params, id, @execute);
end

function r = execute(p)
data = p.data;
f3 = p.f3;
window = p.window;
nw = p.nw;
ftmin = p.ftmin;
fterm = p.fterm;
step = p.step;
pad = p.pad;
padtype = p.padtype;
%% Copied from mingsongli/acycle@b52ea9f510f3be00bde9a0238b9898a1e2315b74 code/guicode/AC.m:L6136-L6138
            data = data(~any(isnan(data),2),:);
            diffx = diff(data(:,1));
            if any(diffx(:) < 0)
%% End copied source
%% Copied from mingsongli/acycle@b52ea9f510f3be00bde9a0238b9898a1e2315b74 code/guicode/AC.m:L6146-L6148
                 data = sortrows(data); % sort data
            end
            if any(diffx(:) == 0)
%% End copied source
%% Copied from mingsongli/acycle@b52ea9f510f3be00bde9a0238b9898a1e2315b74 code/guicode/AC.m:L6154-L6156
                data=findduplicate(data); % find duplicate
            end
            if max(diffx)-min(diffx) <= eps(5)
%% End copied source
%% Copied from mingsongli/acycle@b52ea9f510f3be00bde9a0238b9898a1e2315b74 code/guicode/AC.m:L6162-L6166
                data = interpolate(data,median(diffx));
            end
            if padtype > 0
                data = zeropad2(data,window,padtype);
            end
%% End copied source
%% Copied from mingsongli/acycle@b52ea9f510f3be00bde9a0238b9898a1e2315b74 code/guicode/AC.m:L6183-L6183
            [pow]=pdan(data,f3,window,nw,ftmin,fterm,step,pad);
%% End copied source
r = struct();
r.pow = pow;
r.data = data;
end
