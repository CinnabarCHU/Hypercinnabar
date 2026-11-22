function [retval,id] = helper(params,id)
% depeaks.helper parameters: data.
% Source: https://github.com/mingsongli/acycle/blob/dcba4279168745b563e0535b954297023dd62fc7/code/guicode/AC.m
if nargin < 2, id = []; end
[retval,id] = accompat.masterInvoke('depeaks-v3.1.1+dcba427/helper',params,id,@execute);
end

function r = execute(p)
data = p.data;
%% Copied from mingsongli/acycle@dcba4279168745b563e0535b954297023dd62fc7 code/guicode/AC.m:L3076-L3076
        value = data(:,2);
%% End copied source
%% Copied from mingsongli/acycle@dcba4279168745b563e0535b954297023dd62fc7 code/guicode/AC.m:L4482-L4482
            defaultans = {num2str(min(value)),num2str(max(value))};
%% End copied source
r=struct('data',data,'ymin_cut',str2double(defaultans{1}),'ymax_cut',str2double(defaultans{2}));
end
