function [retval,id] = analyzer(params,id)
% DYNOT.analyzer parameters: data nmc nout nw1 nw2 parmhat sampa sampb window1 window2 f fza fzb ftmin ftmax padwin step pad percent_on.
% Source: https://github.com/mingsongli/acycle/blob/dcba4279168745b563e0535b954297023dd62fc7/code/guicode/DYNOS.m
% Source: https://github.com/mingsongli/acycle/blob/dcba4279168745b563e0535b954297023dd62fc7/code/guicode/dynotIterationWorker.m
% Source: https://github.com/mingsongli/acycle/blob/dcba4279168745b563e0535b954297023dd62fc7/code/guicode/dynotPercentilePlan.m
if nargin < 2, id = []; end
[retval,id] = accompat.masterInvoke('DYNOT-v3.1.1+dcba427/analyzer',params,id,@execute);
end

function r = execute(p)
S = p;
%% Copied from mingsongli/acycle@dcba4279168745b563e0535b954297023dd62fc7 code/guicode/DYNOS.m:L542-L574
data = S.data;
nmc = S.nmc;
nout = S.nout;

if S.nw2 == S.nw1
    randnw = zeros(nmc,1);
else
    randnw = randi(2*(S.nw2-S.nw1),[nmc 1]);
end
samplez = wblrnd(S.parmhat(1),S.parmhat(2),[nmc 1]);
% v2.8 used one shared replacement draw for every value below the lower
% bound and a second shared draw for every value above the upper bound.
% Keep both draws unconditional to preserve the historical random stream.
lowerReplacement = S.sampa + (S.sampb-S.sampa)*rand(1);
samplez(samplez<S.sampa) = lowerReplacement;
upperReplacement = S.sampa + (S.sampb-S.sampa)*rand(1);
samplez(samplez>S.sampb) = upperReplacement;
windowz = S.window1 + (S.window2-S.window1).*rand(nmc,1);
nwz = S.nw1 + randnw/2;
bw = nwz./windowz;

f3m = zeros(nmc,2*numel(S.f));
for i = 1:numel(S.f)
    fz = S.fza + (S.fzb-S.fza).*rand(nmc,1);
    f3m(:,2*i-1) = S.f(i) - fz.*bw;
    fz = S.fza + (S.fzb-S.fza).*rand(nmc,1);
    f3m(:,2*i) = S.f(i) + fz.*bw;
end
f3m(f3m<S.ftmin)=S.ftmin; f3m(f3m>S.ftmax)=S.ftmax;

y_grid = linspace(data(1,1),data(end,1),nout)';
powy = nan(nout,nmc);
powmean = nan(1,nmc);
%% End copied source
%% Copied from mingsongli/acycle@dcba4279168745b563e0535b954297023dd62fc7 code/guicode/DYNOS.m:L887-L888
options = struct('padwin',S.padwin,'ftmin',S.ftmin, ...
    'ftmax',S.ftmax,'step',S.step,'pad',S.pad);
%% End copied source
for index = 1:nmc
    yGrid = y_grid;
%% Copied from mingsongli/acycle@dcba4279168745b563e0535b954297023dd62fc7 code/guicode/DYNOS.m:L898-L899
    [powy(:,index),powmean(index)] = dynotIterationWorker(data,yGrid, ...
        samplez(index),windowz(index),nwz(index),f3m(index,:),options);
%% End copied source
end
%% Copied from mingsongli/acycle@dcba4279168745b563e0535b954297023dd62fc7 code/guicode/DYNOS.m:L586-L601
pm = mean(powmean,'omitnan');
adj = pm./powmean;
powyadjust = repmat(adj,nout,1).*powy;
maxp = max(powyadjust,[],'all','omitnan');
if isfinite(maxp) && maxp > 1
    powyadjust = powyadjust/maxp;
end

percentilePlan = dynotPercentilePlan(S.percent_on);
pp = percentilePlan.percentiles;
powyadjustp = prctile(powyadjust,pp,2);
mask = ~isnan(powyadjustp(:,1));
y_grid_nan = y_grid(mask);
powyad_p_nan = 1 - powyadjustp(mask,:);

colorcode = [221 234 224;201 227 209;176 219 188;126 201 146;67 180 100]/255;
%% End copied source
%% Copied from mingsongli/acycle@dcba4279168745b563e0535b954297023dd62fc7 code/guicode/DYNOS.m:L603-L604
npercent = numel(pp);
npercent2 = percentilePlan.intervalCount;
%% End copied source
%% Copied from mingsongli/acycle@dcba4279168745b563e0535b954297023dd62fc7 code/guicode/DYNOS.m:L610-L610
medianIndex = percentilePlan.medianIndex;
%% End copied source
%% Copied from mingsongli/acycle@dcba4279168745b563e0535b954297023dd62fc7 code/guicode/DYNOS.m:L628-L640
S.run.y_grid = y_grid;
S.run.powyadjust = 1-powyadjust;
S.run.y_grid_nan = y_grid_nan;
S.run.powyad_p_nan = powyad_p_nan;
S.run.npercent = npercent;
S.run.npercent2 = npercent2;
S.run.percentiles = pp;
S.run.medianIndex = medianIndex;
S.run.colorcode = colorcode;
S.run.f3m = f3m;
S.run.nwz = nwz;
S.run.windowz = windowz;
S.run.samplez = samplez;
%% End copied source
r = S.run;
end
