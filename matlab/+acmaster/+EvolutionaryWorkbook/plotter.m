function [retval,id] = plotter(params,id)
% EvolutionaryWorkbook.plotter parameters: outputFile parameters power frequency time redNoise.
% Source: https://github.com/mingsongli/acycle/blob/dcba4279168745b563e0535b954297023dd62fc7/code/seriesanalysis/saveEvofftWorkbook.m
if nargin < 2, id = []; end
[retval,id] = accompat.masterInvoke('EvolutionaryWorkbook-v3.1.1+dcba427/plotter',params,id,@execute);
end

function r = execute(p)
saveEvofftWorkbook(p.outputFile,p.parameters,p.power,p.frequency,p.time,p.redNoise);
r = p.outputFile;
end
