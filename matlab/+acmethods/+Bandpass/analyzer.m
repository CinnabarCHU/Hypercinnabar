function [retval, id] = analyzer(params, id)
% Bandpass.analyzer parameters: data filter flow fhigh taner_c(Taner).
% Source: https://github.com/mingsongli/acycle/blob/b52ea9f510f3be00bde9a0238b9898a1e2315b74/code/misc/update_filter_axes.m#L3
% Source: https://github.com/mingsongli/acycle/blob/b52ea9f510f3be00bde9a0238b9898a1e2315b74/code/guicode/ft.m#L127
if nargin < 2, id = []; end
[retval, id] = aclog.invoke('Bandpass-v1.0/analyzer', params, id, @execute);
end

function r = execute(p)
data = p.data;
filter = p.filter;
flow = p.flow;
fhigh = p.fhigh;
%% Copied from mingsongli/acycle@b52ea9f510f3be00bde9a0238b9898a1e2315b74 code/misc/update_filter_axes.m:L5-L10
datax=data(:,2);
time = data(:,1);
npts = length(time);
dt=mean(diff(time));
nyquist = 1/(2*dt);
rayleigh = 1/(dt*npts);
%% End copied source
if fhigh <= flow
    error('Acycle:Bandpass:FrequencyOrder', 'Expected a positive bandwidth.');
end
%% Copied from mingsongli/acycle@b52ea9f510f3be00bde9a0238b9898a1e2315b74 code/misc/update_filter_axes.m:L34-L36
    fc = (flow+fhigh)/2;
    flch = [flow fc fhigh];
    flch = sort(flch);
%% End copied source
%% Copied from mingsongli/acycle@b52ea9f510f3be00bde9a0238b9898a1e2315b74 code/misc/update_filter_axes.m:L53-L55
flow = flch(1)/nyquist; % lowpass
fcenter = flch(2)/nyquist;
fhigh = flch(3)/nyquist; % highpass
%% End copied source
%% Copied from mingsongli/acycle@b52ea9f510f3be00bde9a0238b9898a1e2315b74 code/misc/update_filter_axes.m:L64-L70
L = length(data(:,2));
dt = mean(diff(data(:,1)));
Y = fft(data(:,2),L);
P2 = abs(Y/L);
P1 = P2(1:floor(L/2)+1);
P1(2:end-1) = 2*P1(2:end-1);
f = 1/dt * (0:(L/2))/L;
%% End copied source
if strcmp(filter, 'Gaussian')
%% Copied from mingsongli/acycle@b52ea9f510f3be00bde9a0238b9898a1e2315b74 code/misc/update_filter_axes.m:L75-L77
    [gaussbandx,filter1,f1]=gaussfilter(datax,dt,flch(2),flch(1),flch(3));
    % Use Hilbert transformation to extract envelope
    gaussbandxAM = abs(hilbert(gaussbandx));
%% End copied source
%% Copied from mingsongli/acycle@b52ea9f510f3be00bde9a0238b9898a1e2315b74 code/misc/update_filter_axes.m:L88-L88
    data_filterout = [time,gaussbandx,gaussbandxAM];
%% End copied source
    response = filter1;
    frequency = f1;
elseif strcmp(filter,'Taner-Hilbert')
    taner_c = p.taner_c;
    existing = evalin('base', 'exist(''tanerfilterenv'',''var'')');
    previous = [];
    if existing, previous = evalin('base','tanerfilterenv'); end
    guard = onCleanup(@() restoreTaner(existing,previous));
%% Copied from mingsongli/acycle@b52ea9f510f3be00bde9a0238b9898a1e2315b74 code/misc/update_filter_axes.m:L94-L98
    [tanhilb,handles.ifaze,handles.ifreq] = ...
    tanerhilbertML(data,flch(2),flch(1),flch(3),taner_c);

    tanerfilterenv = evalin('base','tanerfilterenv');
    tf = tanerfilterenv(1:floor(L/2)+1) ./ max(tanerfilterenv(1:floor(L/2)+1)) .* max(P1);
%% End copied source
%% Copied from mingsongli/acycle@b52ea9f510f3be00bde9a0238b9898a1e2315b74 code/misc/update_filter_axes.m:L117-L117
    data_filterout = tanhilb;
%% End copied source
    response = tf;
    frequency = f;
elseif strcmp(filter,'Cheby1')
%% Copied from mingsongli/acycle@b52ea9f510f3be00bde9a0238b9898a1e2315b74 code/misc/update_filter_axes.m:L126-L135
    d = designfilt('bandpassiir', ...
        'FilterOrder',6, ...
    'PassbandFrequency1',flow,...
    'PassbandFrequency2',fhigh,...
    'PassbandRipple',1,...
    'DesignMethod','cheby1');
    yb = filtfilt(d,datax);
    % Use Hilbert transformation to extract envelope
    ybam = abs(hilbert(yb));
    data_filterout = [time,yb,ybam];
%% End copied source
elseif strcmp(filter,'Ellip')
%% Copied from mingsongli/acycle@b52ea9f510f3be00bde9a0238b9898a1e2315b74 code/misc/update_filter_axes.m:L140-L152
    d = designfilt('bandpassiir', ...
        'FilterOrder',6, ...
    'PassbandFrequency1',flow,...
    'PassbandFrequency2',fhigh,...
    'StopbandAttenuation1',20,...
    'PassbandRipple',1,...
    'StopbandAttenuation2',20,...
    'DesignMethod','ellip');

    yb = filtfilt(d,datax);
    % Use Hilbert transformation to extract envelope
    ybam = abs(hilbert(yb));
    data_filterout = [time,yb,ybam];
%% End copied source
elseif strcmp(filter,'Butter')
%% Copied from mingsongli/acycle@b52ea9f510f3be00bde9a0238b9898a1e2315b74 code/misc/update_filter_axes.m:L157-L165
    d = designfilt('bandpassiir', ...
        'FilterOrder',6, ...
    'HalfPowerFrequency1',flow,...
    'HalfPowerFrequency2',fhigh,...
    'DesignMethod','butter');
    yb = filtfilt(d,datax);  % filtfilt is okay. but it may not be included in some version of Matlab
    % Use Hilbert transformation to extract envelope
    ybam = abs(hilbert(yb));
    data_filterout = [time,yb,ybam];
%% End copied source
else
    error('Acycle:Bandpass:Method', 'Unknown bandpass filter %s.', filter);
end
r = struct();
r.data_filterout = data_filterout;
r.f = f;
r.P1 = P1;
r.filter = filter;
if exist('response','var'), r.response = response; r.frequency = frequency; end
if strcmp(filter,'Taner-Hilbert'), r.ifaze = handles.ifaze; r.ifreq = handles.ifreq; end
end

function restoreTaner(existed, previous)
if existed, assignin('base','tanerfilterenv',previous); else, evalin('base','clear tanerfilterenv'); end
end
