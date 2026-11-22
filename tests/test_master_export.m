function test_master_export()
folder = fullfile(getenv('RUNNER_TEMP'),'acycle-master-methods');
oldPath = path; oldDir = pwd;
guard = onCleanup(@() restore(oldPath,oldDir)); %#ok<NASGU>
cd(folder); restoredefaultpath; setup_method;
assert(isempty(which('acmethods.Bandpass.analyzer')));
p=acmaster.RegularInterpolation.helper(struct('data',[(0:7)',(0:7)'.^2],'samplingInterval',2));
[r,id]=acmaster.RegularInterpolation.analyzer(p);
assert(isequal(r.interpolated,[0 0;2 4;4 16;6 36]) && isequaln(r,aclog.replay(id)));
assert(isempty(which('acycleInterpolateSeries')));
checkDigitizer(folder);
end

function checkDigitizer(folder)
assert(isempty(which('acmethods.DigitizeTrace.analyzer')) && ~isfolder(fullfile(folder,'upstream','acycle')));
img = imread(fullfile(folder,'upstream','master','data','Examples','Example-PlotDigitizer.jpg'));
% Read the -200 and 1400 horizontal ticks and the 0 and 120 vertical ticks.
cal = struct('pixels',[91 1106; 595 1106; 91 1028; 91 94], ...
    'limits',[-200 1400 0 120],'logX',false,'logY',false);
p = acmaster.DigitizeTrace.helper(struct('image',img,'calibration',cal,'seeds',[164 164]));
assert(strcmp(p.mode,'Loose'));
[loose,id] = acmaster.DigitizeTrace.analyzer(p);
y = loose.pixels(:,2);
assert(strcmp(loose.reasons{1},'ok_v') && all(diff(y)==1));
assert(abs(y(1)-159)<=2 && abs(y(end)-1025)<=2);
seedRow = (y==164);
assert(nnz(seedRow)==1 && abs(loose.pixels(seedRow,1)-164)<=3);
assert(abs(loose.data(seedRow,2)-111)<0.3);
assert(contains(fileread(id),'DigitizeTrace-v3.1.1+dcba427/analyzer') && isequaln(loose,aclog.replay(id)));

visibility = get(groot,'defaultFigureVisible');
restoreVisibility = onCleanup(@() set(groot,'defaultFigureVisible',visibility)); %#ok<NASGU>
set(groot,'defaultFigureVisible','off');
acmaster.DigitizeTrace.plotter(struct('image',img,'result',loose));
fig = gcf;
closePlot = onCleanup(@() close(fig)); %#ok<NASGU>
markers = findobj(fig,'Type','line','Marker','+');
assert(isscalar(markers));
assert(isequal(markers.XData(:),loose.pixels(:,1)) && isequal(markers.YData(:),y));

p.mode = 'Strict';
strict = acmaster.DigitizeTrace.analyzer(p);
assert(size(strict.pixels,1)>=8 && size(strict.pixels,1)<size(loose.pixels,1));
% The right-hand marker at Time ~61 checks how closely the trace follows a sharp turn.
tipDistance = min(hypot(loose.pixels(:,1)-571,y-553));
fprintf('Digitizer example: Loose %d pixels, Strict %d pixels, nearest Loose trace to (571,553) %.1f pixels.\n', ...
    size(loose.pixels,1),size(strict.pixels,1),tipDistance);
end

function restore(oldPath,oldDir)
cd(oldDir); path(oldPath);
end
