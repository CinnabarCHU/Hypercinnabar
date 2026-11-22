function [retval, id] = analyzer(params, id)
% Insolation.analyzer parameters: t1 t2 dt unit_t type dayi1 dayi2 latrange lat1 lat2 dlat qinso author res L.
% Source: https://github.com/mingsongli/acycle/blob/b52ea9f510f3be00bde9a0238b9898a1e2315b74/code/guicode/Insolation.m#L313
if nargin < 2, id = []; end
[retval, id] = aclog.invoke('Insolation-v1.0/analyzer', params, id, @execute);
end

function r = execute(p)
t1 = p.t1;
t2 = p.t2;
dt = p.dt;
unit_t = p.unit_t;
type = p.type;
dayi1 = p.dayi1;
dayi2 = p.dayi2;
latrange = p.latrange;
lat1 = p.lat1;
lat2 = p.lat2;
dlat = p.dlat;
qinso = p.qinso;
author = p.author;
res = p.res;
L = p.L;
handles.latrange=latrange;
%% Copied from mingsongli/acycle@b52ea9f510f3be00bde9a0238b9898a1e2315b74 code/guicode/Insolation.m:L313-L337
t0 = max(t1,t2):-abs(dt):min(t1,t2);
t= t0;
unit_t_r = 'ka';
if unit_t == 2
    t = t0*1000;
    unit_t_r = 'Ma';
elseif unit_t == 3
    t = t0/1000;
    unit_t_r = 'yr';
end
if type == 1
    if dayi1 < dayi2
        day = dayi1 : dayi2;
    else
        dayi2 = dayi2+365;
        day = dayi1 : dayi2;
    end
else
    day = dayi1;
end
if handles.latrange == 1
    lat = min(lat1,lat2):abs(dlat):max(lat1,lat2);
else
    lat = lat1;
end
%% End copied source
%% Copied from mingsongli/acycle@b52ea9f510f3be00bde9a0238b9898a1e2315b74 code/guicode/Insolation.m:L347-L347
    [I, ~, xorb, yorb, veq, Insol_a_m, Ix,II]=insoML(t,day,lat,qinso,author,res, L);
%% End copied source
r = struct();
r.I = I;
r.t0 = t0;
r.t = t;
r.day = day;
r.lat = lat;
r.xorb = xorb;
r.yorb = yorb;
r.veq = veq;
r.Insol_a_m = Insol_a_m;
r.Ix = Ix;
r.II = II;
end
