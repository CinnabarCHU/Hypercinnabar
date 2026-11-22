function [retval, id] = analyzer(params, id)
% ExampleInsolation.analyzer parameters: (none).
% Source: https://github.com/mingsongli/acycle/blob/b52ea9f510f3be00bde9a0238b9898a1e2315b74/code/guicode/AC.m#L7871
if nargin < 2, id = []; end
[retval, id] = aclog.invoke('ExampleInsolation-v1.0/analyzer', params, id, @execute);
end

function r = execute(p)
%% Copied from mingsongli/acycle@b52ea9f510f3be00bde9a0238b9898a1e2315b74 code/guicode/AC.m:L7871-L7871
data_name = which('Example-Insol-t-0-2000ka-day-80-lat-65-meandaily-La04.txt');
%% End copied source
%% Copied from mingsongli/acycle@b52ea9f510f3be00bde9a0238b9898a1e2315b74 code/guicode/AC.m:L7881-L7881
data = load(data_name);
%% End copied source
r = struct();
r.data = data;
r.data_name = data_name;
end
