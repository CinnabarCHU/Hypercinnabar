function [retval,id] = helper(params,id)
% SeriesSound.helper parameters: data.
% Source: https://github.com/mingsongli/acycle/blob/dcba4279168745b563e0535b954297023dd62fc7/code/guicode/AC.m
if nargin < 2, id = []; end
[retval,id] = accompat.masterInvoke('SeriesSound-v3.1.1+dcba427/helper',params,id,@execute);
end

function r = execute(p)
data = p.data;
%% Copied from mingsongli/acycle@dcba4279168745b563e0535b954297023dd62fc7 code/guicode/AC.m:L9607-L9607
            defaultans = {'5','1','1'};
%% End copied source
r=struct('data',data,'a',str2double(defaultans{1}),'b',str2double(defaultans{2}),'c',str2double(defaultans{3}));
end
