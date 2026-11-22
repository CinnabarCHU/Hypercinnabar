function [retval,id] = plotter(params,id)
% ecocoplot.plotter parameters: prt_sr out_depth out_ecc out_ep out_eci out_ecoco out_ecocorb out_norbit plotn ecoDetails.
% Source: https://github.com/mingsongli/acycle/blob/dcba4279168745b563e0535b954297023dd62fc7/code/corrcoef/ecocoplot.m
if nargin < 2, id = []; end
[retval,id] = accompat.masterInvoke('ecocoplot-v3.1.1+dcba427/plotter',params,id,@execute);
end

function r = execute(p)
ecocoplot( ...
    p.prt_sr, p.out_depth, p.out_ecc, p.out_ep, p.out_eci, p.out_ecoco, p.out_ecocorb,  ...
    p.out_norbit, p.plotn, p.ecoDetails);
r = [];
end
