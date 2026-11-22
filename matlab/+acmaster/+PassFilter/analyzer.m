function [retval,id] = analyzer(params,id)
% PassFilter.analyzer parameters: data passtype filter_s f11 f12(bandstop).
% Source: https://github.com/mingsongli/acycle/blob/dcba4279168745b563e0535b954297023dd62fc7/code/misc/update_filter_axes4.m
if nargin < 2, id = []; end
[retval,id] = accompat.masterInvoke('PassFilter-v3.1.1+dcba427/analyzer',params,id,@execute);
end

function r = execute(p)
data = p.data;
passtype = p.passtype;
filter_s = p.filter_s;
f11 = p.f11;
%% Copied from mingsongli/acycle@dcba4279168745b563e0535b954297023dd62fc7 code/misc/update_filter_axes4.m:L12-L24
datax=data(:,2);
time = data(:,1);

L = length(data(:,2));
dt = mean(diff(data(:,1)));
Y = fft(data(:,2),L);
P2 = abs(Y/L);
P1 = P2(1:floor(L/2)+1);
P1(2:end-1) = 2*P1(2:end-1);
f = 1/dt * (0:(L/2))/L;

nyquist = 1/(2*dt);
rayleigh = 1/(dt*L);
%% End copied source
switch passtype
case {'highpassiir','lowpassiir'}
%% Copied from mingsongli/acycle@dcba4279168745b563e0535b954297023dd62fc7 code/misc/update_filter_axes4.m:L30-L30
    f1 = f11/nyquist;
%% End copied source
case 'bandstopiir'
    f12=p.f12;
%% Copied from mingsongli/acycle@dcba4279168745b563e0535b954297023dd62fc7 code/misc/update_filter_axes4.m:L41-L45
    flow = min(f12,f11)/nyquist; % lowpass
    fhigh = max(f12,f11)/nyquist; % highpass
    passband1 = flow + 2*rayleigh/nyquist;
    passband2 = fhigh - 2*rayleigh/nyquist;
    f1 = [flow fhigh];
%% End copied source
otherwise
    error('Acycle:PassFilter:Type','Unknown pass type.');
end
if any(strcmp(passtype,{'highpassiir','lowpassiir'}))
%% Copied from mingsongli/acycle@dcba4279168745b563e0535b954297023dd62fc7 code/misc/update_filter_axes4.m:L80-L84
    if strcmp(filter_s,'Butter')
        d = designfilt(passtype, ...
        'FilterOrder',6, ...
        'HalfPowerFrequency',f1,...
        'DesignMethod','butter');
%% End copied source
%% Copied from mingsongli/acycle@dcba4279168745b563e0535b954297023dd62fc7 code/misc/update_filter_axes4.m:L87-L92
    elseif strcmp(filter_s,'Cheby1')
        d = designfilt(passtype, ...
        'FilterOrder',6, ...
        'PassbandFrequency',f1,...
        'PassbandRipple',1,...
        'DesignMethod','cheby1');
%% End copied source
%% Copied from mingsongli/acycle@dcba4279168745b563e0535b954297023dd62fc7 code/misc/update_filter_axes4.m:L95-L101
    elseif strcmp(filter_s,'Ellip')
        d = designfilt(passtype, ...
        'FilterOrder',6, ...
        'PassbandFrequency',f1,...
        'PassbandRipple',1,...
        'StopbandAttenuation',20,...
        'DesignMethod','ellip');
%% End copied source
    else, error('Acycle:PassFilter:Method','Unknown IIR design.'); end
else
%% Copied from mingsongli/acycle@dcba4279168745b563e0535b954297023dd62fc7 code/misc/update_filter_axes4.m:L105-L113
    flow = f1(1);
    fhigh = f1(2);
    
    if strcmp(filter_s,'Butter')
        d = designfilt(passtype, ...
        'FilterOrder',6, ...
        'HalfPowerFrequency1',flow,...
        'HalfPowerFrequency2',fhigh,...
        'DesignMethod','butter');
%% End copied source
%% Copied from mingsongli/acycle@dcba4279168745b563e0535b954297023dd62fc7 code/misc/update_filter_axes4.m:L115-L125
    elseif strcmp(filter_s,'Cheby1')
        d = designfilt(passtype, ...
        'PassbandFrequency1',flow,...
        'StopbandFrequency1',passband1,...
        'StopbandFrequency2',passband2,...
        'PassbandFrequency2',fhigh,...
        'PassbandRipple1',1,...
        'PassbandRipple2',1,...
        'StopbandAttenuation',20,...
        'DesignMethod','cheby1',...
        'MatchExactly','both');
%% End copied source
%% Copied from mingsongli/acycle@dcba4279168745b563e0535b954297023dd62fc7 code/misc/update_filter_axes4.m:L127-L137
    elseif strcmp(filter_s,'Ellip')
        d = designfilt(passtype, ...
        'PassbandFrequency1',flow,...
        'StopbandFrequency1',passband1,...
        'StopbandFrequency2',passband2,...
        'PassbandFrequency2',fhigh,...
        'PassbandRipple1',1,...
        'PassbandRipple2',1,...
        'StopbandAttenuation',20,...
        'DesignMethod','ellip',...
        'MatchExactly','both');
%% End copied source
    else, error('Acycle:PassFilter:Method','Unknown IIR design.'); end
end
%% Copied from mingsongli/acycle@dcba4279168745b563e0535b954297023dd62fc7 code/misc/update_filter_axes4.m:L145-L146
yb = filtfilt(d,datax);  % filtfilt is okay. but it may not be included in some version of Matlab
data_filterout = [time,yb];
%% End copied source
r = struct();
r.data_filterout = data_filterout;
r.f = f;
r.P1 = P1;
end
