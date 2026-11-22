function [retval,id] = analyzer(params,id)
% corrcoefslices_rankNew.analyzer parameters: dat orbit9 dt pad sr1 sr2 srstep adjust red nsim slices method fmaxdata main_unit_selection targetMode options(MaxFrequency,Seed,ShowPeriodograms,ProgressFcn).
% Source: https://github.com/mingsongli/acycle/blob/dcba4279168745b563e0535b954297023dd62fc7/code/corrcoef/corrcoefslices_rankNew.m
if nargin < 2, id = []; end
[retval,id] = accompat.masterInvoke('corrcoefslices_rankNew-v3.1.1+dcba427/analyzer',params,id,@execute);
end

function r = execute(p)
accompat.requireFields(p.options,{'MaxFrequency','Seed','ShowPeriodograms','ProgressFcn'});
[corrCI, corr_h0, corry, details] = corrcoefslices_rankNew( ...
    p.dat, p.orbit9, p.dt, p.pad, p.sr1, p.sr2, p.srstep, p.adjust, p.red, p.nsim, 0, p.slices,  ...
    p.method, p.fmaxdata, p.main_unit_selection, false, p.targetMode,  ...
    'MaxFrequency',p.options.MaxFrequency, 'Seed',p.options.Seed,  ...
    'ShowPeriodograms',p.options.ShowPeriodograms, 'ProgressFcn',p.options.ProgressFcn);
r = struct();
r.corrCI = corrCI;
r.corr_h0 = corr_h0;
r.corry = corry;
r.details = details;
end
