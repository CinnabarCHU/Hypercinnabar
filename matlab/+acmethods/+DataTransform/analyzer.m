function [retval, id] = analyzer(params, id)
% DataTransform.analyzer parameters: data checkid j.
% Source: https://github.com/mingsongli/acycle/blob/b52ea9f510f3be00bde9a0238b9898a1e2315b74/code/guicode/datatransformationsGUI.m#L525
if nargin < 2, id = []; end
[retval, id] = aclog.invoke('DataTransform-v1.0/analyzer', params, id, @execute);
end

function r = execute(p)
data = p.data;
checkid = p.checkid;
j = p.j;
if ~ismember(j,[1,2,5,7:13,21:26]), error('Acycle:Transform:Method','Unknown transformation.'); end
%% Copied from mingsongli/acycle@b52ea9f510f3be00bde9a0238b9898a1e2315b74 code/guicode/datatransformationsGUI.m:L525-L532
            dat = data(:,checkid);
            yt = data;
            lambda = [];
            if j == 1  % Zscore
                dat = zscore(dat);
                fnt = 'standardized';
            end
            if j == 2 % normalize
%% End copied source
edit1=p.edit1; edit2=p.edit2;
%% Copied from mingsongli/acycle@b52ea9f510f3be00bde9a0238b9898a1e2315b74 code/guicode/datatransformationsGUI.m:L533-L538
                min_val = min(edit1, edit2);
                max_val = max(edit1, edit2);
                dat = (dat - min(dat)) ./ (max(dat) - min(dat)) * (max_val - min_val) + min_val;
                fnt = ['norm-',num2str(min_val), '-',num2str(max_val)];
            end
            if j == 7 % logB
%% End copied source
edit3=p.edit3;
%% Copied from mingsongli/acycle@b52ea9f510f3be00bde9a0238b9898a1e2315b74 code/guicode/datatransformationsGUI.m:L540-L546
                if edit3 == 10
                    dat = log10(dat);
                elseif edit3 == 2
                    dat = log2(dat);
                else
                    dat = log10(dat)./log10(edit3);
                end
%% End copied source
%% Copied from mingsongli/acycle@b52ea9f510f3be00bde9a0238b9898a1e2315b74 code/guicode/datatransformationsGUI.m:L548-L557
            end
            if j == 8 % ln
                dat = log(dat);
                fnt = 'ln';
            end
            if j == 9 % exp(x)
                dat = exp(dat);
                fnt = 'exp';
            end
            if j == 10 % n^x
%% End copied source
edit4=p.edit4;
%% Copied from mingsongli/acycle@b52ea9f510f3be00bde9a0238b9898a1e2315b74 code/guicode/datatransformationsGUI.m:L559-L559
                dat = edit4.^dat;
%% End copied source
%% Copied from mingsongli/acycle@b52ea9f510f3be00bde9a0238b9898a1e2315b74 code/guicode/datatransformationsGUI.m:L561-L576
            end
            if j == 5 % 1/x
                dat = 1./dat;
                fnt = 'reciprocal';
            end

            if j == 11 % sqrt
                dat = sqrt(dat);
                fnt = 'sqrt';
            end
            if j == 12 % cube
                dat = nthroot(dat,3);
                fnt = 'cube';
            end
            if j == 13 % box-cox
                if any(dat <= 0)
%% End copied source
%% Copied from mingsongli/acycle@b52ea9f510f3be00bde9a0238b9898a1e2315b74 code/guicode/datatransformationsGUI.m:L578-L606
                    dat = dat + abs(min(dat)) + eps;
                end
                [dat, lambda] = boxcox(dat);
                fnt = 'box-cox';
            end
            if j == 21 % sine
                dat = sin(dat);
                fnt = 'sin';
            end
            if j == 22 % cos
                dat = cos(dat);
                fnt = 'cos';
            end
            if j == 23 % sine
                dat = tan(dat);
                fnt = 'tan';
            end
            if j == 24 % sine
                dat = cot(dat);
                fnt = 'cot';
            end
            if j == 25 % sine
                dat = sec(dat);
                fnt = 'sec';
            end
            if j == 26 % sine
                dat = csc(dat);
                fnt = 'csc';
            end
%% End copied source
%% Copied from mingsongli/acycle@b52ea9f510f3be00bde9a0238b9898a1e2315b74 code/guicode/datatransformationsGUI.m:L609-L611
            for k = 1: length(checkid)
                yt(:, checkid(k)) = dat(:,k);
            end
%% End copied source
r = struct();
r.yt = yt;
r.lambda = lambda;
end
