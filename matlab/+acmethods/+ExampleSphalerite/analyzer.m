function [retval, id] = analyzer(params, id)
% ExampleSphalerite.analyzer parameters: (none).
% Source: https://github.com/mingsongli/acycle/blob/b52ea9f510f3be00bde9a0238b9898a1e2315b74/code/guicode/AC.m#L8270
if nargin < 2, id = []; end
[retval, id] = aclog.invoke('ExampleSphalerite-v1.0/analyzer', params, id, @execute);
end

function r = execute(p)
%% Copied from mingsongli/acycle@b52ea9f510f3be00bde9a0238b9898a1e2315b74 code/guicode/AC.m:L8270-L8270
data_name = which('Example-Sphalerite.jpg');
%% End copied source
%% Copied from mingsongli/acycle@b52ea9f510f3be00bde9a0238b9898a1e2315b74 code/guicode/AC.m:L8273-L8273
    im_name = imread(data_name);
%% End copied source
r = struct();
r.im_name = im_name;
r.data_name = data_name;
end
