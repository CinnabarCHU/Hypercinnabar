function [retval, id] = analyzer(params, id)
% ExampleSvalbardPETM.analyzer parameters: (none).
% Source: https://github.com/mingsongli/acycle/blob/b52ea9f510f3be00bde9a0238b9898a1e2315b74/code/guicode/AC.m#L7776
if nargin < 2, id = []; end
[retval, id] = aclog.invoke('ExampleSvalbardPETM-v1.0/analyzer', params, id, @execute);
end

function r = execute(p)
%% Copied from mingsongli/acycle@b52ea9f510f3be00bde9a0238b9898a1e2315b74 code/guicode/AC.m:L7776-L7776
data_name = which('Example-SvalbardPETM-logFe.txt');
%% End copied source
%% Copied from mingsongli/acycle@b52ea9f510f3be00bde9a0238b9898a1e2315b74 code/guicode/AC.m:L7785-L7785
data = load(data_name);
%% End copied source
r = struct();
r.data = data;
r.data_name = data_name;
end
