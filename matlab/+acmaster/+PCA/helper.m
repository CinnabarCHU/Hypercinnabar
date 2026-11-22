function [retval,id] = helper(params,id)
% PCA.helper parameters: data_new.
% Source: https://github.com/mingsongli/acycle/blob/dcba4279168745b563e0535b954297023dd62fc7/code/guicode/AC.m
if nargin < 2, id = []; end
[retval,id] = accompat.masterInvoke('PCA-v3.1.1+dcba427/helper',params,id,@execute);
end

function r = execute(p)
data_new = p.data_new;
%% Copied from mingsongli/acycle@dcba4279168745b563e0535b954297023dd62fc7 code/guicode/AC.m:L8048-L8048
    defaultans = {'1'};
%% End copied source
depthtime=str2double(defaultans{1});
r = struct();
r.data_new = data_new;
r.depthtime = depthtime;
end
