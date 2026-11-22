function [retval, id] = analyzer(params, id)
% TimeOpt.analyzer parameters: dat sedmin sedmax numsed nsim linLog fit fl fh roll targetE targetP detrend cormethod.
% Source: https://github.com/mingsongli/acycle/blob/b52ea9f510f3be00bde9a0238b9898a1e2315b74/code/guicode/timeOptGUI.m#L380
if nargin < 2, id = []; end
[retval, id] = aclog.invoke('TimeOpt-v1.0/analyzer', params, id, @execute);
end

function r = execute(p)
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
genplot=0;
%% Copied from mingsongli/acycle@b52ea9f510f3be00bde9a0238b9898a1e2315b74 code/guicode/timeOptGUI.m:L380-L382
[xx,datopt,xcl,sr_p]=...
    timeOptAc(dat,sedmin,sedmax,numsed,nsim,linLog,fit,fl,fh,roll,...
    targetE,targetP,detrend,cormethod,genplot);
%% End copied source
r = struct();
r.xx = xx;
r.datopt = datopt;
r.xcl = xcl;
r.sr_p = sr_p;
end
