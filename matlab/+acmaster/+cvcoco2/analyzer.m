function [retval,id] = analyzer(params,id)
% cvcoco2.analyzer parameters: data orbit9 pad sr1 sr2 srstep red nsim method options(BatchSize,Seed,ProgressFcn,MaxFrequency,AnalysisName,SplitMode,InterleavedPhase,Verbose,WarnOnPartialTraining).
% Source: https://github.com/mingsongli/acycle/blob/dcba4279168745b563e0535b954297023dd62fc7/code/corrcoef/cvcoco2.m
if nargin < 2, id = []; end
[retval,id] = accompat.masterInvoke('cvcoco2-v3.1.1+dcba427/analyzer',params,id,@execute);
end

function r = execute(p)
accompat.requireFields(p.options,{'BatchSize','Seed','ProgressFcn','MaxFrequency','AnalysisName','SplitMode','InterleavedPhase','Verbose','WarnOnPartialTraining'});
[result] = cvcoco2( ...
    p.data, p.orbit9, p.pad, p.sr1, p.sr2, p.srstep, p.red, p.nsim, p.method,  ...
    'BatchSize',p.options.BatchSize, 'Seed',p.options.Seed, 'ProgressFcn',p.options.ProgressFcn,  ...
    'MaxFrequency',p.options.MaxFrequency, 'AnalysisName',p.options.AnalysisName,  ...
    'SplitMode',p.options.SplitMode, 'InterleavedPhase',p.options.InterleavedPhase,  ...
    'Verbose',p.options.Verbose, 'WarnOnPartialTraining',p.options.WarnOnPartialTraining);
r = struct();
r.result = result;
end
