function [retval, id] = helper(params, id)
% Clipping.helper parameters: data.
% Source: https://github.com/mingsongli/acycle/blob/b52ea9f510f3be00bde9a0238b9898a1e2315b74/code/guicode/AC.m#L2369
if nargin < 2, id = []; end
[retval, id] = aclog.invoke('Clipping-v1.0/helper', params, id, @execute);
end

function r = execute(p)
data = p.data;
%% Copied from mingsongli/acycle@b52ea9f510f3be00bde9a0238b9898a1e2315b74 code/guicode/AC.m:L2369-L2369
            defaultans = {num2str(nanmean(data(:,2))), '1','0'};
%% End copied source
clip_value=str2double(defaultans{1}); clip_high=str2double(defaultans{2}); clip_set=str2double(defaultans{3});
r = struct();
r.data = data;
r.clip_value = clip_value;
r.clip_high = clip_high;
r.clip_set = clip_set;
end
