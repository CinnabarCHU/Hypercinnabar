function [retval,id] = analyzer(params,id)
% runSyn3FourMethodPublicationStudy.analyzer parameters: options(Phase,InputRoot,OutputRoot,CocoNSim,EcocoNSim,Seed,Resume).
% Source: https://github.com/mingsongli/acycle/blob/dcba4279168745b563e0535b954297023dd62fc7/code/corrcoef/runSyn3FourMethodPublicationStudy.m
if nargin < 2, id = []; end
[retval,id] = accompat.masterInvoke('runSyn3FourMethodPublicationStudy-v3.1.1+dcba427/analyzer',params,id,@execute);
end

function r = execute(p)
accompat.requireFields(p.options,{'Phase','InputRoot','OutputRoot','CocoNSim','EcocoNSim','Seed','Resume'});
[study] = runSyn3FourMethodPublicationStudy( ...
    'Phase',p.options.Phase, 'InputRoot',p.options.InputRoot, 'OutputRoot',p.options.OutputRoot,  ...
    'CocoNSim',p.options.CocoNSim, 'EcocoNSim',p.options.EcocoNSim, 'Seed',p.options.Seed,  ...
    'Resume',p.options.Resume);
r = struct();
r.study = study;
end
