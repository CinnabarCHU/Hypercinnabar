function [retval,id] = helper(params,id)
% smoothciML.helper parameters: X Y method span bootn.
% Source: https://github.com/mingsongli/acycle/blob/dcba4279168745b563e0535b954297023dd62fc7/code/seriesanalysis/smoothciML.m
if nargin < 2, id = []; end
[retval,id] = accompat.masterInvoke('smoothciML-v3.1.1+dcba427/helper',params,id,@execute);
end

function r = execute(p)
r = aclog.defaults(p, {'X', 'Y', 'method', 'span', 'bootn'}, 2, @legacyDefaults);
end

function values = legacyDefaults(X, Y, method, span, bootn)
%% Copied from mingsongli/acycle@dcba4279168745b563e0535b954297023dd62fc7 code/seriesanalysis/smoothciML.m:L25-L33
if nargin < 5 || isempty(bootn)
    bootn = 500;    % 500 or 1000
    if nargin < 4 || isempty(span)
        span = 0.3; % 0 <= span <= 1
        if nargin < 3
            method = 'loess';  % 'loess', 'lowess', 'rloess', or 'rlowess'
        end
    end
end
%% End copied source
values = struct();
if exist('X', 'var'), values.X = X; end
if exist('Y', 'var'), values.Y = Y; end
if exist('method', 'var'), values.method = method; end
if exist('span', 'var'), values.span = span; end
if exist('bootn', 'var'), values.bootn = bootn; end
end
