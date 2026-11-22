function [retval,id] = analyzer(params,id)
% ecocos.analyzer parameters: data target window dt step delinear red pad sr1 sr2 srstep adjust; optional legacyTarget.
% Source: https://github.com/mingsongli/acycle/blob/dcba4279168745b563e0535b954297023dd62fc7/code/corrcoef/ecocos.m
if nargin < 2, id = []; end
[retval,id] = accompat.masterInvoke('ecocos-v3.1.1+dcba427/analyzer',params,id,@execute);
end

function r = execute(p)
guard = accompat.cocoTargetPath(p); %#ok<NASGU>
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
