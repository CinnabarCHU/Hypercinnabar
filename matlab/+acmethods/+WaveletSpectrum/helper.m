function [retval, id] = helper(params, id)
% WaveletSpectrum.helper parameters: data.
% Source: https://github.com/mingsongli/acycle/blob/b52ea9f510f3be00bde9a0238b9898a1e2315b74/code/guicode/waveletGUI.m#L397
% Source: https://github.com/mingsongli/acycle/blob/b52ea9f510f3be00bde9a0238b9898a1e2315b74/code/guicode/waveletGUI.m#L409
% Source: https://github.com/mingsongli/acycle/blob/b52ea9f510f3be00bde9a0238b9898a1e2315b74/code/guicode/waveletGUI.fig
if nargin < 2, id = []; end
[retval, id] = aclog.invoke('WaveletSpectrum-v1.0/helper', params, id, @execute);
end

function r = execute(p)
data = p.data;
time=data(:,1); timelen=time(end)-time(1);
%% Copied from mingsongli/acycle@b52ea9f510f3be00bde9a0238b9898a1e2315b74 code/guicode/waveletGUI.m:L397-L408
datax = data(:,1);
datay = data(:,2);
dt = mean(diff(datax));
s0 = 2*dt;    %
pt2 = 2^fix(log2(timelen));
dss = 0.1;
j1 = round(log2(pt2))/dss; % end
pad = 1;
mother = 'MORLET';
param = 6;

[~,period,~,coi] = wavelet(datay,dt,pad,dss,s0,j1,mother,param);
%% End copied source
% The opening callback sets the period text fields, which are read back with str2double.
pt1=str2double(num2str(min(period))); pt2=str2double(num2str(max(coi)));
method_sel=1; data_standardize=0;
r = struct();
r.data = data;
r.pt1 = pt1;
r.pt2 = pt2;
r.dss = dss;
r.pad = pad;
r.mother = mother;
r.param = param;
r.method_sel = method_sel;
r.data_standardize = data_standardize;
end
