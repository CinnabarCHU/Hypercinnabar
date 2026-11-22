function [retval, id] = plotter(params, id)
% bayes_cpt_r2.plotter parameters: R_2_all.
% Source: https://github.com/mingsongli/acycle/blob/b52ea9f510f3be00bde9a0238b9898a1e2315b74/code/package/bayes_changepoint/bayes_cpt_r2.m#L266
if nargin < 2, id = []; end
[retval, id] = aclog.invoke('bayes_cpt_r2-v1.0/plotter', params, id, @execute);
end

function r = execute(p)
R_2_all = p.R_2_all;
%% Copied from mingsongli/acycle@b52ea9f510f3be00bde9a0238b9898a1e2315b74 code/package/bayes_changepoint/bayes_cpt_r2.m:L266-L266
figure; plot(R_2_all(:,1),R_2_all(:,2),'r-o')
%% End copied source
r=[];
end
