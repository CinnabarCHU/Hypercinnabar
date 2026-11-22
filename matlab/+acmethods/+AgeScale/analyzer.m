function [retval, id] = analyzer(params, id)
% AgeScale.analyzer parameters: data tiepoints.
% Source: https://github.com/mingsongli/acycle/blob/b52ea9f510f3be00bde9a0238b9898a1e2315b74/code/guicode/agescale.m#L447
if nargin < 2, id = []; end
[retval, id] = aclog.invoke('AgeScale-v1.0/analyzer', params, id, @execute);
end

function r = execute(p)
data = p.data;
tiepoints = p.tiepoints;
%% Copied from mingsongli/acycle@b52ea9f510f3be00bde9a0238b9898a1e2315b74 code/guicode/agescale.m:L447-L447
    [time,handles.sr] = depthtotime(data(:,1),tiepoints);
%% End copied source
sr=handles.sr; tuned=[time,data(:,2:end)];
r = struct();
r.time = time;
r.sr = sr;
r.tuned = tuned;
end
