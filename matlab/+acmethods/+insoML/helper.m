function [retval, id] = helper(params, id)
% insoML.helper parameters: t day lat qinso author res L.
% Source: https://github.com/mingsongli/acycle/blob/b52ea9f510f3be00bde9a0238b9898a1e2315b74/code/misc/insoML.m#L50
if nargin < 2, id = []; end
[retval, id] = aclog.invoke('insoML-v1.0/helper', params, id, @execute);
end

function r = execute(p)
r = aclog.defaults(p, {'t', 'day', 'lat', 'qinso', 'author', 'res', 'L'}, 2, @legacyDefaults);
end

function values = legacyDefaults(t, day, lat, qinso, author, res, L)
%% Copied from mingsongli/acycle@b52ea9f510f3be00bde9a0238b9898a1e2315b74 code/misc/insoML.m:L50-L54
if nargin<7, L = 1365; end;
if nargin<6, res=1;    end;
if nargin<5, author=2; end;
if nargin<4, qinso=-2; end;
if nargin<3, lat=65;   end;
%% End copied source
values = struct();
if exist('t', 'var'), values.t = t; end
if exist('day', 'var'), values.day = day; end
if exist('lat', 'var'), values.lat = lat; end
if exist('qinso', 'var'), values.qinso = qinso; end
if exist('author', 'var'), values.author = author; end
if exist('res', 'var'), values.res = res; end
if exist('L', 'var'), values.L = L; end
end
