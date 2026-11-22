function [retval, id] = analyzer(params, id)
% CENOGRID.analyzer parameters: (none).
% Source: https://github.com/mingsongli/acycle/blob/b52ea9f510f3be00bde9a0238b9898a1e2315b74/code/guicode/AC.m#L7947
if nargin < 2, id = []; end
[retval, id] = aclog.invoke('CENOGRID-v1.0/analyzer', params, id, @execute);
end

function r = execute(p)
%% Copied from mingsongli/acycle@b52ea9f510f3be00bde9a0238b9898a1e2315b74 code/guicode/AC.m:L7947-L7948
data_name = which('Example-cenogrid-d18o.txt');
data_name2 = which('Example-cenogrid-d13c.txt');
%% End copied source
%% Copied from mingsongli/acycle@b52ea9f510f3be00bde9a0238b9898a1e2315b74 code/guicode/AC.m:L7960-L7962
data = load(data_name);
time = data(:,1);
value = data(:,2);
%% End copied source
%% Copied from mingsongli/acycle@b52ea9f510f3be00bde9a0238b9898a1e2315b74 code/guicode/AC.m:L7965-L7967
data = load(data_name2);
time2 = data(:,1);
value2 = data(:,2);
%% End copied source
r = struct();
r.time = time;
r.value = value;
r.time2 = time2;
r.value2 = value2;
end
