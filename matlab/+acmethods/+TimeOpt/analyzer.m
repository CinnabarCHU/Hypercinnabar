function [retval, id] = analyzer(params, id)
% TimeOpt.analyzer parameters: dat sedmin sedmax numsed nsim linLog fit fl fh roll targetE targetP detrend cormethod mc_scope (when nsim > 1).
% Source: https://github.com/mingsongli/acycle/blob/b52ea9f510f3be00bde9a0238b9898a1e2315b74/code/guicode/timeOptGUI.m#L380
if nargin < 2, id = []; end
[retval, id] = aclog.invoke('TimeOpt-v1.0/analyzer', params, id, @execute);
end

function [r, status] = execute(p)
dat = p.dat;
sedmin = p.sedmin;
sedmax = p.sedmax;
numsed = p.numsed;
nsim = p.nsim;
linLog = p.linLog;
fit = p.fit;
fl = p.fl;
fh = p.fh;
roll = p.roll;
targetE = p.targetE;
targetP = p.targetP;
detrend = p.detrend;
cormethod = p.cormethod;
cleanup = accompat.tanerWorkspace();
genplot = 0;
requested = nsim;
nsim = 0;
%% Copied from mingsongli/acycle@b52ea9f510f3be00bde9a0238b9898a1e2315b74 code/guicode/timeOptGUI.m:L380-L382
[xx,datopt,xcl,sr_p]=...
    timeOptAc(dat,sedmin,sedmax,numsed,nsim,linLog,fit,fl,fh,roll,...
    targetE,targetP,detrend,cormethod,genplot);
%% End copied source
nsim = requested;
xsim = [];
status = 'done';
if nsim > 1
    sedrate = xx(:,1);
%% Copied from mingsongli/acycle@f4027a865e22cf64500e7145aef592b944df3f98 code/package/timeOpt/timeOptAc.m:L131-L133
datx = dat(:,1);  % unit should be cm
daty = dat(:,2);
diffx = diff(datx);
%% End copied source
%% Copied from mingsongli/acycle@f4027a865e22cf64500e7145aef592b944df3f98 code/package/timeOpt/timeOptAc.m:L137-L137
fc=(fh+fl)/2;
%% End copied source
%% Copied from mingsongli/acycle@f4027a865e22cf64500e7145aef592b944df3f98 code/package/timeOpt/timeOptAc.m:L145-L148
if sum(diffx <= 0) > 0
    disp('>>  Waning: data has to be in ascending order, no duplicated number allowed')
    dat = sortrows(dat);
end
%% End copied source
%% Copied from mingsongli/acycle@f4027a865e22cf64500e7145aef592b944df3f98 code/package/timeOpt/timeOptAc.m:L180-L184
if detrend == 1
    sdat = polyfit(datx,daty,1);
    datalinear = datx * sdat(1) + sdat(2);
    dat(:,2) = dat(:,2) - datalinear;
end
%% End copied source
%% Copied from mingsongli/acycle@f4027a865e22cf64500e7145aef592b944df3f98 code/package/timeOpt/timeOptAc.m:L212-L229
r2env = xx(:,2);
maxr2env = max(r2env);
locj = find(r2env == maxr2env);
if length(locj) > 1
    disp('>>  WARNING: Multiple envelope maxima detected.')
end
r2pwr = xx(:,3);
maxr2pwr = max(r2pwr);
locm = find(r2pwr == maxr2pwr);
if length(locm) > 1
    disp('>>  WARNING: Multiple spectral power maxima detected.')
end
r2opt = xx(:,4);
maxr2opt = max(r2opt);
loci = find(r2opt == maxr2opt);
if length(loci) > 1
    disp('>>  WARNING: Multiple (spectral power*envelope) maxima detected.')
end
%% End copied source
    switch p.mc_scope
        case 'all'
