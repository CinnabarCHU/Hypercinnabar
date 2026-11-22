function [retval, id] = analyzer(params, id)
% EvolutionarySpectrum.analyzer parameters: data window step fmin nyquist norm method time_0pad padtype.
% Source: https://github.com/mingsongli/acycle/blob/b52ea9f510f3be00bde9a0238b9898a1e2315b74/code/guicode/evofftGUI.m#L328
if nargin < 2, id = []; end
[retval, id] = aclog.invoke('EvolutionarySpectrum-v1.0/analyzer', params, id, @execute);
end

function r = execute(p)
data = p.data;
window = p.window;
step = p.step;
fmin = p.fmin;
nyquist = p.nyquist;
norm = p.norm;
method = p.method;
time_0pad = p.time_0pad;
padtype = p.padtype;
handles=struct('nyquist',nyquist,'time_0pad',time_0pad,'padtype',padtype);
%% Copied from mingsongli/acycle@b52ea9f510f3be00bde9a0238b9898a1e2315b74 code/guicode/evofftGUI.m:L328-L341
if handles.time_0pad == 1
    % restore time/depth
    data = zeropad2(data,window,handles.padtype);
else
    data(:,2) = data(:,2) - mean(data(:,2));
end
% Evofft Plot
if strcmp(method,'Periodogram')
    [s,x_grid,y_grid]=evoperiodogram(data,window,step,fmin,handles.nyquist,norm);
elseif strcmp(method,'Lomb-Scargle periodogram')
    [s,x_grid,y_grid]=evoplomb(data,window,step,fmin,handles.nyquist,norm);
elseif strcmp(method,'Multi-taper method')
    [s,x_grid,y_grid] = evopmtm(data,window,step,fmin,handles.nyquist,norm);
elseif strcmp(method,'Fast Fourier transform (MatLab)')
%% End copied source
%% Copied from mingsongli/acycle@b52ea9f510f3be00bde9a0238b9898a1e2315b74 code/guicode/evofftGUI.m:L343-L349
    [s,x_grid,y_grid]=evofftML(data,window,step,fmin,handles.nyquist,norm);
elseif strcmp(method,'Fast Fourier transform (LAH)')
    dt = data(2,1)-data(1,1);
    %[s,x_grid,y_grid]=evofftLAH(data,window,step,dt,fmin,fmax,norm);
    [s,x_grid,y_grid]=evofft(data,window,step,dt,fmin,handles.nyquist,norm);
end
fmingrid = x_grid(2) - x_grid(1);
%% End copied source
r = struct();
r.s = s;
r.x_grid = x_grid;
r.y_grid = y_grid;
r.fmingrid = fmingrid;
end
