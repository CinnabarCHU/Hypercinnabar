function [retval, id] = helper(params, id)
% FixedMovingMean.helper parameters: data.
% Source: https://github.com/mingsongli/acycle/blob/b52ea9f510f3be00bde9a0238b9898a1e2315b74/code/guicode/AC.m#L7216
% Source: https://github.com/mingsongli/acycle/blob/b52ea9f510f3be00bde9a0238b9898a1e2315b74/code/seriesanalysis/movmeanfbw.m#L40
if nargin < 2, id = []; end
[retval, id] = aclog.invoke('FixedMovingMean-v1.0/helper', params, id, @execute);
end

function r = execute(p)
data = p.data;
%% Copied from mingsongli/acycle@b52ea9f510f3be00bde9a0238b9898a1e2315b74 code/guicode/AC.m:L7216-L7225
            time = data(:,1);
            step  = min(diff(time));
            if step == 0
                disp(' Duplicated time detected')
                difft = diff(time);
                difft(difft == 0) = [];
                step  = min(difft);
            end
            value = data(:,2);
            timespan = max(time) - min(time);
%% End copied source
%% Copied from mingsongli/acycle@b52ea9f510f3be00bde9a0238b9898a1e2315b74 code/guicode/AC.m:L7236-L7236
            defaultans = {num2str(timespan*0.3), '0','0.05'};
%% End copied source
window=str2double(defaultans{1}); halfwindow=str2double(defaultans{2}); alpha=str2double(defaultans{3});
r = struct();
r.data = data;
r.window = window;
r.step = step;
r.halfwindow = halfwindow;
r.alpha = alpha;
end
