function [retval, id] = analyzer(params, id)
% EvolutionaryTimeOpt.analyzer parameters: dat window step sedmin sedmax numsed linLog fit fl fh roll targetE targetP normal detrend cormethod.
% Source: https://github.com/mingsongli/acycle/blob/b52ea9f510f3be00bde9a0238b9898a1e2315b74/code/guicode/eTimeOptGUI.m#L446
if nargin < 2, id = []; end
[retval, id] = aclog.invoke('EvolutionaryTimeOpt-v1.0/analyzer', params, id, @execute);
end

function r = execute(p)
dat = p.dat;
window = p.window;
step = p.step;
sedmin = p.sedmin;
sedmax = p.sedmax;
numsed = p.numsed;
linLog = p.linLog;
fit = p.fit;
fl = p.fl;
fh = p.fh;
roll = p.roll;
targetE = p.targetE;
targetP = p.targetP;
normal = p.normal;
detrend = p.detrend;
cormethod = p.cormethod;
%% Copied from mingsongli/acycle@b52ea9f510f3be00bde9a0238b9898a1e2315b74 code/guicode/eTimeOptGUI.m:L446-L448
[senv,spow,sopt,x_grid,y_grid,sr_p] = ...
    eTimeOpt(dat,window,step,sedmin,sedmax,numsed,0,linLog,fit,fl,fh,roll,...
    targetE,targetP,normal,detrend,cormethod,0);
%% End copied source
r = struct();
r.senv = senv;
r.spow = spow;
r.sopt = sopt;
r.x_grid = x_grid;
r.y_grid = y_grid;
r.sr_p = sr_p;
end
