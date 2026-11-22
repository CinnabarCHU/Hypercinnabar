function [retval, id] = analyzer(params, id)
% ExampleGuandao.analyzer parameters: (none).
% Source: https://github.com/mingsongli/acycle/blob/b52ea9f510f3be00bde9a0238b9898a1e2315b74/code/guicode/AC.m#L7810
if nargin < 2, id = []; end
[retval, id] = aclog.invoke('ExampleGuandao-v1.0/analyzer', params, id, @execute);
end

function r = execute(p)
%% Copied from mingsongli/acycle@b52ea9f510f3be00bde9a0238b9898a1e2315b74 code/guicode/AC.m:L7810-L7810
data_name = which('Example-Guandao2AnisianGR.txt');
%% End copied source
%% Copied from mingsongli/acycle@b52ea9f510f3be00bde9a0238b9898a1e2315b74 code/guicode/AC.m:L7820-L7820
data = load(data_name);
%% End copied source
r = struct();
r.data = data;
r.data_name = data_name;
end
