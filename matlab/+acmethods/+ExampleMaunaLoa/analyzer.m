function [retval, id] = analyzer(params, id)
% ExampleMaunaLoa.analyzer parameters: (none).
% Source: https://github.com/mingsongli/acycle/blob/b52ea9f510f3be00bde9a0238b9898a1e2315b74/code/guicode/AC.m#L8156
if nargin < 2, id = []; end
[retval, id] = aclog.invoke('ExampleMaunaLoa-v1.0/analyzer', params, id, @execute);
end

function r = execute(p)
%% Copied from mingsongli/acycle@b52ea9f510f3be00bde9a0238b9898a1e2315b74 code/guicode/AC.m:L8156-L8156
data_name = which('Example-LaunaLoa-Hawaii-CO2-monthly-mean.txt');
%% End copied source
%% Copied from mingsongli/acycle@b52ea9f510f3be00bde9a0238b9898a1e2315b74 code/guicode/AC.m:L8173-L8173
data = load(data_name);
%% End copied source
r = struct();
r.data = data;
r.data_name = data_name;
end
