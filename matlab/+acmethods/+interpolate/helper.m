function [retval, id] = helper(params, id)
% interpolate.helper parameters: data.
% Source: https://github.com/mingsongli/acycle/blob/b52ea9f510f3be00bde9a0238b9898a1e2315b74/code/guicode/AC.m#L2226
if nargin < 2, id = []; end
[retval, id] = aclog.invoke('interpolate-v1.0/helper', params, id, @execute);
end

function r = execute(p)
data = p.data;
%% Copied from mingsongli/acycle@b52ea9f510f3be00bde9a0238b9898a1e2315b74 code/guicode/AC.m:L2226-L2227
                time = data(:,1);
                srmedian = median(diff(time));
%% End copied source
interpolate_rate=str2double(num2str(srmedian));
r = struct();
r.data = data;
r.interpolate_rate = interpolate_rate;
end
