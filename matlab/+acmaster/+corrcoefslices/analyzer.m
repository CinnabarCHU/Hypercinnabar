function [retval,id] = analyzer(params,id)
% corrcoefslices.analyzer parameters: dat target orbit7 dt pad sr1 sr2 srstep adjust red nsim slices.
% Source: https://github.com/mingsongli/acycle/blob/dcba4279168745b563e0535b954297023dd62fc7/code/corrcoef/corrcoefslices.m
if nargin < 2, id = []; end
[retval,id] = accompat.masterInvoke('corrcoefslices-v3.1.1+dcba427/analyzer',params,id,@execute);
end

function r = execute(p)
[corrCI, corr_h0, corry] = corrcoefslices( ...
    p.dat, p.target, p.orbit7, p.dt, p.pad, p.sr1, p.sr2, p.srstep, p.adjust, p.red, p.nsim, 0,  ...
    p.slices);
r = struct();
r.corrCI = corrCI;
r.corr_h0 = corr_h0;
r.corry = corry;
end
