function [retval,id] = analyzer(params,id)
% SortUnique.analyzer parameters: data datasort dataunique dataempty.
% Source: https://github.com/mingsongli/acycle/blob/dcba4279168745b563e0535b954297023dd62fc7/code/guicode/AC.m
if nargin < 2, id = []; end
[retval,id] = accompat.masterInvoke('SortUnique-v3.1.1+dcba427/analyzer',params,id,@execute);
end

function r = execute(p)
data = p.data;
datasort = p.datasort;
dataunique = p.dataunique;
dataempty = p.dataempty;
%% Copied from mingsongli/acycle@dcba4279168745b563e0535b954297023dd62fc7 code/guicode/AC.m:L5972-L5974
                            data = data(~any(isnan(data),2),:); % remove NaN values
                            if datasort == 1
                                data = sortrows(data);
%% End copied source
%% Copied from mingsongli/acycle@dcba4279168745b563e0535b954297023dd62fc7 code/guicode/AC.m:L5976-L5978
                            end
                            if dataunique == 1
                                data=findduplicate(data);
%% End copied source
%% Copied from mingsongli/acycle@dcba4279168745b563e0535b954297023dd62fc7 code/guicode/AC.m:L81-L81
end
%% End copied source
%% Copied from mingsongli/acycle@dcba4279168745b563e0535b954297023dd62fc7 code/guicode/AC.m:L5984-L5985
                            if dataempty == 1
                                data(any(isinf(data),2),:) = [];
%% End copied source
end
r = struct();
r.data = data;
end
