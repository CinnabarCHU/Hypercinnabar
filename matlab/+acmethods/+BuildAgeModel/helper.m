function [retval, id] = helper(params, id)
% BuildAgeModel.helper parameters: data.
% Source: https://github.com/mingsongli/acycle/blob/b52ea9f510f3be00bde9a0238b9898a1e2315b74/code/guicode/AC.m#L3559
if nargin < 2, id = []; end
[retval, id] = aclog.invoke('BuildAgeModel-v1.0/helper', params, id, @execute);
end

function r = execute(p)
data = p.data;
%% Copied from mingsongli/acycle@b52ea9f510f3be00bde9a0238b9898a1e2315b74 code/guicode/AC.m:L3559-L3559
            defaultans = {'41','1'};
%% End copied source
period=str2double(defaultans{1});
pkstrough=str2double(defaultans{2});
r = struct();
r.data = data;
r.period = period;
r.pkstrough = pkstrough;
end
