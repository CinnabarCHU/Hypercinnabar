function [retval, id] = analyzer(params, id)
% ExampleLa2004.analyzer parameters: (none).
% Source: https://github.com/mingsongli/acycle/blob/b52ea9f510f3be00bde9a0238b9898a1e2315b74/code/guicode/AC.m#L7909
if nargin < 2, id = []; end
[retval, id] = aclog.invoke('ExampleLa2004-v1.0/analyzer', params, id, @execute);
end

function r = execute(p)
%% Copied from mingsongli/acycle@b52ea9f510f3be00bde9a0238b9898a1e2315b74 code/guicode/AC.m:L7909-L7909
data_name = which('Example-La2004-1E.5T-1P-0-2000.txt');
%% End copied source
%% Copied from mingsongli/acycle@b52ea9f510f3be00bde9a0238b9898a1e2315b74 code/guicode/AC.m:L7920-L7920
data = load(data_name);
%% End copied source
r = struct();
r.data = data;
r.data_name = data_name;
end
