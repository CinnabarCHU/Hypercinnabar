function [retval,id] = helper(params,id)
% SortUnique.helper parameters: data.
% Source: https://github.com/mingsongli/acycle/blob/dcba4279168745b563e0535b954297023dd62fc7/code/guicode/AC.m
if nargin < 2, id = []; end
[retval,id] = accompat.masterInvoke('SortUnique-v3.1.1+dcba427/helper',params,id,@execute);
end

function r = execute(p)
data = p.data;
%% Copied from mingsongli/acycle@dcba4279168745b563e0535b954297023dd62fc7 code/guicode/AC.m:L1368-L1370
handles.math_sort = 1;
handles.math_unique = 1;
handles.math_deleteempty = 1;
%% End copied source
datasort=handles.math_sort; dataunique=handles.math_unique; dataempty=handles.math_deleteempty;
r = struct();
r.data = data;
r.datasort = datasort;
r.dataunique = dataunique;
r.dataempty = dataempty;
end
