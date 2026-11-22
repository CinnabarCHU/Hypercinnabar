function [retval, id] = helper(params, id)
% AmplitudeModulation.helper parameters: data.
% Source: https://github.com/mingsongli/acycle/blob/b52ea9f510f3be00bde9a0238b9898a1e2315b74/code/guicode/AC.m#L2893
if nargin < 2, id = []; end
[retval, id] = aclog.invoke('AmplitudeModulation-v1.0/helper', params, id, @execute);
end

function r = execute(p)
data = p.data;
%% Copied from mingsongli/acycle@b52ea9f510f3be00bde9a0238b9898a1e2315b74 code/guicode/AC.m:L2893-L2894
            diffx = diff(data(:,1));
            if max(diffx) - min(diffx) > eps('single')
%% End copied source
%% Copied from mingsongli/acycle@b52ea9f510f3be00bde9a0238b9898a1e2315b74 code/guicode/AC.m:L2903-L2905
                interpolate_rate = median(diffx);
                [data]=interpolate(data,interpolate_rate);
            end
%% End copied source
r = struct();
r.data = data;
end
