function [retval, id] = plotter(params, id)
% ecocoplots.plotter parameters: prt_sr out_depth out_ecc out_ep out_eci out_ecoco out_ecocorb.
% Source: https://github.com/mingsongli/acycle/blob/b52ea9f510f3be00bde9a0238b9898a1e2315b74/code/corrcoef/ecocoplots.m#L1
if nargin < 2, id = []; end
[retval, id] = aclog.invoke('ecocoplots-v1.0/plotter', params, id, @execute);
end

function r = execute(p)
[prt_sr] = ecocoplots(p.prt_sr, p.out_depth, p.out_ecc, p.out_ep, p.out_eci, p.out_ecoco, p.out_ecocorb);
r = struct();
r.prt_sr = prt_sr;
end
