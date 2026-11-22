function [retval, id] = helper(params, id)
% AR1Prewhitening.helper parameters: dat.
% Source: https://github.com/mingsongli/acycle/blob/b52ea9f510f3be00bde9a0238b9898a1e2315b74/code/guicode/prewhitenGUI.m#L108
if nargin < 2, id = []; end
[retval, id] = aclog.invoke('AR1Prewhitening-v1.0/helper', params, id, @execute);
end

function r = execute(p)
dat = p.dat;
%% Copied from mingsongli/acycle@b52ea9f510f3be00bde9a0238b9898a1e2315b74 code/guicode/prewhitenGUI.m:L108-L110
diffx = diff(dat(:,1));
% check data
if sum(diffx <= 0) > 0
%% End copied source
%% Copied from mingsongli/acycle@b52ea9f510f3be00bde9a0238b9898a1e2315b74 code/guicode/prewhitenGUI.m:L112-L113
    dat = sortrows(dat);
end
%% End copied source
%% Copied from mingsongli/acycle@b52ea9f510f3be00bde9a0238b9898a1e2315b74 code/guicode/prewhitenGUI.m:L120-L150
[rho]=rhoAR1ML(dat(:,2));

% robust AR1: rho1
dt = median(diff(dat(:,1)));
[po,w]=periodogram(dat(:,2));
fd1=w/(2*pi*dt);
poc = cumsum(po); % cumsum of power
pocnorm = 100*poc/max(poc); % normalized
% the first elements at which the cumulated power exceed 99%
poc1 = find( pocnorm > 99, 1);
% if the frequency detected is smaller than 85% of nyquist frequency
% suggest a new input max freq.
if fd1(poc1)/fd1(end) <= 0.85
    ValidNyqFreq = fd1(poc1);
else
    ValidNyqFreq = fd1(end);
end
% mean power of spectrum
fmax = ValidNyqFreq;
% Nyquist frequency
fn = 1/(2*dt);
% Multi-taper method power spectrum
[pxx,f] = pmtm(dat(:,2),2,length(dat(:,2)));
ft = f/pi*fn;
ft = ft(ft<=fmax);
pxx = pxx(ft<=fmax);
% median-smoothing data numbers
smoothn = round(0.2 * length(pxx));
% median-smoothing
pxxsmooth = moveMedian(pxx,smoothn);  % valid data; for rho evaluation
s0 = mean(pxxsmooth);
%% End copied source
[rhoM,~]=minirhos0(s0,fmax,ft,pxxsmooth,2,0);
r = struct();
r.dat = dat;
r.rho = rho;
r.rhoM = rhoM;
r.data=dat; r.rho1=rho;
end
