function [retval, id] = helper(params, id)
% SortUnique.helper parameters: data.
% Source: https://github.com/mingsongli/acycle/blob/b52ea9f510f3be00bde9a0238b9898a1e2315b74/code/guicode/AC.m#L610
if nargin < 2, id = []; end
[retval, id] = aclog.invoke('SortUnique-v1.0/helper', params, id, @execute);
end

function r = execute(p)
data = p.data;
%% Copied from mingsongli/acycle@b52ea9f510f3be00bde9a0238b9898a1e2315b74 code/guicode/AC.m:L610-L612
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
