function [retval, id] = analyzer(params, id)
% SeriesGenerator.analyzer parameters: x kind and explicit parameters for the selected kind.
% Source: https://github.com/mingsongli/acycle/blob/b52ea9f510f3be00bde9a0238b9898a1e2315b74/code/guicode/linegenerator.m#L414
if nargin < 2, id = []; end
[retval, id] = aclog.invoke('SeriesGenerator-v1.0/analyzer', params, id, @execute);
end

function r = execute(p)
x = p.x;
kind = p.kind;
switch kind
case 'polynomial'
    handles.b=p.intercept;
    a=p.coefficients;
    handles.poly=numel(a);
    if handles.poly>8, error('Acycle:Generator:Degree','Maximum polynomial degree is 8.'); end
    a(end+1:8)=0;
    a1=a(1); a2=a(2); a3=a(3); a4=a(4); a5=a(5); a6=a(6); a7=a(7); a8=a(8);
%% Copied from mingsongli/acycle@b52ea9f510f3be00bde9a0238b9898a1e2315b74 code/guicode/linegenerator.m:L414-L414
    y = handles.b + a1 * x + a2*x.^2+ a3*x.^3+ a4*x.^4+ a5*x.^5+ a6*x.^6+ a7*x.^7+ a8*x.^8;
%% End copied source
case 'sinusoid'
    A=p.amplitude; T=p.period; Ph=p.phase; B=p.offset;
%% Copied from mingsongli/acycle@b52ea9f510f3be00bde9a0238b9898a1e2315b74 code/guicode/linegenerator.m:L430-L430
    y = A * sin(2*pi/T*x + Ph) + B;
%% End copied source
case 'gaussian'
    std=p.std; mean=p.mean;
%% Copied from mingsongli/acycle@b52ea9f510f3be00bde9a0238b9898a1e2315b74 code/guicode/linegenerator.m:L445-L445
        y = std * randn(length(x),1) + mean;
%% End copied source
case 'uniform'
    std=p.std; mean=p.mean;
%% Copied from mingsongli/acycle@b52ea9f510f3be00bde9a0238b9898a1e2315b74 code/guicode/linegenerator.m:L447-L447
        y = std * zscore(rand(length(x),1)) + mean;
%% End copied source
case 'red'
    std=p.std; mean=p.mean; alpha=p.alpha;
%% Copied from mingsongli/acycle@b52ea9f510f3be00bde9a0238b9898a1e2315b74 code/guicode/linegenerator.m:L462-L462
    y = std * zscore(redmark(alpha,length(x))) + mean;
%% End copied source
otherwise
    error('Acycle:Generator:Kind','Unknown signal or noise model.');
end
r = struct();
r.x = x;
r.y = y;
end
