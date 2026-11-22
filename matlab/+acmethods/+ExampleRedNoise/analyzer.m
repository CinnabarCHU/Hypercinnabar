function [retval, id] = analyzer(params, id)
% ExampleRedNoise.analyzer parameters: (none).
% Source: https://github.com/mingsongli/acycle/blob/b52ea9f510f3be00bde9a0238b9898a1e2315b74/code/guicode/AC.m#L8022
if nargin < 2, id = []; end
[retval, id] = aclog.invoke('ExampleRedNoise-v1.0/analyzer', params, id, @execute);
end

function r = execute(p)
%% Copied from mingsongli/acycle@b52ea9f510f3be00bde9a0238b9898a1e2315b74 code/guicode/AC.m:L8022-L8022
data_name = which('Example-Rednoise0.7-2000.txt');
%% End copied source
%% Copied from mingsongli/acycle@b52ea9f510f3be00bde9a0238b9898a1e2315b74 code/guicode/AC.m:L8032-L8032
data = load(data_name);
%% End copied source
r = struct();
r.data = data;
r.data_name = data_name;
end
