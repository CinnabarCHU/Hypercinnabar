function [retval, id] = analyzer(params, id)
% Recurrence.analyzer parameters: data_s method_use normFlag embed_m embed_tau threshold showdet w ws theiler_window lmin.
% Source: https://github.com/mingsongli/acycle/blob/b52ea9f510f3be00bde9a0238b9898a1e2315b74/code/misc/update_recplot.m#L94
% Source: https://github.com/mingsongli/acycle/blob/b52ea9f510f3be00bde9a0238b9898a1e2315b74/code/guicode/RecPlotGUI.m#L775
if nargin < 2, id = []; end
[retval, id] = aclog.invoke('Recurrence-v1.0/analyzer', params, id, @execute);
end

function r = execute(p)
data_s = p.data_s;
method_use = p.method_use;
normFlag = p.normFlag;
embed_m = p.embed_m;
embed_tau = p.embed_tau;
threshold = p.threshold;
showdet = p.showdet;
w = p.w;
ws = p.ws;
theiler_window = p.theiler_window;
lmin = p.lmin;
handles=struct('normFlag',normFlag,'method_use',method_use,'embed_m',embed_m,'embed_tau',embed_tau);
%% Copied from mingsongli/acycle@b52ea9f510f3be00bde9a0238b9898a1e2315b74 code/misc/update_recplot.m:L3-L3
[N, ncol] = size(data_s);
%% End copied source
%% Copied from mingsongli/acycle@b52ea9f510f3be00bde9a0238b9898a1e2315b74 code/misc/update_recplot.m:L6-L12
if ncol == 1
    x = data_s;
    t = 1:N;
else
    x = data_s(:,2);
    t = data_s(:,1);
end
%% End copied source
[~,S,~]=local_build_S_and_threshold(x,normFlag);
%% Copied from mingsongli/acycle@b52ea9f510f3be00bde9a0238b9898a1e2315b74 code/misc/update_recplot.m:L14-L25
%% ---- normalization ----
if isfield(handles,'normFlag') && strcmpi(handles.normFlag,'norm')
    x0 = x(:);
    mu = mean(x0,'omitnan');
    sig = std(x0,'omitnan');

    if sig > 0
        x = (x - mu) ./ sig;
    else
        warning('std(x) = 0, skip normalization');
    end
end
%% End copied source
%% Copied from mingsongli/acycle@b52ea9f510f3be00bde9a0238b9898a1e2315b74 code/misc/update_recplot.m:L90-L94
% --- interpret threshold for RP plotting (METHOD-AWARE, consistent with crp_pdist) ---
% Goal: always produce a valid eps_plot so that RP = (S < eps_plot) has no issues.
%   - rr/fa/in : threshold means RR (0..1) or percent (0..100), convert -> eps_plot from S distribution
%   - others   : threshold means eps (distance), clamp to valid distance range
[eps_plot, rr_plot, threshold_plot_used] = local_threshold_to_eps_for_plot(threshold, handles.method_use, S);
%% End copied source
DETx=[]; DETy=[]; testi=[];
%% Copied from mingsongli/acycle@b52ea9f510f3be00bde9a0238b9898a1e2315b74 code/misc/update_recplot.m:L102-L110
%% ---- DET calculation ----
if showdet == 1
    if ncol == 1
        winN = N;
        wsN  = 1;
    else
        winN = max(data_s(:,1)) - min(data_s(:,1));
        wsN  = median(diff(data_s(:,1)));
    end
%% End copied source
%% Copied from mingsongli/acycle@b52ea9f510f3be00bde9a0238b9898a1e2315b74 code/misc/update_recplot.m:L114-L116
    if ~isnan(w)
        if w > winN
            w = winN;
%% End copied source
%% Copied from mingsongli/acycle@b52ea9f510f3be00bde9a0238b9898a1e2315b74 code/misc/update_recplot.m:L119-L120
        elseif w <= 0
            w = winN;
%% End copied source
%% Copied from mingsongli/acycle@b52ea9f510f3be00bde9a0238b9898a1e2315b74 code/misc/update_recplot.m:L123-L126
        end
        if ncol > 1
            w = round(N * w / winN);  % force integer
        end
%% End copied source
else, error('Acycle:Recurrence:Window','Invalid window.'); end
%% Copied from mingsongli/acycle@b52ea9f510f3be00bde9a0238b9898a1e2315b74 code/misc/update_recplot.m:L134-L136
    if ~isnan(ws)
        if ws > w
            ws = w;
%% End copied source
%% Copied from mingsongli/acycle@b52ea9f510f3be00bde9a0238b9898a1e2315b74 code/misc/update_recplot.m:L139-L140
        elseif ws < wsN
            ws = wsN;
