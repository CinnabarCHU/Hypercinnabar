function [retval, id] = analyzer(params, id)
% rhoAR1ML.analyzer parameters: datax.
% Source: https://github.com/mingsongli/acycle/blob/b52ea9f510f3be00bde9a0238b9898a1e2315b74/code/seriesanalysis/rhoAR1ML.m#L25
if nargin < 2, id = []; end
[retval, id] = aclog.invoke('rhoAR1ML-v1.0/analyzer', params, id, @execute);
end

function r = execute(p)
[rho] = rhoAR1ML(p.datax);
r = struct();
r.rho = rho;
end
