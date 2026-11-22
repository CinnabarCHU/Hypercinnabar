function [retval, id] = analyzer(params, id)
% AstronomicalSolution.analyzer parameters: solution parameter t1 t2 wE/wT/wP(ETP).
% Source: https://github.com/mingsongli/acycle/blob/b52ea9f510f3be00bde9a0238b9898a1e2315b74/code/guicode/basicseries.m#L203
% Source: https://github.com/mingsongli/acycle/blob/b52ea9f510f3be00bde9a0238b9898a1e2315b74/code/guicode/basicseries.m#L427
if nargin < 2, id = []; end
[retval, id] = aclog.invoke('AstronomicalSolution-v1.0/analyzer', params, id, @execute);
end

function r = execute(p)
solution = p.solution;
parameter = p.parameter;
t1 = p.t1;
t2 = p.t2;
%% Copied from mingsongli/acycle@b52ea9f510f3be00bde9a0238b9898a1e2315b74 code/guicode/basicseries.m:L203-L263
if strcmp(solution,'')
    handles.basicseries = [];
    ref = 0;
elseif strcmp(solution,'La2004')
    basicseries = load('La04.mat');
    basicseries=basicseries.data;
    handles.basicseries = basicseries;
    ref = 1;
elseif strcmp(solution,'La2010a')
    basicseries = load('La10a.mat');
    handles.basicseries=basicseries.data;
    ref = 2;
elseif strcmp(solution,'La2010b')
    basicseries = load('La10b.mat');
    handles.basicseries=basicseries.data;
    ref = 2;
elseif strcmp(solution,'La2010c')
    basicseries = load('La10c.mat');
    handles.basicseries=basicseries.data;
    ref = 2;
elseif strcmp(solution,'La2010d')
    basicseries = load('La10d.mat');
    handles.basicseries=basicseries.data;
    ref = 2;
elseif strcmp(solution, 'ZB17a')
    handles.basicseries = load('ZB17a.dat');
    ref = 3;
elseif strcmp(solution, 'ZB17b')
    handles.basicseries = load('ZB17b.dat');
    ref = 3;
elseif strcmp(solution, 'ZB17c')
    handles.basicseries = load('ZB17c.dat');
    ref = 3;
elseif strcmp(solution, 'ZB17d')
    handles.basicseries = load('ZB17d.dat');
    ref = 3;
elseif strcmp(solution, 'ZB17e')
    handles.basicseries = load('ZB17e.dat');
    ref = 3;
elseif strcmp(solution, 'ZB17f')
    handles.basicseries = load('ZB17f.dat');
    ref = 3;
elseif strcmp(solution, 'ZB17h')
    handles.basicseries = load('ZB17h.dat');
    ref = 3;
elseif strcmp(solution, 'ZB17i')
    handles.basicseries = load('ZB17i.dat');
    ref = 3;
elseif strcmp(solution, 'ZB17j')
    handles.basicseries = load('ZB17j.dat');
    ref = 3;
elseif strcmp(solution, 'ZB17k')
    handles.basicseries = load('ZB17k.dat');
    ref = 3;
elseif strcmp(solution, 'ZB17p')
    handles.basicseries = load('ZB17p.dat');
    ref = 3;
elseif strcmp(solution, 'ZB18a')
    handles.basicseries = load('ZB18a.dat');
    ref = 4;
end
%% End copied source
if ref==0, error('Acycle:Astronomy:Solution','Select an orbital solution.'); end
bounds=sort([t1,t2]); t1=bounds(1); t2=bounds(2); dat=handles.basicseries;
%% Copied from mingsongli/acycle@b52ea9f510f3be00bde9a0238b9898a1e2315b74 code/guicode/basicseries.m:L406-L429
if t1 < 0
    error('Error: t1 must be no less than 0')
    return;
end
if t2 <= t1
    error('Error: t2 must be larger than t1')
    return;
end
if ref == 3 && t2 > 1.0e+05
    error('Error: t2 must be less than 100,000')
    return;
end
if ref == 4 && t2 > 1.0e+05
    error('Error: t2 must be less than 100,000')
    return;
end
if (ref == 1 || ref == 2) && t2 >= 249000
    error('Error: t2 must be less than 249,000')
    return;
end

data = select_interval(dat,t1,t2);
%data = dat(t1:t2,:);
clear dat
%% End copied source
switch parameter
case 'ETP'
    wE=p.wE; wT=p.wT; wP=p.wP;
%% Copied from mingsongli/acycle@b52ea9f510f3be00bde9a0238b9898a1e2315b74 code/guicode/basicseries.m:L435-L437
    data(:,5)=wE * zscore(data(:,2))+ wT * zscore(data(:,3)) + wP * zscore(data(:,4));
    dat(:,1)=data(:,1);
    dat(:,2)=data(:,5);
%% End copied source
case 'Eccentricity'
%% Copied from mingsongli/acycle@b52ea9f510f3be00bde9a0238b9898a1e2315b74 code/guicode/basicseries.m:L442-L442
    dat=[data(:,1),data(:,2)];
%% End copied source
case 'Obliquity'
%% Copied from mingsongli/acycle@b52ea9f510f3be00bde9a0238b9898a1e2315b74 code/guicode/basicseries.m:L444-L444
    dat=[data(:,1),data(:,3)];
%% End copied source
case 'Precession'
%% Copied from mingsongli/acycle@b52ea9f510f3be00bde9a0238b9898a1e2315b74 code/guicode/basicseries.m:L446-L446
    dat=[data(:,1),data(:,4)];
%% End copied source
case 'Inclination'
%% Copied from mingsongli/acycle@b52ea9f510f3be00bde9a0238b9898a1e2315b74 code/guicode/basicseries.m:L448-L448
    dat=[data(:,1),data(:,3)];
%% End copied source
otherwise
    error('Acycle:Astronomy:Parameter','Unknown orbital series.');
end
r = struct();
r.dat = dat;
r.solution = solution;
r.parameter = parameter;
r.t1 = t1;
r.t2 = t2;
end
