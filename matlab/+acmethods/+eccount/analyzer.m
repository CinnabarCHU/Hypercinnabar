function [retval, id] = analyzer(params, id)
% eccount.analyzer parameters: srn ecc eci ecoco enorb.
% Source: https://github.com/mingsongli/acycle/blob/b52ea9f510f3be00bde9a0238b9898a1e2315b74/code/corrcoef/eccount.m#L1
if nargin < 2, id = []; end
[retval, id] = aclog.invoke('eccount-v1.0/analyzer', params, id, @execute);
end

function r = execute(p)
[eccounts] = eccount(p.srn, p.ecc, p.eci, p.ecoco, p.enorb);
r = struct();
r.eccounts = eccounts;
end
