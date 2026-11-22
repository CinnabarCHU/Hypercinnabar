function [retval,id] = analyzer(params,id)
% cocoConclusionReport.analyzer parameters: mode arguments (cell).
% Source: https://github.com/mingsongli/acycle/blob/dcba4279168745b563e0535b954297023dd62fc7/code/corrcoef/cocoConclusionReport.m
if nargin < 2, id = []; end
[retval,id] = accompat.masterInvoke('cocoConclusionReport-v3.1.1+dcba427/analyzer',params,id,@execute);
end

function r = execute(p)
[report] = cocoConclusionReport(p.mode, p.arguments{:});
r = struct();
r.report = report;
end
