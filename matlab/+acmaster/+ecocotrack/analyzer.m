function [retval,id] = analyzer(params,id)
% ecocotrack.analyzer parameters: locatcc out_ecc out_eci out_ecoco out_norbit out_depth sr1 sr2 srstep srsh srslice sig ci sh_norb.
% Source: https://github.com/mingsongli/acycle/blob/dcba4279168745b563e0535b954297023dd62fc7/code/corrcoef/ecocotrack.m
if nargin < 2, id = []; end
[retval,id] = accompat.masterInvoke('ecocotrack-v3.1.1+dcba427/analyzer',params,id,@execute);
end

function r = execute(p)
[srslice_range, srn_all, srn_best, eccout_all] = ecocotrack(p.locatcc, p.out_ecc, p.out_eci, p.out_ecoco, ...
    p.out_norbit, p.out_depth, p.sr1, p.sr2, ...
    p.srstep, p.srsh, p.srslice, p.sig, ...
    p.ci, 0, p.sh_norb);
r = struct();
r.srslice_range = srslice_range;
r.srn_all = srn_all;
r.srn_best = srn_best;
r.eccout_all = eccout_all;
end
