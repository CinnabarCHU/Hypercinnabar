function [retval, id] = analyzer(params, id)
% corrsig.analyzer parameters: dat target orbit7 dt pad sr1 sr2 srstep adjust red nsim display.
% Source: https://github.com/mingsongli/acycle/blob/b52ea9f510f3be00bde9a0238b9898a1e2315b74/code/corrcoef/corrsig.m#L1
if nargin < 2, id = []; end
[retval, id] = aclog.invoke('corrsig-v1.0/analyzer', params, id, @execute);
end

function r = execute(p)
[corrCI, corr_h0, corry] = corrsig(p.dat, p.target, p.orbit7, p.dt, ...
    p.pad, p.sr1, p.sr2, p.srstep, ...
    p.adjust, p.red, p.nsim, 0, ...
    p.display);
r = struct();
r.corrCI = corrCI;
r.corr_h0 = corr_h0;
r.corry = corry;
end
