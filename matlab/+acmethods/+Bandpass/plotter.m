function [retval, id] = plotter(params, id)
% Bandpass.plotter parameters: result po2 fd2 x_1 x_2 y_1 y_2 y_3 unit.
% Source: https://github.com/mingsongli/acycle/blob/b52ea9f510f3be00bde9a0238b9898a1e2315b74/code/guicode/ft.m#L167
% Source: https://github.com/mingsongli/acycle/blob/b52ea9f510f3be00bde9a0238b9898a1e2315b74/code/misc/update_filter_axes.m#L79
if nargin < 2, id = []; end
[retval, id] = aclog.invoke('Bandpass-v1.0/plotter', params, id, @execute);
end

function r = execute(p)
result = p.result;
po2 = p.po2;
fd2 = p.fd2;
x_1 = p.x_1;
x_2 = p.x_2;
y_1 = p.y_1;
y_2 = p.y_2;
y_3 = p.y_3;
unit = p.unit;
handles = struct('x_1',x_1,'x_2',x_2,'y_1',y_1,'y_3',y_3,'unit',unit);
figure;
subplot(2,1,2);
%% Copied from mingsongli/acycle@b52ea9f510f3be00bde9a0238b9898a1e2315b74 code/guicode/ft.m:L168-L170
plot(fd2,po2);
xlim([handles.x_1 handles.x_2])
ylim([handles.y_1 handles.y_3])
%% End copied source
%% Copied from mingsongli/acycle@b52ea9f510f3be00bde9a0238b9898a1e2315b74 code/guicode/ft.m:L173-L173
    xlabel(['Frequency (cycles/' handles.unit,')'])
%% End copied source
subplot(2,1,1);
f = result.f; P1 = result.P1;
%% Copied from mingsongli/acycle@b52ea9f510f3be00bde9a0238b9898a1e2315b74 code/misc/update_filter_axes.m:L80-L81
    plot(f,P1)
    hold on
%% End copied source
if strcmp(result.filter,'Gaussian')
    filter1 = result.response; f1 = result.frequency;
%% Copied from mingsongli/acycle@b52ea9f510f3be00bde9a0238b9898a1e2315b74 code/misc/update_filter_axes.m:L82-L82
    plot(f1,max(P1)*filter1,'r-')
%% End copied source
elseif strcmp(result.filter,'Taner-Hilbert')
    tf = result.response;
%% Copied from mingsongli/acycle@b52ea9f510f3be00bde9a0238b9898a1e2315b74 code/misc/update_filter_axes.m:L103-L103
    plot(f,tf,'r-')
%% End copied source
end
%% Copied from mingsongli/acycle@b52ea9f510f3be00bde9a0238b9898a1e2315b74 code/misc/update_filter_axes.m:L83-L85
    xlim([x_1, x_2])
    ylim([y_1, y_2])
    hold off
%% End copied source
r = [];
end
