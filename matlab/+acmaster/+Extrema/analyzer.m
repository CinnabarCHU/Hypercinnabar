function [retval,id] = analyzer(params,id)
% Extrema.analyzer parameters: data t1 t2 maxmin ind.
% Source: https://github.com/mingsongli/acycle/blob/dcba4279168745b563e0535b954297023dd62fc7/code/guicode/AC.m
if nargin < 2, id = []; end
[retval,id] = accompat.masterInvoke('Extrema-v3.1.1+dcba427/analyzer',params,id,@execute);
end

function r = execute(p)
data = p.data;
t1 = p.t1;
t2 = p.t2;
maxmin = p.maxmin;
ind = p.ind;
%% Copied from mingsongli/acycle@dcba4279168745b563e0535b954297023dd62fc7 code/guicode/AC.m:L4842-L4848
                [dat] = select_interval(data,t1,t2);
                y = dat(:,ind);
                if maxmin == 1  
                    [m,i] = max(y);
                else
                    [m,i] = min(y);
                end
%% End copied source
row=dat(i,:);
r = struct();
r.m = m;
r.i = i;
r.row = row;
end
