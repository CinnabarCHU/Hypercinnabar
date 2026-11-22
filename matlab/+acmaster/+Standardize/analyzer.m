function [retval,id] = analyzer(params,id)
% Standardize.analyzer parameters: data.
% Source: https://github.com/mingsongli/acycle/blob/dcba4279168745b563e0535b954297023dd62fc7/code/guicode/AC.m
if nargin < 2, id = []; end
[retval,id] = accompat.masterInvoke('Standardize-v3.1.1+dcba427/analyzer',params,id,@execute);
end

function r = execute(p)
data = p.data;
%% Copied from mingsongli/acycle@dcba4279168745b563e0535b954297023dd62fc7 code/guicode/AC.m:L3279-L3281
            time = data(:,1);
            value = (data(:,2)-mean(data(:,2)))/std(data(:,2));
            data1 = [time,value];
%% End copied source
r = struct();
r.data1 = data1;
end
