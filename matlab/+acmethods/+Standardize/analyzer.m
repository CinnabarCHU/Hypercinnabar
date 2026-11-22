function [retval, id] = analyzer(params, id)
% Standardize.analyzer parameters: data.
% Source: https://github.com/mingsongli/acycle/blob/b52ea9f510f3be00bde9a0238b9898a1e2315b74/code/guicode/AC.m#L2274
if nargin < 2, id = []; end
[retval, id] = aclog.invoke('Standardize-v1.0/analyzer', params, id, @execute);
end

function r = execute(p)
data = p.data;
%% Copied from mingsongli/acycle@b52ea9f510f3be00bde9a0238b9898a1e2315b74 code/guicode/AC.m:L2274-L2276
            time = data(:,1);
            value = (data(:,2)-mean(data(:,2)))/std(data(:,2));
            data1 = [time,value];
%% End copied source
r = struct();
r.data1 = data1;
end
