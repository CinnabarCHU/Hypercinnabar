function [retval,id] = analyzer(params,id)
% RGBToGray.analyzer parameters: im_name.
% Source: https://github.com/mingsongli/acycle/blob/dcba4279168745b563e0535b954297023dd62fc7/code/guicode/AC.m
if nargin < 2, id = []; end
[retval,id] = accompat.masterInvoke('RGBToGray-v3.1.1+dcba427/analyzer',params,id,@execute);
end

function r = execute(p)
im_name = p.im_name;
%% Copied from mingsongli/acycle@dcba4279168745b563e0535b954297023dd62fc7 code/guicode/AC.m:L5119-L5119
                        I = rgb2gray(im_name);
%% End copied source
r = struct();
r.I = I;
end
