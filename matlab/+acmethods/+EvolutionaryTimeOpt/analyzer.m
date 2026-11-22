function [retval, id] = analyzer(params, id)
% EvolutionaryTimeOpt.analyzer parameters: dat window step sedmin sedmax numsed linLog fit fl fh roll targetE targetP normal detrend cormethod time_0pad padtype.
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
cleanup = accompat.tanerWorkspace();
if p.time_0pad
    dat = zeropad2(dat,window,p.padtype);
end
data = dat;
nsim = 0; % GUIDE always disabled Monte Carlo inside a sliding window.
%% Copied from mingsongli/acycle@f4027a865e22cf64500e7145aef592b944df3f98 code/package/timeOpt/eTimeOpt.m:L24-L68
senv=[];
spow=[];
sopt=[];

x = data(:,1);
y = data(:,2);
dt = median(diff(x)); % sample rates

if step < dt; 
    step = dt;
end

npts = length(x);      % number of rows of data
if window >= abs(x(end)-x(1))
    error('Error in eTimeOpt. Window must be smaller than the x range')
end
n_win = floor(window/dt);  % number of data within 1 window
n_step = floor(step/dt); % number of data for 1 step
npts_new1 = npts - n_win +1; % size of y_grid if step = 1
npts_new = ceil(npts_new1/n_step); % size of y_grid
% 
sr_p_data = zeros(npts_new,6);

if mod(n_win,2)==0
    nstart = (n_win/2);
else
    nstart = (n_win+1)/2; % first data in y_grid
end

z = zeros(npts_new,n_win);
y_grid = zeros(npts_new,1);

% read data y for each window and detrend before saving data in z
j=1;
for i = 1: n_step : npts
    k = i + n_win - 1; %
    z(j,:) = y(i:k);
    y_grid(j,:) = x(nstart+i-1);
    j = j+1;
    if j > npts_new
        break
    end
end

depth_w = (0: dt : (n_win-1) * dt)';
%% End copied source
%% Copied from mingsongli/acycle@f4027a865e22cf64500e7145aef592b944df3f98 code/package/timeOpt/eTimeOpt.m:L81-L81
for i =1 : npts_new
%% End copied source
%% Copied from mingsongli/acycle@f4027a865e22cf64500e7145aef592b944df3f98 code/package/timeOpt/eTimeOpt.m:L89-L98
    d = z(i,:);
    dat = [depth_w,d'];
    disp(' ')
    disp(['--> Sliding window ',num2str(i),' of ',num2str(npts_new),'. Window center = ',num2str(y_grid(i)/100)])
    [xx,~,~,sr_p] =timeOptAc(dat,sedmin,sedmax,numsed,nsim,linLog,fit,fl,fh,roll,targetE,targetP,detrend,cormethod,0);
    senv(i,:) = xx(:,2)';
    spow(i,:) = xx(:,3)';
    sopt(i,:) = xx(:,4)';
    sr_p_data(i,:) = sr_p;
end
%% End copied source
%% Copied from mingsongli/acycle@f4027a865e22cf64500e7145aef592b944df3f98 code/package/timeOpt/eTimeOpt.m:L104-L117
if normal == 1
    maxsenv = max(senv,[],2);
    maxspow = max(spow,[],2);
    maxsopt = max(sopt,[],2);
    for i = 1: npts_new
        senv(i,:) = senv(i,:)/maxsenv(i);
        spow(i,:) = spow(i,:)/maxspow(i);
        sopt(i,:) = sopt(i,:)/maxsopt(i);
    end
end
x_grid = xx(:,1)';

[srow, ~] = size(senv);
y_grid = linspace((x(1)+window/2), (x(end)-window/2), srow); %debug
%% End copied source
sr_p=sr_p_data;
r = struct();
r.senv = senv;
r.spow = spow;
r.sopt = sopt;
r.x_grid = x_grid;
r.y_grid = y_grid;
r.sr_p = sr_p;
end
