function out = robot(p,id,host)
% Run the exact single-series workflow. Host handles and file writes stay out of replay.
if nargin < 2 || isempty(id), id = acMenuNewId(); end
if nargin < 3, host = struct(); end
[~,engine] = accore.register('push_robot',p.operation);
base = struct('plot',false,'save',false,'pause',0,'folder',accore.io('workspace'),'refresh',@()[], ...
    'setMaxFrequency',@(~)[],'setMinPeriod',@(~)[]);
host = acMenuMerge(base,host);
if host.plot
    host.warning = @warndlg; host.problem = @errordlg;
else
    host.warning = @(msg)warning('Acycle:Robot:Stage','%s',msg);
    host.problem = host.warning;
end
journal = aclog.interfaceId(id,true);
out = aclog.invoke(['Workflow_',engine.operation,'-v1'],p,journal,@execute);
    function [r,status] = execute(input)
        before = findall(groot,'Type','figure');
        oldVis = get(groot,'DefaultFigureVisible'); oldPwd = pwd;
        oldFig = get(groot,'CurrentFigure');
        restore = onCleanup(@()restoreHost(before,oldFig,oldVis,oldPwd,host.plot)); %#ok<NASGU>
        if ~host.plot, set(groot,'DefaultFigureVisible','off'); end
        if strcmp(engine.revision,'master')
            scoped = accompat.masterPath(); %#ok<NASGU>
            r = acRobotFlowMaster(input,host);
        else
            scoped = acMenuGuidePath(); %#ok<NASGU>
            r = acRobotFlowLegacy(input,host);
        end
        status = 'done';
        if input.settings.wavelet && isempty(r.wavelet), status = 'incomplete'; end
    end
end

function restoreHost(before,oldFig,visibility,folder,show)
cd(folder);
if ~show
    current = findall(groot,'Type','figure');
    delete(current(~ismember(current,before)));
    if isgraphics(oldFig), set(groot,'CurrentFigure',oldFig); end
end
set(groot,'DefaultFigureVisible',visibility);
end