%% Copied from mingsongli/acycle@f4027a865e22cf64500e7145aef592b944df3f98 code/package/timeOpt/timeOptAc.m:L407-L407
        xcl  = ones(numsed,4);
%% End copied source
%% Copied from mingsongli/acycle@f4027a865e22cf64500e7145aef592b944df3f98 code/package/timeOpt/timeOptAc.m:L418-L437
        defaultcl = 1/(nsim+1);
        for i = 1:numsed
            sedrate1 = sedrate(i);
            xsim = timeOptSimAc(dat,sedrate1,nsim,fit,cormethod,targetE,targetP,fc,fl,fh,roll);
            xcl(i,1) = sedrate1;
            xs1 = xsim(:,1);
            xcl(i,2) = length(xs1(xs1>r2env(i)))/nsim;
            if xcl(i,2) == 0
                xcl(i,2) = defaultcl;
            end
            xs2 = xsim(:,2);
            xcl(i,3) = length(xs2(xs2>r2pwr(i)))/nsim;
            if xcl(i,3) == 0
                xcl(i,3) = defaultcl;
            end
            xs3 = xsim(:,3);
            xcl(i,4) = length(xs3(xs3>r2opt(i)))/nsim;
            if xcl(i,4) == 0
                xcl(i,4) = defaultcl;
            end
%% End copied source
%% Copied from mingsongli/acycle@f4027a865e22cf64500e7145aef592b944df3f98 code/package/timeOpt/timeOptAc.m:L446-L452
            disp(' ')
            disp(['>>  At sedimentation rate of ', num2str(sedrate1)])
            disp(['>>    Envelope r^2 p-value = ',num2str(xcl(i,2),'%.5f')])    
            disp(['>>    Power    r^2 p-value = ',num2str(xcl(i,3),'%.5f')])
            disp(['>>    Optimal  r^2 p-value = ',num2str(xcl(i,4),'%.5f')])
            
        end
%% End copied source
            xsim = [];
        case 'optimum'
%% Copied from mingsongli/acycle@f4027a865e22cf64500e7145aef592b944df3f98 code/package/timeOpt/timeOptAc.m:L511-L511
        xcl  = ones(1,4);
%% End copied source
%% Copied from mingsongli/acycle@f4027a865e22cf64500e7145aef592b944df3f98 code/package/timeOpt/timeOptAc.m:L513-L513
        xsim = timeOptSimAc(dat,sedrate(loci(1)),nsim,fit,cormethod,targetE,targetP,fc,fl,fh,roll);
%% End copied source
%% Copied from mingsongli/acycle@f4027a865e22cf64500e7145aef592b944df3f98 code/package/timeOpt/timeOptAc.m:L519-L530
        xcl(1) = sedrate(loci(1));
        xs1 = xsim(:,1);
        xcl(2) = length(xs1(xs1>r2env(loci(1))))/nsim;
        xs2 = xsim(:,2);
        xcl(3) = length(xs2(xs2>r2pwr(loci(1))))/nsim;
        xs3 = xsim(:,3);
        xcl(4) = length(xs3(xs3>r2opt(loci(1))))/nsim;
        %
        disp(['>>  At sedimentation rate of ', num2str(sedrate(loci(1)),'%.3f')])
        disp(['>>       Envelope r^2 p-value = ',num2str(xcl(2),'%.5f')])    
        disp(['>>       Power    r^2 p-value = ',num2str(xcl(3),'%.5f')])
        disp(['>>       Optimal  r^2 p-value = ',num2str(xcl(4),'%.5f')])
%% End copied source
        case 'cancel'
            status = 'incomplete'; % The observed time scale and fits are already available.
        otherwise
            error('Acycle:TimeOpt:Scope','Unknown Monte Carlo scope %s.',p.mc_scope);
    end
end
r = struct();
r.xx = xx;
r.datopt = datopt;
r.xcl = xcl;
r.sr_p = sr_p;
r.xsim = xsim;
end
