function [retval, id] = helper(params, id)
% rmse4leadlag.helper parameters: target series ll step timedir plotn.
% Source: https://github.com/mingsongli/acycle/blob/b52ea9f510f3be00bde9a0238b9898a1e2315b74/code/seriesanalysis/rmse4leadlag.m#L32
if nargin < 2, id = []; end
[retval, id] = aclog.invoke('rmse4leadlag-v1.0/helper', params, id, @execute);
end

function r = execute(p)
dat1=p.target; dat2=p.series;
%% Copied from mingsongli/acycle@b52ea9f510f3be00bde9a0238b9898a1e2315b74 code/guicode/leadlagGUI.m:L194-L201
dat1 = sortrows(dat1);
dat2 = sortrows(dat2);
% unique
dat1=findduplicate(dat1);
dat2=findduplicate(dat2);
% remove empty
dat1(any(isinf(dat1),2),:) = [];
dat2(any(isinf(dat2),2),:) = [];
%% End copied source
%% Copied from mingsongli/acycle@b52ea9f510f3be00bde9a0238b9898a1e2315b74 code/guicode/leadlagGUI.m:L258-L263
xmax = nanmax(dat2(:,1));
xmin = nanmin(dat2(:,1));

ll = (xmax-xmin)/10;
%step = (xmax-xmin)/200;
step = mean(diff(dat2(:,1)),'omitnan')/2;
%% End copied source
p.target=dat1; p.series=dat2;
if ~isfield(p,'ll'), p.ll=str2double(num2str(ll)); end
if ~isfield(p,'step'), p.step=str2double(num2str(step)); end
r = aclog.defaults(p, {'target', 'series', 'll', 'step', 'timedir', 'plotn'}, 4, @legacyDefaults);
end

function values = legacyDefaults(target, series, ll, step, timedir, plotn)
%% Copied from mingsongli/acycle@b52ea9f510f3be00bde9a0238b9898a1e2315b74 code/seriesanalysis/rmse4leadlag.m:L32-L33
if nargin < 6; plotn = 1; end
if nargin < 5; timedir = 1; end
%% End copied source
values = struct();
if exist('target', 'var'), values.target = target; end
if exist('series', 'var'), values.series = series; end
if exist('ll', 'var'), values.ll = ll; end
if exist('step', 'var'), values.step = step; end
if exist('timedir', 'var'), values.timedir = timedir; end
if exist('plotn', 'var'), values.plotn = plotn; end
end
