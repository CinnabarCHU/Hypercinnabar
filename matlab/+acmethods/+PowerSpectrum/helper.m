function [retval, id] = helper(params, id)
% PowerSpectrum.helper parameters: data.
% Source: https://github.com/mingsongli/acycle/blob/b52ea9f510f3be00bde9a0238b9898a1e2315b74/code/guicode/spectrum.m#L157
% Source: https://github.com/mingsongli/acycle/blob/b52ea9f510f3be00bde9a0238b9898a1e2315b74/code/guicode/spectrum.m#L212
% Source: https://github.com/mingsongli/acycle/blob/b52ea9f510f3be00bde9a0238b9898a1e2315b74/code/guicode/spectrum.fig
if nargin < 2, id = []; end
[retval, id] = aclog.invoke('PowerSpectrum-v1.0/helper', params, id, @execute);
end

function r = execute(p)
data = p.data;
data_s=data;
%% Copied from mingsongli/acycle@b52ea9f510f3be00bde9a0238b9898a1e2315b74 code/guicode/spectrum.m:L157-L157
data_s = sortrows(data_s);
%% End copied source
%% Copied from mingsongli/acycle@b52ea9f510f3be00bde9a0238b9898a1e2315b74 code/guicode/spectrum.m:L161-L162
data_s(:,2) = data_s(:,2) - mean(data_s(:,2));
handles.current_data = data_s;
%% End copied source
%% Copied from mingsongli/acycle@b52ea9f510f3be00bde9a0238b9898a1e2315b74 code/guicode/spectrum.m:L166-L181
handles.linlogY = 1;
handles.logfreq = 0;
handles.pad = 1;
handles.checkbox_ar1_v = 0;
handles.checkbox_robustAR1_v = 1;
handles.check_ftest_value = 0;
handles.checkPL = 0;
handles.checkBPL= 0;

handles.timebandwidth = 2;
handles.datasample = 0;  % warning of sampling rate: uneven = 1
Dt = diff(data_s(:,1));

if max(Dt) - min(Dt) > 10 * eps('single')
    handles.datasample = 1;
    handles.method ='Lomb-Scargle spectrum';
%% End copied source
%% Copied from mingsongli/acycle@b52ea9f510f3be00bde9a0238b9898a1e2315b74 code/guicode/spectrum.m:L190-L191
else
    handles.method ='Multi-taper method';
%% End copied source
%% Copied from mingsongli/acycle@b52ea9f510f3be00bde9a0238b9898a1e2315b74 code/guicode/spectrum.m:L196-L199
end

handles.mean = mean(Dt);
handles.nyquist = 1/(2*handles.mean);     % prepare nyquist
%% End copied source
%% Copied from mingsongli/acycle@b52ea9f510f3be00bde9a0238b9898a1e2315b74 code/guicode/spectrum.m:L212-L224
[po,w]=periodogram(data_s(:,2));
fd1=w/(2*pi*handles.mean); 
handles.ValidNyqFreq = fd1(end);

poc = cumsum(po); % cumsum of power
pocnorm = 100*poc/max(poc); % normalized
% the first elements at which the cumulated power exceed 99%
poc1 = find( pocnorm >= 99, 1);
% if the frequency detected is smaller than 85% of nyquist frequency
% suggest a new input max freq.
if fd1(poc1)/fd1(end) <= 0.85
    handles.ValidNyqFreqR = fd1(poc1);
    handles.BiasCorr = 1;
%% End copied source
fmax=str2double(num2str(fd1(poc1)));
%% Copied from mingsongli/acycle@b52ea9f510f3be00bde9a0238b9898a1e2315b74 code/guicode/spectrum.m:L228-L229
else
    handles.BiasCorr = 0;
%% End copied source
    fmax=handles.nyquist;
%% Copied from mingsongli/acycle@b52ea9f510f3be00bde9a0238b9898a1e2315b74 code/guicode/spectrum.m:L230-L230
end
%% End copied source
%% Copied from mingsongli/acycle@b52ea9f510f3be00bde9a0238b9898a1e2315b74 code/guicode/spectrum.m:L1128-L1129
        pfa = [50 10 1 0.01]/100;
        pd = 1 - pfa;
%% End copied source
r=handles; r.data=data_s; r.nw=handles.timebandwidth; r.fmax=fmax; r.fmin=0;
r.padtimes=5; r.nzeropad=5*size(data_s,1); r.pd=pd;
end
