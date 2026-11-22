function [retval, id] = analyzer(params, id)
% ExampleMars.analyzer parameters: (none).
% Source: https://github.com/mingsongli/acycle/blob/b52ea9f510f3be00bde9a0238b9898a1e2315b74/code/guicode/AC.m#L8135
if nargin < 2, id = []; end
[retval, id] = aclog.invoke('ExampleMars-v1.0/analyzer', params, id, @execute);
end

function r = execute(p)
%% Copied from mingsongli/acycle@b52ea9f510f3be00bde9a0238b9898a1e2315b74 code/guicode/AC.m:L8135-L8135
data_name = which('Example-HiRISE-PSP_002733_1880_RED.jpg');
%% End copied source
%% Copied from mingsongli/acycle@b52ea9f510f3be00bde9a0238b9898a1e2315b74 code/guicode/AC.m:L8138-L8138
    im_name = imread(data_name);
%% End copied source
r = struct();
r.im_name = im_name;
r.data_name = data_name;
end