%% End copied source
%% Copied from mingsongli/acycle@b52ea9f510f3be00bde9a0238b9898a1e2315b74 code/misc/update_recplot.m:L143-L146
        end
        if ncol > 1
            ws = round(N * ws / winN);  % force integer
        end
%% End copied source
else, error('Acycle:Recurrence:Step','Invalid sliding step.'); end
%% Copied from mingsongli/acycle@b52ea9f510f3be00bde9a0238b9898a1e2315b74 code/misc/update_recplot.m:L171-L172
    m = handles.embed_m;
    tau = handles.embed_tau;
%% End copied source
%% Copied from mingsongli/acycle@b52ea9f510f3be00bde9a0238b9898a1e2315b74 code/misc/update_recplot.m:L195-L199
    [DETy, testi] = crp_pdist(x, w, ws, theiler_window, lmin, 0, threshold, handles.method_use, handles.normFlag, m, tau);


    DETx = round(t(testi) + 1/2 * winN * w / N);
end
%% End copied source
r = struct();
r.t = t;
r.x = x;
r.S = S;
r.eps_plot = eps_plot;
r.rr_plot = rr_plot;
r.threshold_plot_used = threshold_plot_used;
r.DETx = DETx;
r.DETy = DETy;
r.testi = testi;
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
%% Copied from mingsongli/acycle@b52ea9f510f3be00bde9a0238b9898a1e2315b74 code/misc/update_recplot.m:L368-L466
function [eps_plot, rr_plot, thr_used] = local_threshold_to_eps_for_plot(threshold, method_use, S)
% Convert GUI "threshold" into eps_plot for RP visualization, consistent with crp_pdist semantics.
% Returns:
%   eps_plot : distance threshold used for RP image (S < eps_plot)
%   rr_plot  : RR used when method is rr/fa/in, else NaN
%   thr_used : possibly corrected threshold value for GUI display

thr_used = threshold;

% basic check
if nargin < 2 || isempty(method_use), method_use = 'rr'; end
if nargin < 1 || isempty(threshold) || ~isfinite(threshold)
    threshold = 0.10;
    thr_used  = threshold;
end

method_use = lower(string(method_use));
rr_methods = ["rr","fa","in"];

% get finite off-diagonal distances for robust stats/clamping
d = local_offdiag_distvec(S);
if isempty(d)
    % fallback: avoid crash; RP will be empty
    eps_plot = 0;
    rr_plot  = NaN;
    return;
end
dmin = min(d);
dmax = max(d);

if any(method_use == rr_methods)
    % RR mode: threshold should be RR (0..1) or percent (0..100)
    if threshold <= 0
        rr = 0.10;
        thr_used = rr;
        warning('Threshold <= 0 in RR mode. Reset to 0.10.');
    elseif threshold <= 1
        rr = threshold;
    elseif threshold <= 100
        rr = threshold/100;
    else
        % >100 is nonsensical for RR/percent; clamp to 100%
        rr = 1.0;
        thr_used = 100;
        warning('Threshold > 100 in RR mode. Clamped to 100%% (RR=1).');
    end

    % keep rr strictly inside [0,1]
    rr = max(0, min(1, rr));
    rr_plot = rr;

    % convert RR -> eps on S distribution
    eps_plot = local_eps_from_rr_for_plot(S, rr_plot);

    % safety clamp to [dmin,dmax] (should already be, but keep it robust)
    eps_plot = max(dmin, min(dmax, eps_plot));
else
    % EPS mode: threshold is a distance (even if <=1)
    rr_plot = NaN;
    eps_plot = double(threshold);
 
    % clamp eps to distance range
    if eps_plot > dmax
        eps_plot = dmax;
        thr_used = eps_plot;
        warning(['Threshold is too big for eps-mode. Clamped to max distance = ', num2str(dmax)]);
    elseif eps_plot < dmin
        eps_plot = dmin;
        thr_used = eps_plot;
        warning(['Threshold is too small for eps-mode. Clamped to min distance = ', num2str(dmin)]);
    end
end

end

function d = local_offdiag_distvec(D)
% Extract finite upper-triangular off-diagonal distances as a vector.
n = size(D,1);
mask = triu(true(n), 1);      % exclude diagonal
d = D(mask);
d = d(isfinite(d));
d = double(d(:));
end

function epsk = local_eps_from_rr_for_plot(D, rr)
% RR -> eps using the upper-triangle distance distribution.
% rr in [0,1]. epsk is the rr-quantile point (discrete).
d = local_offdiag_distvec(D);
if isempty(d)
    epsk = 0;
    return;
end

rr = max(0, min(1, rr));

d = sort(d);
K = max(1, min(numel(d), round(rr * numel(d))));
epsk = d(K);
end
%% End copied source
