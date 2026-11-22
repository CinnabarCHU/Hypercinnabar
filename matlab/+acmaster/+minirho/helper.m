function [retval,id] = helper(params,id)
% minirho.helper parameters: s0 fn ft pxxsmooth linlog genplot.
% Source: https://github.com/mingsongli/acycle/blob/dcba4279168745b563e0535b954297023dd62fc7/code/seriesanalysis/minirho.m
if nargin < 2, id = []; end
[retval,id] = accompat.masterInvoke('minirho-v3.1.1+dcba427/helper',params,id,@execute);
end

function r = execute(p)
r = aclog.defaults(p, {'s0', 'fn', 'ft', 'pxxsmooth', 'linlog', 'genplot'}, 4, @legacyDefaults);
end

function values = legacyDefaults(s0, fn, ft, pxxsmooth, linlog, genplot)
%% Copied from mingsongli/acycle@dcba4279168745b563e0535b954297023dd62fc7 code/seriesanalysis/minirho.m:L12-L20
if nargin < 6
    genplot =0;
    if nargin < 5
        linlog = 2;
        if nargin < 4
            error('Error. Too few input arguments.')
        end
    end
end
%% End copied source
values = struct();
if exist('s0', 'var'), values.s0 = s0; end
if exist('fn', 'var'), values.fn = fn; end
if exist('ft', 'var'), values.ft = ft; end
if exist('pxxsmooth', 'var'), values.pxxsmooth = pxxsmooth; end
if exist('linlog', 'var'), values.linlog = linlog; end
if exist('genplot', 'var'), values.genplot = genplot; end
end
