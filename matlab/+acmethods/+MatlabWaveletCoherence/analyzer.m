function [retval, id] = analyzer(params, id)
% MatlabWaveletCoherence.analyzer parameters: dat1 dat2 data_standardize wtcthreshold.
% Source: https://github.com/mingsongli/acycle/blob/b52ea9f510f3be00bde9a0238b9898a1e2315b74/code/package/wavelet/wavecoh_readGUI.m#L116
if nargin < 2, id = []; end
[retval, id] = aclog.invoke('MatlabWaveletCoherence-v1.0/analyzer', params, id, @execute);
end

function r = execute(p)
dat1 = p.dat1;
dat2 = p.dat2;
data_standardize = p.data_standardize;
wtcthreshold = p.wtcthreshold;
%% Copied from mingsongli/acycle@b52ea9f510f3be00bde9a0238b9898a1e2315b74 code/package/wavelet/wavecoh_readGUI.m:L116-L118
    datax = dat1(:,1);
    dat1y = dat1(:,2);
    dat2y = dat2(:,2);
%% End copied source
%% Copied from mingsongli/acycle@b52ea9f510f3be00bde9a0238b9898a1e2315b74 code/package/wavelet/wavecoh_readGUI.m:L125-L133
        variance = std(dat1y)^2;
        variance2 = std(dat2y)^2;
        if data_standardize
            dat1y = (dat1y - mean(dat1y))/sqrt(variance);
            dat2y = (dat2y - mean(dat2y))/sqrt(variance2);
        end
        dt = mean(diff(datax));
        fs = 1/dt;
        [wcoh,wcs,period,coi] = wcoherence(dat1y,dat2y,fs,'PhaseDisplayThreshold',wtcthreshold);
%% End copied source
r = struct();
r.datax = datax;
r.dat1y = dat1y;
r.dat2y = dat2y;
r.wcoh = wcoh;
r.wcs = wcs;
r.period = period;
r.coi = coi;
r.fs = fs;
end
