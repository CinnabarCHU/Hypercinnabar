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
end
