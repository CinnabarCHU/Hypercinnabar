function test_package_portability()
% Exercise a copied method and the logger with neither the monolithic GUI nor the full repository on path.
root=fileparts(fileparts(mfilename('fullpath')));
scratch=tempname; mkdir(scratch);
oldPath=path; oldFolder=pwd; oldLog=getenv('ACYCLE_LOG_DIR');
guard=onCleanup(@() restoreEnvironment(oldPath,oldFolder,oldLog,scratch));
stage=fullfile(scratch,'matlab'); mkdir(stage); mkdir(fullfile(stage,'+acmethods'));
copyfile(fullfile(root,'matlab','+aclog'),fullfile(stage,'+aclog'));
copyfile(fullfile(root,'matlab','logger.m'),stage);
setenv('ACYCLE_LOG_DIR',fullfile(scratch,'journal'));
series=fullfile(root,'upstream','acycle','code','seriesanalysis');
matlabRuntime=~exist('OCTAVE_VERSION','builtin');
if matlabRuntime
    method='Bandpass';
    copyfile(fullfile(series,'gaussfilter.m'),stage);
else
    method='Derivative';
end
copyfile(fullfile(root,'matlab','+acmethods',['+',method]),fullfile(stage,'+acmethods',['+',method]));
cd(scratch); restoredefaultpath; addpath(stage); rehash;
assert(isempty(which('AC')) && isempty(which('acmethods.CircularSpectrum.analyzer')));
assert(startsWith(which(['acmethods.',method,'.analyzer']),stage));
t=(0:255)'; data=[t,sin(t*2*pi/20)+.2*cos(t*2*pi/5)];
if matlabRuntime
    p=acmethods.Bandpass.helper(struct('data',data)); [r,callId]=acmethods.Bandpass.analyzer(p);
    [g,~,~]=gaussfilter(p.data(:,2),1,(p.flow+p.fhigh)/2,p.flow,p.fhigh);
    assert(isequaln(r.data_filterout,[t,g,abs(hilbert(g))]));
    assert(isequaln(r,aclog.replay(callId)));
    p.unit='m'; p.result=r;
    before=findall(groot,'Type','figure');
    graphicsGuard=onCleanup(@() close(setdiff(findall(groot,'Type','figure'),before)));
    acmethods.Bandpass.plotter(p);
    assert(numel(findall(groot,'Type','figure'))==numel(before)+1);
else
    p=acmethods.Derivative.helper(struct('data',data)); [r,callId]=acmethods.Derivative.analyzer(p);
    assert(isequaln(r,aclog.replay(callId)) && isequal(r.data1(:,2),diff(data(:,2))));
end
fprintf('Copied package isolation passed for %s.\n',method);
end

function restoreEnvironment(oldPath,folder,oldLog,scratch)
cd(folder); path(oldPath); setenv('ACYCLE_LOG_DIR',oldLog); rmdir(scratch,'s');
end
