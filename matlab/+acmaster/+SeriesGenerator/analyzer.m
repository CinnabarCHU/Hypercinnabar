function [retval,id] = analyzer(params,id)
% SeriesGenerator.analyzer parameters: x kind; polynomial intercept coefficients; harmonic amplitude period phase offset; white distribution mu sigma; red mu sigma alpha.
% Source: https://github.com/mingsongli/acycle/blob/dcba4279168745b563e0535b954297023dd62fc7/code/guicode/linegenerator.m
if nargin < 2, id = []; end
[retval,id] = accompat.masterInvoke('SeriesGenerator-v3.1.1+dcba427/analyzer',params,id,@execute);
end

function r = execute(p)
x=p.x(:);
switch p.kind
case 'polynomial'
    b=p.intercept; c=p.coefficients(:)'; deg=numel(c);
    if deg>8, error('Acycle:Series:Degree','Maximum polynomial degree is eight.'); end
    c(deg+1:8)=0;
%% Copied from mingsongli/acycle@dcba4279168745b563e0535b954297023dd62fc7 code/guicode/linegenerator.m:L360-L361
                    c((deg+1):end) = 0;
                    y = b + c(1)*x + c(2)*x.^2 + c(3)*x.^3 + c(4)*x.^4 + c(5)*x.^5 + c(6)*x.^6 + c(7)*x.^7 + c(8)*x.^8;
%% End copied source
case 'harmonic'
    A=p.amplitude; T=p.period; Ph=p.phase; B=p.offset;
%% Copied from mingsongli/acycle@dcba4279168745b563e0535b954297023dd62fc7 code/guicode/linegenerator.m:L367-L370
                    if T == 0
                        T = 100;
                    end
                    y = A * sin(2*pi./T.*x + Ph) + B;
%% End copied source
case 'white'
    mu=p.mu; sigma=p.sigma; app.whiteDist=string(validatestring(p.distribution,{'normal','uniform'}));
%% Copied from mingsongli/acycle@dcba4279168745b563e0535b954297023dd62fc7 code/guicode/linegenerator.m:L374-L378
                    if app.whiteDist == "normal"
                        y = sigma * randn(length(x),1) + mu;
                    else
                        y = sigma * zscore(rand(length(x),1)) + mu;
                    end
%% End copied source
case 'red'
    mu=p.mu; sigma=p.sigma; alpha=p.alpha;
%% Copied from mingsongli/acycle@dcba4279168745b563e0535b954297023dd62fc7 code/guicode/linegenerator.m:L383-L383
                    y = sigma * zscore(localRedNoise(alpha,length(x))) + mu;
%% End copied source
otherwise, error('Acycle:Series:Mode','Unknown generator.');
end
r=[x,y];
end

%% Copied from mingsongli/acycle@dcba4279168745b563e0535b954297023dd62fc7 code/guicode/linegenerator.m:L549-L556
function y = localRedNoise(alpha,n)
if exist('redmark','file') == 2
    y = redmark(alpha,n);
else
    rng('shuffle');
    y = filter(1,[1;-alpha],randn(n,1));
end
end
%% End copied source
