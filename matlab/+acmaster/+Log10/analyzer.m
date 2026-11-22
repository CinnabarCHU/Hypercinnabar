function [retval,id] = analyzer(params,id)
% Log10.analyzer parameters: data.
% Source: https://github.com/mingsongli/acycle/blob/dcba4279168745b563e0535b954297023dd62fc7/code/guicode/AC.m
if nargin < 2, id = []; end
[retval,id] = accompat.masterInvoke('Log10-v3.1.1+dcba427/analyzer',params,id,@execute);
end

function r = execute(p)
data = p.data;
%% Copied from mingsongli/acycle@dcba4279168745b563e0535b954297023dd62fc7 code/guicode/AC.m:L3456-L3458
            time = data(:,1);
            value = log10(data(:,2));
            data1 = [time,value];
%% End copied source
r = struct();
r.data1 = data1;
end
