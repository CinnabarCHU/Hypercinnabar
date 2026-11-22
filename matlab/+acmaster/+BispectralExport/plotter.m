function [retval,id] = plotter(params,id)
% BispectralExport.plotter parameters: result settings outputDirectory baseName.
% Source: https://github.com/mingsongli/acycle/blob/dcba4279168745b563e0535b954297023dd62fc7/code/package/bispectral/bispectralSave.m
% Source: https://github.com/mingsongli/acycle/blob/dcba4279168745b563e0535b954297023dd62fc7/code/package/bispectral/bispectralPlot.m
if nargin < 2, id = []; end
[retval,id] = accompat.masterInvoke('BispectralExport-v3.1.1+dcba427/plotter',params,id,@execute);
end

function r = execute(p)
if isempty(p.outputDirectory) || isempty(p.baseName), error('Acycle:Bispectral:Destination','Supply the destination and result name.'); end
[fig,~] = bispectralPlot(p.result,p.settings);
cleanup = onCleanup(@() close(fig));
r = bispectralSave(p.result,fig,p.outputDirectory,p.baseName);
end
