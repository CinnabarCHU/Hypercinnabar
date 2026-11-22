function [retval, id] = helper(params, id)
% StratigraphicCorrelation.helper parameters: reference series tiepoints1 tiepoints2.
% Source: https://github.com/mingsongli/acycle/blob/b52ea9f510f3be00bde9a0238b9898a1e2315b74/code/guicode/CorrelationGUI.m#L248
% Source: https://github.com/mingsongli/acycle/blob/b52ea9f510f3be00bde9a0238b9898a1e2315b74/code/guicode/CorrelationGUI.m#L334
% Source: https://github.com/mingsongli/acycle/blob/b52ea9f510f3be00bde9a0238b9898a1e2315b74/code/guicode/CorrelationGUI.m#L421
if nargin < 2, id = []; end
[retval, id] = aclog.invoke('StratigraphicCorrelation-v1.0/helper', params, id, @execute);
end

function r = execute(p)
rawref=p.reference; rawser=p.series; r=struct('data1',rawser,'reference',rawref);
r.refxmin=min(rawref(:,1)); r.refxmax=max(rawref(:,1));
r.serxmin=min(rawser(:,1)); r.serxmax=max(rawser(:,1));
r.tiepoints1=p.tiepoints1; r.tiepoints2=p.tiepoints2;
if size(r.tiepoints1,1)~=size(r.tiepoints2,1), error('Acycle:Correlation:Tiepoints','Reference and series require paired tie points.'); end
end
