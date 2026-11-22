function [retval, id] = helper(params, id)
% TimeOpt.helper parameters: dat (depth in cm).
% Source: https://github.com/mingsongli/acycle/blob/b52ea9f510f3be00bde9a0238b9898a1e2315b74/code/guicode/timeOptGUI.m#L279
if nargin < 2, id = []; end
[retval, id] = aclog.invoke('TimeOpt-v1.0/helper', params, id, @execute);
end

function r = execute(p)
dat = p.dat;
npts=size(dat,1);
%% Copied from mingsongli/acycle@b52ea9f510f3be00bde9a0238b9898a1e2315b74 code/guicode/timeOptGUI.m:L279-L292
handles.sedmin = 0;
handles.sedmax = 100;
handles.numsed = 200;
handles.fl = 0.035;
handles.fh = 0.065;
handles.targetE = [405.6795,130.719,123.839,98.86307,94.87666];
handles.targetP = [23.62069,22.31868,19.06768,18.91979];

dt = median(diff(dat(:,1)));
fnyq = handles.sedmin/(2*dt);
if handles.fh > fnyq
    sedmin = 2 * dt * handles.fh;
    handles.sedmin = sedmin;
end
%% End copied source
%% Copied from mingsongli/acycle@b52ea9f510f3be00bde9a0238b9898a1e2315b74 code/guicode/timeOptGUI.m:L295-L300
fray = handles.sedmax/(npts * dt);
flow = 1/max(handles.targetE);
if fray > flow
    sedmax = npts * dt * flow;
    handles.sedmax = sedmax;
end
%% End copied source
%% Copied from mingsongli/acycle@b52ea9f510f3be00bde9a0238b9898a1e2315b74 code/guicode/timeOptGUI.m:L310-L315
handles.nsim = 0;
handles.linLog = 2;
handles.fit = 1;
handles.roll = 10^12;
handles.detrend = 1;
handles.cormethod = 2;
%% End copied source
r=handles; r.dat=dat;
end
