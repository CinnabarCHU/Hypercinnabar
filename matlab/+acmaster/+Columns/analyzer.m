function [retval,id] = analyzer(params,id)
% Columns.analyzer parameters: data c1 c2.
% Source: https://github.com/mingsongli/acycle/blob/dcba4279168745b563e0535b954297023dd62fc7/code/guicode/AC.m
if nargin < 2, id = []; end
[retval,id] = accompat.masterInvoke('Columns-v3.1.1+dcba427/analyzer',params,id,@execute);
end

function r = execute(p)
data = p.data;
c1 = p.c1;
c2 = p.c2;
%% Copied from mingsongli/acycle@dcba4279168745b563e0535b954297023dd62fc7 code/guicode/AC.m:L7242-L7242
            data = data(~any(isnan(data),2),:);
%% End copied source
%% Copied from mingsongli/acycle@dcba4279168745b563e0535b954297023dd62fc7 code/guicode/AC.m:L7910-L7911
                    data_new(:,1) = data(:,c1);
                    data_new(:,2:2+length(c2)-1) = data(:,c2);
%% End copied source
r = struct();
r.data_new = data_new;
end
