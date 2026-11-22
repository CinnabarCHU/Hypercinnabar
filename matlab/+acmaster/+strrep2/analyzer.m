function [retval,id] = analyzer(params,id)
% strrep2.analyzer parameters: filename pre post.
% Source: https://github.com/mingsongli/acycle/blob/dcba4279168745b563e0535b954297023dd62fc7/code/misc/strrep2.m
if nargin < 2, id = []; end
[retval,id] = accompat.masterInvoke('strrep2-v3.1.1+dcba427/analyzer',params,id,@execute);
end

function r = execute(p)
[foldername] = strrep2(p.filename, p.pre, p.post);
r = struct();
r.foldername = foldername;
end
