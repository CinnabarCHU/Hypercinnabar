function [retval, id] = helper(params, id)
% DYNOT.helper parameters: data.
% Source: https://github.com/mingsongli/acycle/blob/b52ea9f510f3be00bde9a0238b9898a1e2315b74/code/guicode/DYNOS.m#L870
if nargin < 2, id = []; end
[retval, id] = aclog.invoke('DYNOT-v1.0/helper', params, id, @execute);
end

function r = execute(p)
data = p.data;
%% Copied from mingsongli/acycle@b52ea9f510f3be00bde9a0238b9898a1e2315b74 code/guicode/DYNOS.m:L870-L878
    if data(2,1)<= data(1,1)
        data = flipud(data);
    end
    xmin = min(data(:,1));
    xmax = max(data(:,1));
    ymin = min(data(:,2));
    ymax = max(data(:,2));
    samplerate = diff(data(:,1));
    parmhat = wblfit(samplerate); % estimate weibull a and b
%% End copied source
%% Copied from mingsongli/acycle@b52ea9f510f3be00bde9a0238b9898a1e2315b74 code/guicode/DYNOS.m:L888-L888
    samplerange = prctile(samplerate, [5 95]);
%% End copied source
%% Copied from mingsongli/acycle@b52ea9f510f3be00bde9a0238b9898a1e2315b74 code/guicode/DYNOS.m:L894-L911
    handles.sampa = samplerange(1);
    handles.sampb = samplerange(2);
    handles.parmhat = parmhat;
    handles.unit = 'ka';
    handles.window1 = 300;
    handles.window2 = 500;
    handles.nw1 = 2;
    handles.nw2 = 2;
    handles.pad = 1000;
    handles.step = 5;
    handles.nout = 1000;
    handles.shiftwin = 1;
    handles.padwin = 1;
    handles.fza = 0.9;
    handles.fzb = 1.2;
    handles.ftmin = 0.001;
    handles.ftmax = 1;
    handles.nmc = 1000;
%% End copied source
%% Copied from mingsongli/acycle@b52ea9f510f3be00bde9a0238b9898a1e2315b74 code/guicode/DYNOS.m:L915-L920
    handles.checkbox1median_v = 50;
    handles.checkbox50_v = [25 75];
    handles.checkbox68_v = [15.865 84.135];
    handles.checkbox80_v = [10 90];
    handles.checkbox90_v = [5 95];
    handles.checkbox95_v = [2.5 97.5];
%% End copied source
%% Copied from mingsongli/acycle@b52ea9f510f3be00bde9a0238b9898a1e2315b74 code/guicode/DYNOS.m:L927-L927
    c = [405 125 95 40.9 23.6 22.3 19.1];
%% End copied source
r=handles; r.data=data; r.f=1./c;
r.percent=sort([handles.checkbox1median_v,handles.checkbox50_v,handles.checkbox68_v, ...
    handles.checkbox80_v,handles.checkbox90_v,handles.checkbox95_v]);
end
