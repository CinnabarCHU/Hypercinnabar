function [retval, id] = helper(params, id)
% MatlabWaveletCoherence.helper parameters: dat1 dat2.
% Source: https://github.com/mingsongli/acycle/blob/b52ea9f510f3be00bde9a0238b9898a1e2315b74/code/package/wavelet/wavecoh_readGUI.m#L17
% Source: https://github.com/mingsongli/acycle/blob/b52ea9f510f3be00bde9a0238b9898a1e2315b74/code/guicode/waveletGUI.m#L170
if nargin < 2, id = []; end
[retval, id] = aclog.invoke('MatlabWaveletCoherence-v1.0/helper', params, id, @execute);
end

function r = execute(p)
dat1 = p.dat1;
dat2 = p.dat2;
%% Copied from mingsongli/acycle@b52ea9f510f3be00bde9a0238b9898a1e2315b74 code/package/wavelet/wavecoh_readGUI.m:L17-L17
dat1 = sortrows(dat1);
%% End copied source
%% Copied from mingsongli/acycle@b52ea9f510f3be00bde9a0238b9898a1e2315b74 code/package/wavelet/wavecoh_readGUI.m:L21-L21
dat2 = sortrows(dat2);
%% End copied source
%% Copied from mingsongli/acycle@b52ea9f510f3be00bde9a0238b9898a1e2315b74 code/package/wavelet/wavecoh_readGUI.m:L26-L40
xmin = max( min(dat1(:,1), min(dat2(:,1))));
xmax = min( max(dat1(:,1), max(dat2(:,1))));
dat1 = select_interval(dat1,xmin,xmax);

% ensure time are equal
Dti1 = diff(dat1(:,1));
dt = mean(Dti1);
if max(Dti1) - min(Dti1) > 10 * eps('single')
    [dat1]=interpolate(dat1,dt);
end
if isequal(dat1(:,1),dat2(:,1))
else
    dat2int2 = interp1(dat2(:,1),dat2(:,2),dat1(:,1));
    dat2  = [dat1(:,1),dat2int2];
end
%% End copied source
r=struct('dat1',dat1,'dat2',dat2,'data_standardize',0,'wtcthreshold',.7);
r.plot_series=1; r.plot_swap=0; r.plot_2d=1; r.plot_linelog=0; r.plot_colorgrid=[];
r.plot_colormap='default'; r.plot_flipx=0; r.plot_flipy=0; r.plot_phase=0; r.plot_coi=1; r.plot_sl=1; r.plot_log2pow=0;
r.unit=''; r.unit_type=0;
time=dat1(:,1); timelen=time(end)-time(1); data=dat1;
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
%% Copied from mingsongli/acycle@b52ea9f510f3be00bde9a0238b9898a1e2315b74 code/guicode/waveletGUI.m:L392-L392
Yticks_default = 2.^(fix(log2(2*dt)):fix(log2(timelen)));
%% End copied source
r.Yticks=Yticks_default; r.pt1=str2double(num2str(min(period))); r.pt2=str2double(num2str(max(coi)));
r.dss=dss; r.pad=pad; r.param=param;
end
