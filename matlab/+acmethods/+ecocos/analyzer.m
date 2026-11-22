function [retval, id] = analyzer(params, id)
% ecocos.analyzer parameters: data target window dt step delinear red pad sr1 sr2 srstep adjust.
% Source: https://github.com/mingsongli/acycle/blob/b52ea9f510f3be00bde9a0238b9898a1e2315b74/code/corrcoef/ecocos.m#L1
if nargin < 2, id = []; end
[retval, id] = aclog.invoke('ecocos-v1.0/analyzer', params, id, @execute);
end

function r = execute(p)
[prt_sr, out_depth, out_ecc, out_ep, out_eci, ...
    out_ecoco, out_ecocorb, norbit] = ecocos(p.data, p.target, p.window, p.dt, ...
    p.step, p.delinear, p.red, p.pad, ...
    p.sr1, p.sr2, p.srstep, p.adjust, ...
    0);
r = struct();
r.prt_sr = prt_sr;
r.out_depth = out_depth;
r.out_ecc = out_ecc;
r.out_ep = out_ep;
r.out_eci = out_eci;
r.out_ecoco = out_ecoco;
r.out_ecocorb = out_ecocorb;
r.norbit = norbit;
end
