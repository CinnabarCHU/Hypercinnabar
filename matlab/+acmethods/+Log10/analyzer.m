function [retval, id] = analyzer(params, id)
% Log10.analyzer parameters: data.
% Source: https://github.com/mingsongli/acycle/blob/b52ea9f510f3be00bde9a0238b9898a1e2315b74/code/guicode/AC.m#L2454
if nargin < 2, id = []; end
[retval, id] = aclog.invoke('Log10-v1.0/analyzer', params, id, @execute);
end

function r = execute(p)
data = p.data;
%% Copied from mingsongli/acycle@b52ea9f510f3be00bde9a0238b9898a1e2315b74 code/guicode/AC.m:L2454-L2456
            time = data(:,1);
            value = log10(data(:,2));
            data1 = [time,value];
%% End copied source
r = struct();
r.data1 = data1;
end
