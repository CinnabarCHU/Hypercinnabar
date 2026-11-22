function [retval,id] = analyzer(params,id)
% ExampleMars.analyzer parameters: (none).
% Source: https://github.com/mingsongli/acycle/blob/dcba4279168745b563e0535b954297023dd62fc7/code/guicode/AC.m
if nargin < 2, id = []; end
[retval,id] = accompat.masterInvoke('ExampleMars-v3.1.1+dcba427/analyzer',params,id,@execute);
end

function r = execute(p)
%% Copied from mingsongli/acycle@dcba4279168745b563e0535b954297023dd62fc7 code/guicode/AC.m:L9137-L9137
data_name = which('Example-HiRISE-PSP_002733_1880_RED.jpg');
%% End copied source
%% Copied from mingsongli/acycle@dcba4279168745b563e0535b954297023dd62fc7 code/guicode/AC.m:L5023-L5023
                    im_name = imread(data_name);
%% End copied source
r = struct();
r.im_name = im_name;
r.data_name = data_name;
end
