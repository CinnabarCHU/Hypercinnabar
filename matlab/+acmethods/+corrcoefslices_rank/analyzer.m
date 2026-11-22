function [retval, id] = analyzer(params, id)
% corrcoefslices_rank.analyzer parameters: dat target orbit7 dt pad sr1 sr2 srstep adjust red nsim slices method.
% Source: https://github.com/mingsongli/acycle/blob/b52ea9f510f3be00bde9a0238b9898a1e2315b74/code/corrcoef/corrcoefslices_rank.m#L90
if nargin < 2, id = []; end
[retval, id] = aclog.invoke('corrcoefslices_rank-v1.0/analyzer', params, id, @execute);
end

function r = execute(p)
dat = p.dat;
target = p.target;
orbit7 = p.orbit7;
dt = p.dt;
pad = p.pad;
sr1 = p.sr1;
sr2 = p.sr2;
srstep = p.srstep;
adjust = p.adjust;
red = p.red;
nsim = p.nsim;
slices = p.slices;
method = p.method;
%% Copied from mingsongli/acycle@b52ea9f510f3be00bde9a0238b9898a1e2315b74 code/corrcoef/corrcoefslices_rank.m:L87-L105
display = 1;  % show simulation steps

%% Slice
if isreal(slices) && slices > 0 && ~mod(slices,1)
   if slices > 1
       dat_slice = data_slices(dat,slices);  % remove mean value; cut into slices
       dat_demean = [dat(:,1),detrend(dat(:,2),0)];
   else
       time = dat(:,1);
       %value = (dat(:,2)-mean(dat(:,2)))/std(dat(:,2));  % standardized
       value = dat(:,2);
       dat_slice = [time,detrend(value,0)];  % subtract mean value
       dat_demean = dat_slice;
   end

else
    disp('Error: Number of split slices must be a real, positive AND integer number.')
    return;
end
%% End copied source
%% Copied from mingsongli/acycle@b52ea9f510f3be00bde9a0238b9898a1e2315b74 code/corrcoef/corrcoefslices_rank.m:L121-L154
dataf =[];
datap =[];
for j = 1: slices
    dat_nyq = 1/(2*dt);   % Nyquist
    dat_ray = 1/(length(dat_slice(:,1)) * dt);  % rayleigh
    [p,f] = periodogram(dat_slice(:,2*j),[],pad,1/dt);  % power of dat
    % remove AR1 noise
    if red == 2
        [theored]=theoredar1ML(dat(:,2),f,mean(p),dt);
        p = p ./ theored;
        p = p - 1;
        p(p<0) = 0;   % power removing AR(1) noise
    elseif red == 1
        [theored]=theoredar1ML(dat(:,2),f,mean(p),dt);
        p = p - theored;
        p(p<0) = 0;   % power removing AR(1) noise
    elseif red == 3
        % robust
        theored = redconf_any(f,p,dt,0.25,2);
        p = p - theored;
        p(p<0) = 0;   % power removing AR(1) noise
    elseif and (red >= 50, red < 100)
        [theored]=theoredar1ML(dat(:,2),f,mean(p),dt);
        facchired = 2*gammaincinv(red/100,2)/(2*2);
        tabtchired = theored * facchired;
        p = p ./ tabtchired;
        p = p - 1;
        p(p<0) = 0;   % power removing AR(1) noise
    end
    dataf(:,j) = f;
    datap(:,j) = p;
end
    data = [f,mean(datap,2)];
% plot power spectra
%% End copied source
%% Copied from mingsongli/acycle@b52ea9f510f3be00bde9a0238b9898a1e2315b74 code/corrcoef/corrcoefslices_rank.m:L189-L195
target_real= target;  % save target frequencies-power series
targetnew = targetrebuilt(target);  % get peaks from given target
targetf = targetnew(:,2);
targetp = targetnew(:,1);
%  Number of peaks in the power spectrum of real data series?
[pks,~] = findpeaks(data(:,2));
npks = length(pks);
%% End copied source
%% Copied from mingsongli/acycle@b52ea9f510f3be00bde9a0238b9898a1e2315b74 code/corrcoef/corrcoefslices_rank.m:L199-L200
f_nyq_target = target_real(length(target_real(:,1)),1);
sr0 = f_nyq_target * 100/dat_nyq;
%% End copied source
%% Copied from mingsongli/acycle@b52ea9f510f3be00bde9a0238b9898a1e2315b74 code/corrcoef/corrcoefslices_rank.m:L204-L213
[corrxch,corry_rch,corrpych,nmi] = ...
    cyclecorr(data,targetf,targetp,target_real,orbit7,dat_ray,sr1,sr2,srstep,sr0,adjust,method);
