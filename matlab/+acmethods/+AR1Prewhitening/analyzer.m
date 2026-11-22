function [retval, id] = analyzer(params, id)
% AR1Prewhitening.analyzer parameters: data rho1.
% Source: https://github.com/mingsongli/acycle/blob/b52ea9f510f3be00bde9a0238b9898a1e2315b74/code/guicode/prewhitenGUI.m#L284
if nargin < 2, id = []; end
[retval, id] = aclog.invoke('AR1Prewhitening-v1.0/analyzer', params, id, @execute);
end

function r = execute(p)
data = p.data;
rho1 = p.rho1;
%% Copied from mingsongli/acycle@b52ea9f510f3be00bde9a0238b9898a1e2315b74 code/guicode/prewhitenGUI.m:L284-L284
datp = prewhitening(data,rho1);
%% End copied source
r = struct();
r.datp = datp;
end
