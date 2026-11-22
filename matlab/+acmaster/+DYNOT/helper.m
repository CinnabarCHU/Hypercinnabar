function [retval,id] = helper(params,id)
% DYNOT.helper parameters: data.
% Source: https://github.com/mingsongli/acycle/blob/dcba4279168745b563e0535b954297023dd62fc7/code/guicode/DYNOS.m
if nargin < 2, id = []; end
[retval,id] = accompat.masterInvoke('DYNOT-v3.1.1+dcba427/helper',params,id,@execute);
end

function r = execute(p)
S = struct();
%% Copied from mingsongli/acycle@dcba4279168745b563e0535b954297023dd62fc7 code/guicode/DYNOS.m:L34-L53
S.use_middle_age = true;
S.age = 0;
S.orbit9 = defaultOrbit9();
S.cycles = S.orbit9;
S.f = 1./S.cycles;

S.window1 = 300;
S.window2 = 500;
S.nw1 = 2;
S.nw2 = 2;
S.pad = 1000;
S.step = 5;
S.nout = 1000;
S.shiftwin = 1;
S.padwin = 1;
S.fza = 0.9;
S.fzb = 1.2;
S.ftmin = 0.001;
S.ftmax = 1;
S.nmc = 1000;
%% End copied source
%% Copied from mingsongli/acycle@dcba4279168745b563e0535b954297023dd62fc7 code/guicode/DYNOS.m:L57-L57
S.percent_on = [true true true true true true];
%% End copied source
data = sanitizeData(p.data);
if size(data,1)<10, error('Acycle:DYNOT:Rows','At least ten usable rows are required.'); end
%% Copied from mingsongli/acycle@dcba4279168745b563e0535b954297023dd62fc7 code/guicode/DYNOS.m:L337-L337
    S.data = data;
%% End copied source
%% Copied from mingsongli/acycle@dcba4279168745b563e0535b954297023dd62fc7 code/guicode/DYNOS.m:L340-L350
    if data(2,1) <= data(1,1)
        data = flipud(data);
    end
    samplerate = diff(data(:,1));
    S.parmhat = wblfit(samplerate);
    samplerange = prctile(samplerate,[5 95]);

    S.sampa = samplerange(1);
    S.sampb = samplerange(2);
    S.cut1 = data(1,1);
    S.cut2 = data(end,1);
%% End copied source
r = S;
end

%% Copied from mingsongli/acycle@dcba4279168745b563e0535b954297023dd62fc7 code/guicode/DYNOS.m:L522-L524
function cycles = defaultOrbit9()
cycles = [405.6912, 130.6979, 123.8532, 98.8517, 94.8856, 40.9897, 23.6820, 22.3758, 18.9519];
end
%% End copied source

%% Copied from mingsongli/acycle@dcba4279168745b563e0535b954297023dd62fc7 code/guicode/DYNOS.m:L870-L882
function data = sanitizeData(data)
if size(data,2) > 2
    data = data(:,1:2);
end
data = sortrows(data,1);
if exist('findduplicate','file') == 2
    data = findduplicate(data);
else
    [~,ia] = unique(data(:,1),'stable');
    data = data(ia,:);
end
data(any(~isfinite(data),2),:) = [];
end
%% End copied source