corrCI = [corrxch,corry_rch,corrpych,nmi];

%% simulation:  corry (sr x nsim) correlation coefficient
sr_range = sr1:srstep:sr2;
mpts = length(sr_range);
%critical = 100/mpts;% critical significance level by Steve Meyers

if nsim > 0
%% End copied source
%% Copied from mingsongli/acycle@b52ea9f510f3be00bde9a0238b9898a1e2315b74 code/corrcoef/corrcoefslices_rank.m:L231-L244
    corry = zeros(mpts,nsim);
    for i = 1: nsim
        randspectrum = randspec_sin(f,npks,dat_ray);
        sim_spectum = [f,randspectrum];
        %[prand,frand] = randpermperiodogram(dat_demean,dt,pad); % Mingsong Li, 20180417
        %sim_spectum = [frand,prand]; % Mingsong Li, 20180417
        corryi = cyclecorrsig(sim_spectum,targetf,targetp,target_real,orbit7,dat_ray,sr1,sr2,srstep,sr0,adjust,method);
        if display == 1
            if rem(i,20) == 0
                disp(['>> Step 2: Simulation ',num2str(i),' of ',num2str(nsim)])
            end
        end
        corry(:,i) = corryi;

%% End copied source
%% Copied from mingsongli/acycle@b52ea9f510f3be00bde9a0238b9898a1e2315b74 code/corrcoef/corrcoefslices_rank.m:L255-L255
    end
%% End copied source
%% Copied from mingsongli/acycle@b52ea9f510f3be00bde9a0238b9898a1e2315b74 code/corrcoef/corrcoefslices_rank.m:L262-L292
    corry_sim_sort = sort(corry,2);
    corrlength = length(corry_rch);  % number of tested sed. rate
    corry_per = zeros(corrlength,1);
    
    for i = 1: corrlength
        corry_r1 = corry_rch(i);
        corry_sim_sort1 = corry_sim_sort(i,:);
        corry_per(i) = (100 - invprctile(corry_sim_sort1, corry_r1))/100;
    end
    
%     for i = 1: corrlength
%         corry_r1 = corry_rch(i);
%         corry_sim_sort1 = corry_sim_sort(i,:);
%         corry_sim_sort2 = corry_sim_sort1(corry_sim_sort1<corry_r1); % number of corr-value that is less than real data
%         totallength = length(corry_sim_sort1(~isnan(corry_sim_sort1))); % number of not-null value
%         %corry_per(i) = (totallength-length(corry_sim_sort2))/nsim;
%         corry_per(i) = (totallength-length(corry_sim_sort2)+1)/(totallength+1); % Dec. 29, 2017 revised by M. Li
%         if corry_per(i) == 0
%             corry_per(i) = 1/(totallength+1);
%         end
%     end
    
%     assignin('base','corry_per',corry_per)
%     assignin('base','corrxch',corrxch)
    %% confidence interval estimation for correlation coefficient
    
    corr_h0 = corry_per;  % percentile of the value
    
    orbitn = length(orbit7);

    corr_h0(:,2) = (orbitn-corrCI(:,end));   % number of orbits involved
%% End copied source
%% Copied from mingsongli/acycle@b52ea9f510f3be00bde9a0238b9898a1e2315b74 code/corrcoef/corrcoefslices_rank.m:L367-L370
else
    corr_h0 = zeros(mpts,1);
    corry = [];
end
%% End copied source
r = struct();
r.corrCI = corrCI;
r.corr_h0 = corr_h0;
r.corry = corry;
end

%% Copied from mingsongli/acycle@b52ea9f510f3be00bde9a0238b9898a1e2315b74 code/corrcoef/corrcoefslices_rank.m:L373-L400
function datanew = data_slices(dat, slices)
% INPUT: data input
datanew = [];
if slices <= 1
    return
end
x = dat(:,1);
data_size = size(x);
data_length = data_size(1,1);
t1 = dat(1,1);
tn = dat(data_length,1);
slice = linspace(t1, tn, slices+1);

for i = 1: slices
    data_int = select_interval(dat,slice(i),slice(i+1));
    time = data_int(:,1);
    value = (data_int(:,2)-mean(data_int(:,2)))/std(data_int(:,2));
    data_int = [time,detrend(value,0)];
    time_len(i) = length(time);
    if max(time_len) > time_len(i)
        datanew(1:time_len(i),(2*i-1):(2*i)) = data_int;
    elseif max(time_len) < time_len(i)
        datanew((time_len(i-1)+1):time_len(i),(2*i-3):(2*i-2)) = 0;
        datanew(:,(2*i-1):(2*i)) = data_int;
    else
        datanew(:,(2*i-1):(2*i)) = data_int;
    end
end
%% End copied source
end
