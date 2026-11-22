function [retval, id] = helper(params, id)
% PCA.helper parameters: data_new.
% Source: https://github.com/mingsongli/acycle/blob/b52ea9f510f3be00bde9a0238b9898a1e2315b74/code/guicode/AC.m#L6930
if nargin < 2, id = []; end
[retval, id] = aclog.invoke('PCA-v1.0/helper', params, id, @execute);
end

function r = execute(p)
data_new = p.data_new;
%% Copied from mingsongli/acycle@b52ea9f510f3be00bde9a0238b9898a1e2315b74 code/guicode/AC.m:L6930-L6930
    defaultans = {'1'};
%% End copied source
depthtime=str2double(defaultans{1});
r = struct();
r.data_new = data_new;
r.depthtime = depthtime;
end
