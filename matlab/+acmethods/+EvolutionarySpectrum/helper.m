function [retval, id] = helper(params, id)
% EvolutionarySpectrum.helper parameters: data.
% Source: https://github.com/mingsongli/acycle/blob/b52ea9f510f3be00bde9a0238b9898a1e2315b74/code/guicode/evofftGUI.m#L216
if nargin < 2, id = []; end
[retval, id] = aclog.invoke('EvolutionarySpectrum-v1.0/helper', params, id, @execute);
end

function r = execute(p)
data_s=p.data;
%% Copied from mingsongli/acycle@b52ea9f510f3be00bde9a0238b9898a1e2315b74 code/guicode/evofftGUI.m:L216-L216
handles.normal = 1;
%% End copied source
%% Copied from mingsongli/acycle@b52ea9f510f3be00bde9a0238b9898a1e2315b74 code/guicode/evofftGUI.m:L220-L227

xmin = min(data_s(:,1));
xmax = max(data_s(:,1));
mean1 = median(diff(data_s(:,1)));
handles.mean = mean1;
handles.step = handles.mean;
handles.nyquist = 1/(2*handles.mean);     % prepare nyquist
handles.window = 0.2*(xmax-xmin);
%% End copied source
%% Copied from mingsongli/acycle@b52ea9f510f3be00bde9a0238b9898a1e2315b74 code/guicode/evofftGUI.m:L231-L232
handles.time_0pad = 1;
handles.padtype = 1;
%% End copied source
%% Copied from mingsongli/acycle@b52ea9f510f3be00bde9a0238b9898a1e2315b74 code/guicode/evofftGUI.m:L235-L238
ncal = (xmax-xmin - handles.window)/mean1;
if ncal > 500
    handles.step = abs(xmax - xmin - handles.window)/500;
end
%% End copied source
%% Copied from mingsongli/acycle@b52ea9f510f3be00bde9a0238b9898a1e2315b74 code/guicode/evofftGUI.m:L229-L229
handles.method = 'Fast Fourier transform (LAH)';
%% End copied source
%% Copied from mingsongli/acycle@b52ea9f510f3be00bde9a0238b9898a1e2315b74 code/guicode/evofftGUI.m:L263-L264
diffx = diff(data_s(:,1));
if max(diffx) - min(diffx) > 10*eps('single')
%% End copied source
%% Copied from mingsongli/acycle@b52ea9f510f3be00bde9a0238b9898a1e2315b74 code/guicode/evofftGUI.m:L272-L273
    interpolate_rate = mean(diffx);
    handles.current_data = interpolate(data_s,interpolate_rate);
%% End copied source
else
    handles.current_data=data_s;
end
r=struct('data',handles.current_data,'window',handles.window,'step',handles.step,'fmin',0, ...
    'nyquist',handles.nyquist,'norm',handles.normal,'time_0pad',handles.time_0pad, ...
    'padtype',handles.padtype,'method',handles.method);
end
