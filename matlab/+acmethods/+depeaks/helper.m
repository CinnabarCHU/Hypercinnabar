function [retval, id] = helper(params, id)
% depeaks.helper parameters: data.
% Source: https://github.com/mingsongli/acycle/blob/b52ea9f510f3be00bde9a0238b9898a1e2315b74/code/guicode/AC.m#L3427
if nargin < 2, id = []; end
[retval, id] = aclog.invoke('depeaks-v1.0/helper', params, id, @execute);
end

function r = execute(p)
data = p.data;
%% Copied from mingsongli/acycle@b52ea9f510f3be00bde9a0238b9898a1e2315b74 code/guicode/AC.m:L3427-L3427
            value = data(:,2);
%% End copied source
%% Copied from mingsongli/acycle@b52ea9f510f3be00bde9a0238b9898a1e2315b74 code/guicode/AC.m:L3437-L3437
            defaultans = {num2str(min(value)),num2str(max(value))};
%% End copied source
r=struct('data',data,'ymin_cut',str2double(defaultans{1}),'ymax_cut',str2double(defaultans{2}));
end
