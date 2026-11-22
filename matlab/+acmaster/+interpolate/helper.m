function [retval,id] = helper(params,id)
% interpolate.helper parameters: data.
% Source: https://github.com/mingsongli/acycle/blob/dcba4279168745b563e0535b954297023dd62fc7/code/guicode/AC.m
if nargin < 2, id = []; end
[retval,id] = accompat.masterInvoke('interpolate-v3.1.1+dcba427/helper',params,id,@execute);
end

function r = execute(p)
data = p.data;
%% Copied from mingsongli/acycle@dcba4279168745b563e0535b954297023dd62fc7 code/guicode/AC.m:L3235-L3236
                time = data(:,1);
                srmedian = median(diff(time));
%% End copied source
interpolate_rate=str2double(num2str(srmedian));
r = struct();
r.data = data;
r.interpolate_rate = interpolate_rate;
end
