function [retval, id] = helper(params, id)
% FixedMovingMedian.helper parameters: data.
% Source: https://github.com/mingsongli/acycle/blob/b52ea9f510f3be00bde9a0238b9898a1e2315b74/code/guicode/AC.m#L7455
% Source: https://github.com/mingsongli/acycle/blob/b52ea9f510f3be00bde9a0238b9898a1e2315b74/code/seriesanalysis/movmeanfbw.m#L42
if nargin < 2, id = []; end
[retval, id] = aclog.invoke('FixedMovingMedian-v1.0/helper', params, id, @execute);
end

function r = execute(p)
data = p.data;
%% Copied from mingsongli/acycle@b52ea9f510f3be00bde9a0238b9898a1e2315b74 code/guicode/AC.m:L7455-L7457
            time = data(:,1);
            value = data(:,2);
            timespan = max(time) - min(time);
%% End copied source
%% Copied from mingsongli/acycle@b52ea9f510f3be00bde9a0238b9898a1e2315b74 code/guicode/AC.m:L7468-L7468
            defaultans = {num2str(timespan*0.3), num2str(median(diff(time))), '0'};
%% End copied source
window=str2double(defaultans{1}); step=str2double(defaultans{2}); halfwindow=str2double(defaultans{3});
defaults=acmethods.movmeanfbw.helper(struct('data',data,'window',window,'step',step,'halfwindow',halfwindow));
alpha=defaults.alpha;
r = struct();
r.data = data;
r.window = window;
r.step = step;
r.halfwindow = halfwindow;
r.alpha = alpha;
end
