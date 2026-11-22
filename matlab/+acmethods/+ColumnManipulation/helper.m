function [retval, id] = helper(params, id)
% ColumnManipulation.helper parameters: dataCell.
% Source: https://github.com/mingsongli/acycle/blob/b52ea9f510f3be00bde9a0238b9898a1e2315b74/code/guicode/column_manipulateGUI.m#L82
% Source: https://github.com/mingsongli/acycle/blob/b52ea9f510f3be00bde9a0238b9898a1e2315b74/code/guicode/column_manipulateGUI.m#L92
if nargin < 2, id = []; end
[retval, id] = aclog.invoke('ColumnManipulation-v1.0/helper', params, id, @execute);
end

function r = execute(p)
dataCell = p.dataCell;
% GUI selects column 2 and initializes its weight to one (lines 82–92).
r=struct('dataCell',{dataCell},'colman1',[2,1]);
end
