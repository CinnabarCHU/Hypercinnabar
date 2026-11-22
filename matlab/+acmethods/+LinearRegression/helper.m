function [retval, id] = helper(params, id)
% LinearRegression.helper parameters: selectedData.
% Source: https://github.com/mingsongli/acycle/blob/b52ea9f510f3be00bde9a0238b9898a1e2315b74/code/guicode/AC.m#L8941
if nargin < 2, id = []; end
[retval, id] = aclog.invoke('LinearRegression-v1.0/helper', params, id, @execute);
end

function r = execute(p)
selectedData=p.selectedData;
validateattributes(selectedData,{'numeric'},{'2d','nonempty'});
if size(selectedData,2)<2, error('Acycle:LinearRegression:Columns','Select two columns.'); end
r=struct('selectedData',selectedData(:,1:2));
end
