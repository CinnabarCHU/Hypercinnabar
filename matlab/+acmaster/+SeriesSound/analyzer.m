function [retval,id] = analyzer(params,id)
% SeriesSound.analyzer parameters: data a b c.
% Source: https://github.com/mingsongli/acycle/blob/dcba4279168745b563e0535b954297023dd62fc7/code/guicode/AC.m
if nargin < 2, id = []; end
[retval,id] = accompat.masterInvoke('SeriesSound-v3.1.1+dcba427/analyzer',params,id,@execute);
end

function r = execute(p)
data = p.data;
a = p.a;
b = p.b;
c = p.c;
%% Copied from mingsongli/acycle@dcba4279168745b563e0535b954297023dd62fc7 code/guicode/AC.m:L9614-L9618
                if c == 1
                    y = repmat( data(:,2)-mean(data(:,2)), [a,1]);
                else
                    y = repmat( data(:,2), [a,1]);
                end
%% End copied source
Fs=b*8192;
r = struct();
r.y = y;
r.Fs = Fs;
end
