function [retval, id] = helper(params, id)
% Bandpass.helper parameters: data.
% Source: https://github.com/mingsongli/acycle/blob/b52ea9f510f3be00bde9a0238b9898a1e2315b74/code/guicode/ft.m#L128
if nargin < 2, id = []; end
[retval, id] = aclog.invoke('Bandpass-v1.0/helper', params, id, @execute);
end

function r = execute(p)
data = p.data;
data_s = data;
%% Copied from mingsongli/acycle@b52ea9f510f3be00bde9a0238b9898a1e2315b74 code/guicode/ft.m:L128-L129
data_s = sortrows(data_s);
data_s(:,2) = data_s(:,2) - mean(data_s(:,2));
%% End copied source
%% Copied from mingsongli/acycle@b52ea9f510f3be00bde9a0238b9898a1e2315b74 code/guicode/ft.m:L141-L157
handles.step = data_s(2,1)-data_s(1,1);
datax = data_s(:,1);
[po2,w2] = pmtm(data_s(:,2),2,5*length(datax));
fd2 = w2/(2*pi*handles.step);
L = length(data_s(:,2));
dt = mean(diff(data_s(:,1)));
Y = fft(data_s(:,2),L);
P2 = abs(Y/L);
P1 = P2(1:floor(L/2)+1);
P1(2:end-1) = 2*P1(2:end-1);
f = 1/dt * (0:(L/2))/L;

handles.x_1 = 0;
handles.x_2 = 0.5*max(f);
handles.y_1 = 0;
handles.y_2 = max(P1);
handles.y_3 = max(po2);
%% End copied source
%% Copied from mingsongli/acycle@b52ea9f510f3be00bde9a0238b9898a1e2315b74 code/guicode/ft.m:L179-L185
fd1index = find(P1 == max(P1), 1, 'first');
fq_deft = f(fd1index);   % find f with max power
handles.fd1index = fd1index;
handles.filt_fmid = fq_deft;
handles.filt_flow = fq_deft * 0.8; % 40%
handles.filt_fhigh = fq_deft * 1.2; % 40%
handles.taner_c = 10^12;
%% End copied source
%% Copied from mingsongli/acycle@b52ea9f510f3be00bde9a0238b9898a1e2315b74 code/guicode/ft.m:L189-L189
handles.filter = 'Gaussian';
%% End copied source
r = struct();
r.P1 = P1;
r.f = f;
r.po2 = po2;
r.fd2 = fd2;
r.data = data_s;
r.filter = handles.filter;
r.flow = str2double(num2str(handles.filt_flow));
r.fhigh = str2double(num2str(handles.filt_fhigh));
r.taner_c = handles.taner_c;
r.x_1 = handles.x_1; r.x_2 = handles.x_2;
r.y_1 = handles.y_1; r.y_2 = handles.y_2; r.y_3 = handles.y_3;
end
