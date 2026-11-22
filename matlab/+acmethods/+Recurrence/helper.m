function [retval, id] = helper(params, id)
% Recurrence.helper parameters: data_s.
% Source: https://github.com/mingsongli/acycle/blob/b52ea9f510f3be00bde9a0238b9898a1e2315b74/code/guicode/RecPlotGUI.m#L170
% Source: https://github.com/mingsongli/acycle/blob/b52ea9f510f3be00bde9a0238b9898a1e2315b74/code/guicode/RecPlotGUI.m#L324
% Source: https://github.com/mingsongli/acycle/blob/b52ea9f510f3be00bde9a0238b9898a1e2315b74/code/guicode/RecPlotGUI.m#L775
% Source: https://github.com/mingsongli/acycle/blob/b52ea9f510f3be00bde9a0238b9898a1e2315b74/code/guicode/RecPlotGUI.fig
if nargin < 2, id = []; end
[retval, id] = aclog.invoke('Recurrence-v1.0/helper', params, id, @execute);
end

function r = execute(p)
data_s = p.data_s;
handles.current_data=data_s;
%% Copied from mingsongli/acycle@b52ea9f510f3be00bde9a0238b9898a1e2315b74 code/guicode/RecPlotGUI.m:L170-L171
handles.embed_m   = 1;
handles.embed_tau = 1;
%% End copied source
%% Copied from mingsongli/acycle@b52ea9f510f3be00bde9a0238b9898a1e2315b74 code/guicode/RecPlotGUI.m:L179-L180
handles.method_use = 'max';
handles.normFlag   = 'norm';
%% End copied source
%% Copied from mingsongli/acycle@b52ea9f510f3be00bde9a0238b9898a1e2315b74 code/guicode/RecPlotGUI.m:L324-L324
[N, ncol] = size(data_s);
%% End copied source
%% Copied from mingsongli/acycle@b52ea9f510f3be00bde9a0238b9898a1e2315b74 code/guicode/RecPlotGUI.m:L327-L342
% sliding window size
win_ratio = 0.3; 
theiler_window = 1;
lmin = 2; 

if ncol == 1
    x = data_s;
    t = 1:N;
    w = round(win_ratio * N);
    ws = 1;
    if w/ws > 500
        ws = round(w/300);
    end
else
    diffx = diff(data_s(:,1));
    if max(diffx) - min(diffx) > 10*eps('single')
%% End copied source
%% Copied from mingsongli/acycle@b52ea9f510f3be00bde9a0238b9898a1e2315b74 code/guicode/RecPlotGUI.m:L350-L351
        interpolate_rate = mean(diffx);
        handles.current_data = interpolate(data_s,interpolate_rate);
%% End copied source
%% Copied from mingsongli/acycle@b52ea9f510f3be00bde9a0238b9898a1e2315b74 code/guicode/RecPlotGUI.m:L353-L366
    end
    data_s = handles.current_data;
    x = data_s(:,2);
    t = data_s(:,1);
    ws = median(diffx);
    wmax = abs((max(t) - min(t)));  % 30%
    w = ws * 30;
    if w > wmax
        w = wmax;
    end
end

% ---- build distance matrix + default threshold (based on normFlag) ----
[x_forS, S, threshold] = local_build_S_and_threshold(x, handles.normFlag);
%% End copied source
r=struct('data_s',data_s,'threshold',str2double(num2str(threshold)),'w',str2double(num2str(w)), ...
    'ws',str2double(num2str(ws)),'theiler_window',theiler_window,'lmin',lmin,'embed_m',handles.embed_m, ...
    'embed_tau',handles.embed_tau,'method_use',handles.method_use,'normFlag',handles.normFlag);
r.showseries=0;
r.showdet=0;
r.fliptime=0;
r.flipseries=0;
r.ylabeli='Value';
end

%% Copied from mingsongli/acycle@b52ea9f510f3be00bde9a0238b9898a1e2315b74 code/guicode/RecPlotGUI.m:L775-L815
function [x_use, S, threshold] = local_build_S_and_threshold(x, normFlag)
% Build distance matrix S and a reasonable default threshold
% normFlag: 'norm' => zscore; 'nonorm' => raw

x_use = double(x(:));

if nargin < 2 || isempty(normFlag), normFlag = 'nonorm'; end
nf = lower(strtrim(string(normFlag)));

% legacy compatibility
if nf == "narow", nf = "nonorm"; end
if nf == "normalize" || nf == "zscore", nf = "norm"; end

if nf == "norm"
    mu  = mean(x_use,'omitnan');
    sig = std(x_use,'omitnan');
    if isfinite(sig) && sig > 0
        x_use = (x_use - mu) ./ sig;
    end
end

N = numel(x_use);
S = zeros(N, N);
for i = 1:N
    S(:,i) = abs(x_use(i) - x_use);
end

% Default threshold heuristic (same formula as your original, but omit NaNs)
d = S(:);
d = d(isfinite(d));

if isempty(d)
    threshold = 0.1;
else
    threshold = median(d) - 0.5 * std(d);
end

% safety: threshold must be finite and within [min,max] of distances
dmin = min(d); dmax = max(d);
if ~isfinite(threshold), threshold = 0.1; end
threshold = max(dmin, min(dmax, threshold));
%% End copied source
end
