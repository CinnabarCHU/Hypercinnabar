function [retval,id] = helper(params,id)
% BootstrapSmooth.helper parameters: data.
% Source: https://github.com/mingsongli/acycle/blob/dcba4279168745b563e0535b954297023dd62fc7/code/guicode/SmoothBootGUI.m
if nargin < 2, id = []; end
[retval,id] = accompat.masterInvoke('BootstrapSmooth-v3.1.1+dcba427/helper',params,id,@execute);
end

function r = execute(p)
data=p.data;
%% Copied from mingsongli/acycle@dcba4279168745b563e0535b954297023dd62fc7 code/guicode/SmoothBootGUI.m:L40-L43
x = data(:,1);
y = data(:,2);

xlen = max(x) - min(x);
%% End copied source
r=struct('x',x,'y',y,'method','lowess','span',.3,'bootn',1000);
end
