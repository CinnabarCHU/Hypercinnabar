function [retval,id] = analyzer(params,id)
% ExampleRedNoise.analyzer parameters: (none).
% Source: https://github.com/mingsongli/acycle/blob/dcba4279168745b563e0535b954297023dd62fc7/code/guicode/AC.m
if nargin < 2, id = []; end
[retval,id] = accompat.masterInvoke('ExampleRedNoise-v3.1.1+dcba427/analyzer',params,id,@execute);
end

function r = execute(p)
%% Copied from mingsongli/acycle@dcba4279168745b563e0535b954297023dd62fc7 code/guicode/AC.m:L9030-L9030
data_name = which('Example-Rednoise0.7-2000.txt');
%% End copied source
%% Copied from mingsongli/acycle@dcba4279168745b563e0535b954297023dd62fc7 code/guicode/AC.m:L3074-L3074
        data = load(data_name);
%% End copied source
r = struct();
r.data = data;
r.data_name = data_name;
end
