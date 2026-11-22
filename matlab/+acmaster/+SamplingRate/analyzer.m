function [retval,id] = analyzer(params,id)
% SamplingRate.analyzer parameters: data_filterout.
% Source: https://github.com/mingsongli/acycle/blob/dcba4279168745b563e0535b954297023dd62fc7/code/guicode/AC.m
if nargin < 2, id = []; end
[retval,id] = accompat.masterInvoke('SamplingRate-v3.1.1+dcba427/analyzer',params,id,@execute);
end

function r = execute(p)
data_filterout = p.data_filterout;
%% Copied from mingsongli/acycle@dcba4279168745b563e0535b954297023dd62fc7 code/guicode/AC.m:L6920-L6922
            t = data_filterout(:,1);
            dt = diff(t);
            len_t = length(t);
%% End copied source
%% Copied from mingsongli/acycle@dcba4279168745b563e0535b954297023dd62fc7 code/guicode/AC.m:L6924-L6925
            datasamp = [t(1:len_t-1),dt];
            datasamp = datasamp(~any(isnan(datasamp),2),:);
%% End copied source
r = struct();
r.datasamp = datasamp;
r.dt = dt;
end
