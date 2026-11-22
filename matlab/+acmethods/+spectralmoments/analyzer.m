function [retval, id] = analyzer(params, id)
% spectralmoments.analyzer parameters: data window step pad srmean smoothmodel padedge.
% Source: https://github.com/mingsongli/acycle/blob/b52ea9f510f3be00bde9a0238b9898a1e2315b74/code/seriesanalysis/spectralmoments.m#L84
if nargin < 2, id = []; end
[retval, id] = aclog.invoke('spectralmoments-v1.0/analyzer', params, id, @execute);
end

function r = execute(p)
data = p.data;
window = p.window;
step = p.step;
pad = p.pad;
srmean = p.srmean;
smoothmodel = p.smoothmodel;
padedge = p.padedge;
%% Copied from mingsongli/acycle@b52ea9f510f3be00bde9a0238b9898a1e2315b74 code/seriesanalysis/spectralmoments.m:L84-L91
if srmean < 0; error('Mean sedimentation rate must be > 0'); end
if pad < 1; error('padding must be > 0'); end
if step <= 0; error('Step must be larger than 0'); end

if padedge == 1
    data = zeropad2(data,window,1);
end

%% End copied source
%% Copied from mingsongli/acycle@b52ea9f510f3be00bde9a0238b9898a1e2315b74 code/seriesanalysis/spectralmoments.m:L94-L139
x = data(:,1); % depth 
y = data(:,2); % value

dt = median(diff(x)); % sampling rate

if step < dt
    step = dt;
end

npts = length(x); % number of rows of data

if window >= npts * dt
    error('Error in spectralmoments. Window must be smaller than data length')
end

n_win = floor(window/dt);  % number of data within 1 window
n_step = floor(step/dt); % number of data for 1 step
npts_new1 = npts - n_win +1; % size of y_grid if step = 1
npts_new = ceil(npts_new1/n_step); % size of y_grid

%
if mod(n_win,2)==0
    nstart = (n_win/2);
else
    nstart = (n_win+1)/2; % first data in y_grid
end

z = zeros(npts_new,n_win);
y_grid = zeros(npts_new,1);
uf = zeros(npts_new,1);
Bw = zeros(npts_new,1);

% read data y for each n and detrend before saving data in z
j=1;
for i = 1: n_step : npts
    k = i+n_win-1; %
    zz = y(i:k);
    c = detrend(zz);
    z(j,:) = c';  
    y_grid(j,:)=x(nstart+i-1);
    j = j+1;
    if j > npts_new
        break
    end
end

%% End copied source
%% Copied from mingsongli/acycle@b52ea9f510f3be00bde9a0238b9898a1e2315b74 code/seriesanalysis/spectralmoments.m:L153-L158
for i =1:npts_new
    d = z(i,:);
    [pxx,f] = periodogram(d,[],pad*n_win,1/dt);
    uf(i) = sum(f.*pxx./sum(pxx));
    BW2 = sum((f-uf(i)).^2 .* pxx / sum(pxx));
    Bw(i) = sqrt(BW2);
%% End copied source
%% Copied from mingsongli/acycle@b52ea9f510f3be00bde9a0238b9898a1e2315b74 code/seriesanalysis/spectralmoments.m:L166-L166
end
%% End copied source
%% Copied from mingsongli/acycle@b52ea9f510f3be00bde9a0238b9898a1e2315b74 code/seriesanalysis/spectralmoments.m:L172-L173
depth = linspace((x(1)+window/2), (x(end)-window/2), npts_new);
depth = depth';
%% End copied source
%% Copied from mingsongli/acycle@b52ea9f510f3be00bde9a0238b9898a1e2315b74 code/seriesanalysis/spectralmoments.m:L176-L186
    if strcmp(smoothmodel, 'poly')
        %windowsize = round(window/dt);
        windowsize = round(window/n_step);
        [~,Bwtrend] = DetrendSignalPP(Bw,windowsize,n_step,2);
    else
        span = window/abs(depth(end)-depth(1));
        Bwtrend = smooth(depth,Bw, span,smoothmodel);
    end
    sr = srmean * Bw(1) ./ Bwtrend;
    sr = sr - mean(sr);
    sr = sr + srmean;
%% End copied source
r = struct();
r.depth = depth;
r.uf = uf;
r.Bw = Bw;
r.Bwtrend = Bwtrend;
r.sr = sr;
end
