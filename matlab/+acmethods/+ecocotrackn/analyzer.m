function [retval, id] = analyzer(params, id)
% ecocotrackn.analyzer parameters: locat srsh iniloc srn method.
% Source: https://github.com/mingsongli/acycle/blob/b52ea9f510f3be00bde9a0238b9898a1e2315b74/code/corrcoef/ecocotrackn.m#L1
if nargin < 2, id = []; end
[retval, id] = aclog.invoke('ecocotrackn-v1.0/analyzer', params, id, @execute);
end

function r = execute(p)
[srn1, locatnan] = ecocotrackn(p.locat, p.srsh, p.iniloc, p.srn, p.method);
r = struct();
r.srn1 = srn1;
r.locatnan = locatnan;
end
