function [retval, id] = analyzer(params, id)
% Coherence.analyzer parameters: target data windowsize1 nooverlap1 cohthreshold.
% Source: https://github.com/mingsongli/acycle/blob/b52ea9f510f3be00bde9a0238b9898a1e2315b74/code/misc/coherence_update.m#L6
if nargin < 2, id = []; end
[retval, id] = aclog.invoke('Coherence-v1.0/analyzer', params, id, @execute);
end

function r = execute(p)
target = p.target;
data = p.data;
windowsize1 = p.windowsize1;
nooverlap1 = p.nooverlap1;
cohthreshold = p.cohthreshold;
%% Copied from mingsongli/acycle@b52ea9f510f3be00bde9a0238b9898a1e2315b74 code/misc/coherence_update.m:L6-L12
target = datapreproc(target,0);
sr_target = median(diff(target(:,1)));  % sampling rate; using median of diff x

% start and end of the 1st column of the target
tar1 = min(target(:,1));
tar2 = max(target(:,1));
target1 = target;
%% End copied source
%% Copied from mingsongli/acycle@b52ea9f510f3be00bde9a0238b9898a1e2315b74 code/misc/coherence_update.m:L24-L24
windowsize = round(windowsize1/sr_target);  % window size
%% End copied source
%% Copied from mingsongli/acycle@b52ea9f510f3be00bde9a0238b9898a1e2315b74 code/misc/coherence_update.m:L26-L26
nooverlap = round(nooverlap1/sr_target); % number of overlap
%% End copied source
%% Copied from mingsongli/acycle@b52ea9f510f3be00bde9a0238b9898a1e2315b74 code/misc/coherence_update.m:L58-L85
    data = sortrows(data);
    % unique
    data=findduplicate(data);
    % remove empty
    data(any(isinf(data),2),:) = [];
    % start and end of the 1st column of the series
    ser1 = min(data(:,1));
    ser2 = max(data(:,1));
    
    series = data;
    %
    % interpolate series to reference
    series2int = interp1(series(:,1),series(:,2),target1(:,1));
    data  = [target1(:,1),series2int];
    
    % common interval
    sel1 = max(ser1, tar1); % lower bound
    sel2 = min(ser2, tar2); % upper bound
    if sel1 >= sel2
        error('Error: no overlap')
    else
        sel21 = sel2 - sel1;
        if sel21/2 < windowsize1
            warning('Window size is too large. Reset it... Done.')
            windowsize1 = sel21/2;
            windowsize = round(windowsize1/sr_target);
            nooverlap1 = round(windowsize1 * 0.5);
            nooverlap = round(nooverlap1/sr_target);
%% End copied source
%% Copied from mingsongli/acycle@b52ea9f510f3be00bde9a0238b9898a1e2315b74 code/misc/coherence_update.m:L88-L100
        end
    end

    % Select the common interval for both target and series
    [series3] = select_interval(data,sel1,sel2);
    [target2] = select_interval(target1,sel1,sel2);
    
    % series selection and normalize
    y = series3(:,2);
    y = (y - mean(y))/std(y);
    % target selection and normalize
    x = target2(:,2);
    x = (x - mean(x))/std(x);
%% End copied source
%% Copied from mingsongli/acycle@b52ea9f510f3be00bde9a0238b9898a1e2315b74 code/misc/coherence_update.m:L106-L107
        [Cxy,F1, MSC_critical,significant_freqs,significant_Cxy, phase_diff_deg,F2,phase_uncertainty_deg] ...
            = cohac(x,y,sr_target,'hamming',windowsize,nooverlap,cohthreshold,0);
%% End copied source
r = struct();
r.Cxy = Cxy;
r.F1 = F1;
r.MSC_critical = MSC_critical;
r.significant_freqs = significant_freqs;
r.significant_Cxy = significant_Cxy;
r.phase_diff_deg = phase_diff_deg;
r.F2 = F2;
r.phase_uncertainty_deg = phase_uncertainty_deg;
end
