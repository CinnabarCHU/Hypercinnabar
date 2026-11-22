function [retval, id] = analyzer(params, id)
% DYNOT.analyzer parameters: data sampa sampb parmhat window1 window2 nw1 nw2 pad step nout shiftwin padwin f fza fzb ftmin ftmax nmc percent.
% Source: https://github.com/mingsongli/acycle/blob/b52ea9f510f3be00bde9a0238b9898a1e2315b74/code/guicode/DYNOS.m#L406
if nargin < 2, id = []; end
[retval, id] = aclog.invoke('DYNOT-v1.0/analyzer', params, id, @execute);
end

function r = execute(p)
data = p.data;
sampa = p.sampa;
sampb = p.sampb;
parmhat = p.parmhat;
window1 = p.window1;
window2 = p.window2;
nw1 = p.nw1;
nw2 = p.nw2;
pad = p.pad;
step = p.step;
nout = p.nout;
shiftwin = p.shiftwin;
padwin = p.padwin;
f = p.f;
fza = p.fza;
fzb = p.fzb;
ftmin = p.ftmin;
ftmax = p.ftmax;
nmc = p.nmc;
percent = p.percent;
%% Copied from mingsongli/acycle@b52ea9f510f3be00bde9a0238b9898a1e2315b74 code/guicode/DYNOS.m:L406-L410
percent = sort(unique(percent));
percent = percent(percent~=0);
if isempty(percent)
    percent = 50;
end
%% End copied source
%% Copied from mingsongli/acycle@b52ea9f510f3be00bde9a0238b9898a1e2315b74 code/guicode/DYNOS.m:L414-L441
if nw2==nw1
    randnw = 0*rand(nmc,1);
else
    randnw = randi(2*(nw2-nw1),[nmc 1]);
end
%
samplez = wblrnd(parmhat(1),parmhat(2),[nmc 1]);
samplez(samplez<sampa) = sampa+(sampb-sampa)*rand(1);
samplez(samplez>sampb) = sampa+(sampb-sampa)*rand(1);
randwindow=rand(nmc,1);
windowz = window1+(window2-window1)*randwindow; % windowz range from window1 to window2
nwz = nw1 + randnw/2;                       % nw range from nw1 to nw2
bw = nwz./windowz;
ncol = length(f);
f3m =[];
for i=1:ncol
    fz = fza+(fzb-fza)*rand(nmc,1);
    f3m(:,2*i-1) = f(i)-fz.*bw;
    fz = fza+(fzb-fza)*rand(nmc,1);
    f3m(:,2*i)   = f(i)+fz.*bw;
end
f3m(f3m < ftmin) = ftmin;
f3m(f3m > ftmax) = ftmax;
%% Set plot y axis grid and a empty powy 
y_grid = linspace(data(1,1),data(length(data(:,1)),1),nout);
y_grid = y_grid';
powy = zeros(nout,nmc);  % for interpolated series
powmean = zeros(1,nmc);
%% End copied source
%% Copied from mingsongli/acycle@b52ea9f510f3be00bde9a0238b9898a1e2315b74 code/guicode/DYNOS.m:L455-L459
if shiftwin == 1
    shiftwin1 = 0;
else
    shiftwin1 = shiftwin;
end
%% End copied source
%% Copied from mingsongli/acycle@b52ea9f510f3be00bde9a0238b9898a1e2315b74 code/guicode/DYNOS.m:L666-L666
    for i=1:nmc
%% End copied source
%% Copied from mingsongli/acycle@b52ea9f510f3be00bde9a0238b9898a1e2315b74 code/guicode/DYNOS.m:L670-L690
        dat = [];
        dat(:,1) = data(1,1):samplez(i):data(length(data(:,1)),1);
        dat(:,2) = interp1(data(:,1),data(:,2),dat(:,1),'pchip'); 
        f3=f3m(i,:);
        window = windowz(i);
        % detrending
        % Fit a first‐order polynomial (linear trend)
        p = polyfit(dat(:,1), dat(:,2), 1);          % p(1) = slope, p(2) = intercept
        % If you want to replace the second column in `data` with the detrended series:
        dat(:,2) = dat(:,2) - polyval(p, dat(:,1));
        % half-window padding
        if padwin > 0
            dat = zeropad2(dat,window,padwin);
        end
        
        y_grid_rand=randi([-1*shiftwin1,shiftwin1])*window/2;   % shift y_grid1
        nw = nwz(i);
        [power]=pdan(dat,f3,window,nw,ftmin,ftmax,step,pad); % power ratio of data series
        powy(:,i)=interp1((power(:,1)+y_grid_rand/shiftwin),power(:,2),y_grid);
        power2=power(:,2); %
        powmean(1,i)=mean(power2(~isnan(power2))); % mean power of each calculation
%% End copied source
%% Copied from mingsongli/acycle@b52ea9f510f3be00bde9a0238b9898a1e2315b74 code/guicode/DYNOS.m:L712-L712
    end
%% End copied source
%% Copied from mingsongli/acycle@b52ea9f510f3be00bde9a0238b9898a1e2315b74 code/guicode/DYNOS.m:L717-L726
powmean_mean = mean(powmean);  % mean power ratio of each calculation
powmeanadjust = [];  % Make sure each running of this script don't be affected by previous running
powmeanadjust = powmean_mean./powmean;
powmeanadjust = repmat(powmeanadjust,nout,1);
powyadjust = powmeanadjust.*powy;
% Dec 10, 2016 Add by Mingsong Li. To avoid a problem that total power > 1
maxp = max(max(powyadjust));
if maxp > 1
    powyadjust=powyadjust/maxp;
end
%% End copied source
%% Copied from mingsongli/acycle@b52ea9f510f3be00bde9a0238b9898a1e2315b74 code/guicode/DYNOS.m:L737-L751
npercent  = length(percent);
npercent2 = (length(percent)-1)/2;
powyp = prctile(powy, percent,2);
powyadjustp=prctile(powyadjust, percent,2);
powyad_p_nan =[];
y_grid_nan=[];
% Remove NaN within powyadjustp
for i = 1: npercent
    powyadjustp1=powyadjustp(:,i);
    powyad_p_nan(:,i) = powyadjustp1(~isnan(powyadjustp1));
end
y_grid_nan = y_grid(~isnan(powyadjustp(:,1)));
powyad_p_nan = 1 - powyad_p_nan;
powyadjust = 1- powyadjust;
powyadjustp = 1 - powyadjustp;
%% End copied source
r = struct();
r.y_grid = y_grid;
r.y_grid_nan = y_grid_nan;
r.powy = powy;
r.powmean = powmean;
r.powyadjust = powyadjust;
r.powyp = powyp;
r.powyadjustp = powyadjustp;
r.powyad_p_nan = powyad_p_nan;
r.samplez = samplez;
r.windowz = windowz;
r.nwz = nwz;
r.f3m = f3m;
r.npercent = npercent;
r.npercent2 = npercent2;
r.data = data;
end
