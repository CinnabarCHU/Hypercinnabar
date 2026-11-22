function [retval,id] = analyzer(params,id)
% corrcoefsig.analyzer parameters: dat target orbit7 dt pad sr1 sr2 srstep adjust red nsim display; optional legacyTarget.
% Source: https://github.com/mingsongli/acycle/blob/dcba4279168745b563e0535b954297023dd62fc7/code/corrcoef/corrcoefsig.m
if nargin < 2, id = []; end
[retval,id] = accompat.masterInvoke('corrcoefsig-v3.1.1+dcba427/analyzer',params,id,@execute);
end

function r = execute(p)
guard = accompat.cocoTargetPath(p); %#ok<NASGU>
[corrCI, corr_h0, corry] = corrcoefsig(p.dat, p.target, p.orbit7, p.dt, ...
    p.pad, p.sr1, p.sr2, p.srstep, ...
    p.adjust, p.red, p.nsim, 0, ...
    p.display);
r = struct();
r.corrCI = corrCI;
r.corr_h0 = corr_h0;
r.corry = corry;
end
