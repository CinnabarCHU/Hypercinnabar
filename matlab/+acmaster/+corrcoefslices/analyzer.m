function [retval,id] = analyzer(params,id)
% corrcoefslices.analyzer parameters: dat target orbit7 dt pad sr1 sr2 srstep adjust red nsim slices; optional legacyTarget.
% Source: https://github.com/mingsongli/acycle/blob/dcba4279168745b563e0535b954297023dd62fc7/code/corrcoef/corrcoefslices.m
if nargin < 2, id = []; end
[retval,id] = accompat.masterInvoke('corrcoefslices-v3.1.1+dcba427/analyzer',params,id,@execute);
end

function r = execute(p)
guard = accompat.cocoTargetPath(p); %#ok<NASGU>
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
%% Copied from mingsongli/acycle@dcba4279168745b563e0535b954297023dd62fc7 code/corrcoef/corrcoefslices.m:L89-L89
display = 1;  % show simulation steps
%% End copied source
%% Copied from mingsongli/acycle@dcba4279168745b563e0535b954297023dd62fc7 code/corrcoef/corrcoefslices.m:L100-L145
if isreal(slices) && slices > 0 && ~mod(slices,1)
   if slices > 1
       dat_slice = data_slices(dat,slices);
   else
       dat_slice = dat;
   end
else
    disp('Error: Number of split slices must be a real, positive AND integer number.')
    return;
end
%% data
dataf =[];
datap =[];
for j = 1: slices
    dat_nyq = 1/(2*dt);   % Nyquist
    dat_ray = 1/(length(dat_slice(:,2*j-1))*dt);  % rayleigh
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
        p(p<0) = 0;
    end
    % remove red% noise
    if and (red >= 50, red < 100)
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
%% End copied source
%% Copied from mingsongli/acycle@dcba4279168745b563e0535b954297023dd62fc7 code/corrcoef/corrcoefslices.m:L164-L170
target_real= target;  % save target frequencies-power series
targetnew = targetrebuilt(target);  % get peaks from given target
targetf = targetnew(:,2);
targetp = targetnew(:,1);
%  Number of peaks in the power spectrum of real data series?
[pks,~] = findpeaks(p);
npks = length(pks);
%% End copied source
%% Copied from mingsongli/acycle@dcba4279168745b563e0535b954297023dd62fc7 code/corrcoef/corrcoefslices.m:L174-L175
f_nyq_target = target_real(length(target_real(:,1)),1);
sr0 = f_nyq_target*100/dat_nyq;
%% End copied source
%% Copied from mingsongli/acycle@dcba4279168745b563e0535b954297023dd62fc7 code/corrcoef/corrcoefslices.m:L178-L184
[corrxch,corry_rch,corrpych,corrloch,corrupch,nmi] = ...
    cyclecorr4(data,targetf,targetp,target_real,orbit7,dat_ray,sr1,sr2,srstep,sr0,adjust);
corrCI = [corrxch,corry_rch,corrpych,corrloch,corrupch,nmi];

%% simulation:  corry (sr x nsim) correlation coefficient
sr_range = sr1:srstep:sr2;
mpts = length(sr_range);
%% End copied source
%% Copied from mingsongli/acycle@dcba4279168745b563e0535b954297023dd62fc7 code/corrcoef/corrcoefslices.m:L205-L214
if nsim > 0
   
        %% Monte Carlo simulation
        corry = zeros(mpts,nsim);
        for i = 1: nsim
            if display == 1
                disp(['>> Step 2: Simulation ',num2str(i),' of ',num2str(nsim)])
            end
            randspectrum = randspec_sin(f,npks,dat_ray);
            [corry(:,i)] = cyclecorr4sig([f,randspectrum],targetf,targetp,target_real,orbit7,dat_ray,sr1,sr2,srstep,sr0,adjust);
%% End copied source
%% Copied from mingsongli/acycle@dcba4279168745b563e0535b954297023dd62fc7 code/corrcoef/corrcoefslices.m:L221-L221
        end
%% End copied source
%% Copied from mingsongli/acycle@dcba4279168745b563e0535b954297023dd62fc7 code/corrcoef/corrcoefslices.m:L226-L248
    corry_sim_sort = sort(corry,2);
    corrlength = length(corry_rch);  % number of tested sed. rate
    corry_per = zeros(corrlength,1);
    %
    %assignin('base','corry_rch',corry_rch)
    %assignin('base','corry',corry)
    %
    for i = 1: corrlength
        corry_r1 = corry_rch(i);
        corry_sim_sort1 = corry_sim_sort(i,:);
        %corry_sim_sort2 = [];
        corry_sim_sort2 = corry_sim_sort1(corry_sim_sort1<corry_r1); % number of corr-value that is less than real data
        totallength = length(corry_sim_sort1(~isnan(corry_sim_sort1))); % number of not-null value
        %corry_per(i) = (totallength-length(corry_sim_sort2))/nsim;
        corry_per(i) = (totallength-length(corry_sim_sort2)+1)/(totallength+1); % Dec. 29, 2017 revised by M. Li
        if corry_per(i) == 0
            %corry_per(i) = 1/(nsim+1);
            corry_per(i) = 1/(totallength+1);
        end
    end
    %% confidence interval estimation for correlation coefficient
    
    corr_h0 = corry_per;  % percentile of the value
%% End copied source
%% Copied from mingsongli/acycle@dcba4279168745b563e0535b954297023dd62fc7 code/corrcoef/corrcoefslices.m:L280-L283
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

%% Copied from mingsongli/acycle@dcba4279168745b563e0535b954297023dd62fc7 code/corrcoef/corrcoefslices.m:L286-L302
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
        datanew(:,(2*i-1):(2*i)) = data_int;
    end
%% End copied source
end
