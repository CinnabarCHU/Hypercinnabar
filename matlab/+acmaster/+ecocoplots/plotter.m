function [retval,id] = plotter(params,id)
% ecocoplots.plotter parameters: prt_sr out_depth out_ecc out_ep out_eci out_ecoco out_ecocorb.
% Source: https://github.com/mingsongli/acycle/blob/dcba4279168745b563e0535b954297023dd62fc7/code/corrcoef/ecocoplots.m
if nargin < 2, id = []; end
[retval,id] = accompat.masterInvoke('ecocoplots-v3.1.1+dcba427/plotter',params,id,@execute);
end

function r = execute(p)
ecocoplots(p.prt_sr, p.out_depth, p.out_ecc, p.out_ep, p.out_eci, p.out_ecoco, p.out_ecocorb);
r = [];
end
