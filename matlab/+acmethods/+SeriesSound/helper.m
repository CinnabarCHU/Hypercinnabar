function [retval, id] = helper(params, id)
% SeriesSound.helper parameters: data.
% Source: https://github.com/mingsongli/acycle/blob/b52ea9f510f3be00bde9a0238b9898a1e2315b74/code/guicode/AC.m#L8599
if nargin < 2, id = []; end
[retval, id] = aclog.invoke('SeriesSound-v1.0/helper', params, id, @execute);
end

function r = execute(p)
data = p.data;
%% Copied from mingsongli/acycle@b52ea9f510f3be00bde9a0238b9898a1e2315b74 code/guicode/AC.m:L8599-L8599
            defaultans = {'5','1','1'};
%% End copied source
r=struct('data',data,'a',str2double(defaultans{1}),'b',str2double(defaultans{2}),'c',str2double(defaultans{3}));
end
