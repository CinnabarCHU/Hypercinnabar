function [retval, id] = analyzer(params, id)
% ExampleExtinction.analyzer parameters: (none).
% Source: https://github.com/mingsongli/acycle/blob/b52ea9f510f3be00bde9a0238b9898a1e2315b74/code/guicode/AC.m#L7848
if nargin < 2, id = []; end
[retval, id] = aclog.invoke('ExampleExtinction-v1.0/analyzer', params, id, @execute);
end

function r = execute(p)
%% Copied from mingsongli/acycle@b52ea9f510f3be00bde9a0238b9898a1e2315b74 code/guicode/AC.m:L7848-L7849
data_name = which('Example-CSA-extinction.txt');
data = load(data_name);
%% End copied source
r = struct();
r.data = data;
end
