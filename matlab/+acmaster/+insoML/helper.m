function [retval,id] = helper(params,id)
% insoML.helper parameters: t day lat qinso author res L.
% Source: https://github.com/mingsongli/acycle/blob/dcba4279168745b563e0535b954297023dd62fc7/code/misc/insoML.m
if nargin < 2, id = []; end
[retval,id] = accompat.masterInvoke('insoML-v3.1.1+dcba427/helper',params,id,@execute);
end

function r = execute(p)
r = aclog.defaults(p, {'t', 'day', 'lat', 'qinso', 'author', 'res', 'L'}, 2, @legacyDefaults);
end

function values = legacyDefaults(t, day, lat, qinso, author, res, L)
%% Copied from mingsongli/acycle@dcba4279168745b563e0535b954297023dd62fc7 code/misc/insoML.m:L50-L54
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
