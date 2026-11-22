function [retval,id] = analyzer(params,id)
% ac_sort_dir_entries.analyzer parameters: entries sortMode.
% Source: https://github.com/mingsongli/acycle/blob/dcba4279168745b563e0535b954297023dd62fc7/code/misc/ac_sort_dir_entries.m
if nargin < 2, id = []; end
[retval,id] = accompat.masterInvoke('ac_sort_dir_entries-v3.1.1+dcba427/analyzer',params,id,@execute);
end

function r = execute(p)
[sortedEntries] = ac_sort_dir_entries(p.entries, p.sortMode);
r = struct();
r.sortedEntries = sortedEntries;
end
