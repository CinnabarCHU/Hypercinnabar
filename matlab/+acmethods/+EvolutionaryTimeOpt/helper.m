function [retval, id] = helper(params, id)
% EvolutionaryTimeOpt.helper parameters: dat (depth in cm).
% Source: https://github.com/mingsongli/acycle/blob/b52ea9f510f3be00bde9a0238b9898a1e2315b74/code/guicode/eTimeOptGUI.m#L228
if nargin < 2, id = []; end
[retval, id] = aclog.invoke('EvolutionaryTimeOpt-v1.0/helper', params, id, @execute);
end

function r = execute(p)
dat=p.dat;
if any(diff(dat(:,1))<=0), dat=sortrows(dat); end
%% Copied from mingsongli/acycle@b52ea9f510f3be00bde9a0238b9898a1e2315b74 code/guicode/eTimeOptGUI.m:L239-L246
datx = dat(:,1);  % unit should be cm
daty = dat(:,2);
npts = length(datx);
dt = median(diff(dat(:,1)));
dtr = dt;
%
handles.window = 0.35 * abs(datx(end) - datx(1));
handles.step = 0.65 * abs(datx(end)-datx(1))/200;
%% End copied source
%% Copied from mingsongli/acycle@b52ea9f510f3be00bde9a0238b9898a1e2315b74 code/guicode/eTimeOptGUI.m:L256-L258
if handles.step <= dt
    handles.step = dt;
end
%% End copied source
%% Copied from mingsongli/acycle@b52ea9f510f3be00bde9a0238b9898a1e2315b74 code/guicode/eTimeOptGUI.m:L319-L333
handles.dat = dat; % save data
% set default sedmin, sedmax
handles.sedmin = 0;
handles.sedmax = 100;
handles.numsed = 200;
handles.fl = 0.035;
handles.fh = 0.065;
handles.targetE = [405.6795,130.719,123.839,98.86307,94.87666];
handles.targetP = [23.62069,22.31868,19.06768,18.91979];

fnyq = handles.sedmin/(2*dtr);
if handles.fh > fnyq
    sedmin = 2 * dtr * handles.fh;
    handles.sedmin = sedmin;
end
%% End copied source
%% Copied from mingsongli/acycle@b52ea9f510f3be00bde9a0238b9898a1e2315b74 code/guicode/eTimeOptGUI.m:L336-L341
fray = handles.sedmax/(npts * dtr);
flow = 1/max(handles.targetE);
if fray > flow
    sedmax = npts * dtr * flow;
    handles.sedmax = sedmax;
end
%% End copied source
%% Copied from mingsongli/acycle@b52ea9f510f3be00bde9a0238b9898a1e2315b74 code/guicode/eTimeOptGUI.m:L352-L367
handles.npts = npts;
handles.dt = dt;
handles.dtr = dtr;
handles.nsim = 0;
handles.linLog = 2;
handles.fit = 1;
handles.roll = 10^12;
handles.detrend = 1;
handles.cormethod = 2;
handles.genplot = 1;
handles.flipy = 1;
handles.normal = 0;
handles.age = 0;
handles.plot_2d = 1;
handles.time_0pad = 1;  % updated acycle v1.2.1
handles.padtype = 1; % updated acycle v1.2.1
%% End copied source
r=handles;
r.unit='cm'; r.unit_type=1; r.main_unit_selection=0; r.lang_choice=0;
r.lang_var={}; r.lang_id={};
end
