function [retval, id] = plotter(params, id)
% ecocoplot.plotter parameters: prt_sr out_depth out_ecc out_ep out_eci out_ecoco out_ecocorb out_norbit plotn.
% Source: https://github.com/mingsongli/acycle/blob/b52ea9f510f3be00bde9a0238b9898a1e2315b74/code/corrcoef/ecocoplot.m#L1
if nargin < 2, id = []; end
[retval, id] = aclog.invoke('ecocoplot-v1.0/plotter', params, id, @execute);
end

function r = execute(p)
[prt_sr] = ecocoplot(p.prt_sr, p.out_depth, p.out_ecc, p.out_ep, ...
    p.out_eci, p.out_ecoco, p.out_ecocorb, p.out_norbit, ...
    p.plotn);
r = struct();
r.prt_sr = prt_sr;
end
