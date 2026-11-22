function [retval,id] = helper(params,id)
% eccpeaks.helper parameters: X ecc eci norbit corrcoef ci sh_norb n dim a.
% Source: https://github.com/mingsongli/acycle/blob/dcba4279168745b563e0535b954297023dd62fc7/code/corrcoef/eccpeaks.m
if nargin < 2, id = []; end
[retval,id] = accompat.masterInvoke('eccpeaks-v3.1.1+dcba427/helper',params,id,@execute);
end

function r = execute(p)
r = aclog.defaults(p, {'X', 'ecc', 'eci', 'norbit', 'corrcoef', 'ci', 'sh_norb', 'n', 'dim', 'a'}, 3, @legacyDefaults);
end

function values = legacyDefaults(X, ecc, eci, norbit, corrcoef, ci, sh_norb, n, dim, a)
%% Copied from mingsongli/acycle@dcba4279168745b563e0535b954297023dd62fc7 code/corrcoef/eccpeaks.m:L17-L40
if nargin > 10
    error('Too many input arguments')
end
if nargin < 10
    a = 0;
    if nargin < 9
        dim =1;
        if nargin < 8
            n = 1;
            if nargin < 7
                sh_norb = 3;
                if nargin < 6
                    ci = 5;
                    if nargin < 5
                        corrcoef = 0.3;
                        if nargin < 4
                            error('Too few input arguments')
                        end
                    end
                end
            end
        end
    end
end
%% End copied source
values = struct();
if exist('X', 'var'), values.X = X; end
if exist('ecc', 'var'), values.ecc = ecc; end
if exist('eci', 'var'), values.eci = eci; end
if exist('norbit', 'var'), values.norbit = norbit; end
if exist('corrcoef', 'var'), values.corrcoef = corrcoef; end
if exist('ci', 'var'), values.ci = ci; end
if exist('sh_norb', 'var'), values.sh_norb = sh_norb; end
if exist('n', 'var'), values.n = n; end
if exist('dim', 'var'), values.dim = dim; end
if exist('a', 'var'), values.a = a; end
end
