function [retval,id] = helper(params,id)
% Clipping.helper parameters: data.
% Source: https://github.com/mingsongli/acycle/blob/dcba4279168745b563e0535b954297023dd62fc7/code/guicode/AC.m
if nargin < 2, id = []; end
[retval,id] = accompat.masterInvoke('Clipping-v3.1.1+dcba427/helper',params,id,@execute);
end

function r = execute(p)
data = p.data;
%% Copied from mingsongli/acycle@dcba4279168745b563e0535b954297023dd62fc7 code/guicode/AC.m:L3371-L3371
            defaultans = {num2str(nanmean(data(:,2))), '1','0'};
%% End copied source
clip_value=str2double(defaultans{1}); clip_high=str2double(defaultans{2}); clip_set=str2double(defaultans{3});
r = struct();
r.data = data;
r.clip_value = clip_value;
r.clip_high = clip_high;
r.clip_set = clip_set;
end
