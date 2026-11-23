function value = acMenuRedNoise(engine,p)
% Both upstream redmark files reseed from the wall clock inside the kernel.
% Supply the recorded seed to the same legacy normal generator and use Li's filter.
seed=p.seed;
validateattributes(seed,{'numeric'},{'scalar','real','finite','nonnegative','<=',2^32-1});
previous=rng;
guard=onCleanup(@()rng(previous)); %#ok<NASGU>
randn('state',double(seed)); %#ok<RAND>
if strcmp(engine.package,'redmark')
    value=struct('yred',acMenuRedSamples(p.alfa,p.n));
elseif strcmp(engine.revision,'guide')
    x=p.x; std=p.std; mean=p.mean; alpha=p.alpha;
    redmark=@acMenuRedSamples;
%% Copied from mingsongli/acycle@b52ea9f510f3be00bde9a0238b9898a1e2315b74 code/guicode/linegenerator.m:L462-L462
    y = std * zscore(redmark(alpha,length(x))) + mean;
%% End copied source
    value=struct('x',x,'y',y);
else
    x=p.x(:); mu=p.mu; sigma=p.sigma; alpha=p.alpha;
    localRedNoise=@acMenuRedSamples;
%% Copied from mingsongli/acycle@dcba4279168745b563e0535b954297023dd62fc7 code/guicode/linegenerator.m:L383-L383
                    y = sigma * zscore(localRedNoise(alpha,length(x))) + mu;
%% End copied source
    value=[x,y];
end
end

function yred = acMenuRedSamples(alfa,n)
% Also upstream GUIDE code/seriesanalysis/redmark.m:L22.
%% Copied from mingsongli/acycle@dcba4279168745b563e0535b954297023dd62fc7 code/seriesanalysis/redmark.m:L23-L23
yred=filter(1,[1;-alfa],randn(n,1));
%% End copied source
end
