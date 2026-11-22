function [retval,id] = analyzer(params,id)
% cocoAdaptivePublicationReport.analyzer parameters: corrCI corrH0 details.
% Source: https://github.com/mingsongli/acycle/blob/dcba4279168745b563e0535b954297023dd62fc7/code/corrcoef/cocoAdaptivePublicationReport.m
if nargin < 2, id = []; end
[retval,id] = accompat.masterInvoke('cocoAdaptivePublicationReport-v3.1.1+dcba427/analyzer',params,id,@execute);
end

function r = execute(p)
[report] = cocoAdaptivePublicationReport(p.corrCI, p.corrH0, p.details);
r = struct();
r.report = report;
end
