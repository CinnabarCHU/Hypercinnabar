function [retval, id] = helper(params, id)
% DynamicFiltering.helper parameters: data.
% Source: https://github.com/mingsongli/acycle/blob/b52ea9f510f3be00bde9a0238b9898a1e2315b74/code/guicode/DynamicFilter.m#L92
if nargin < 2, id = []; end
[retval, id] = aclog.invoke('DynamicFiltering-v1.0/helper', params, id, @execute);
end

function r = execute(p)
data_s=p.data;
%% Copied from mingsongli/acycle@b52ea9f510f3be00bde9a0238b9898a1e2315b74 code/guicode/DynamicFilter.m:L94-L94
data_s(:,2) = data_s(:,2) - mean(data_s(:,2));
%% End copied source
%% Copied from mingsongli/acycle@b52ea9f510f3be00bde9a0238b9898a1e2315b74 code/guicode/DynamicFilter.m:L167-L184
xmin = min(data_s(:,1));
xmax = max(data_s(:,1));
mean1 = median(diff(data_s(:,1)));
handles.mean = mean1;
handles.step = 4*mean1;
handles.nyquist = 1/(2*handles.mean);     % prepare nyquist
handles.window = 0.2*(xmax-xmin);

handles.normal = 1;
handles.lenthx = xmax-xmin;
handles.time_0pad = 1;
handles.padtype = 1;
% if number of calculations is larger than 500;
% then, a large step is recommended. This way, the ncal is ~500.
ncal = (xmax-xmin - handles.window)/mean1;
if ncal > 500
    handles.step = abs(xmax - xmin - handles.window)/500;
end
%% End copied source
r=struct('data',data_s,'window',handles.window,'step',handles.step,'norm',handles.normal, ...
    'fmin',0,'fmax',handles.nyquist,'padding',handles.padtype);
end
