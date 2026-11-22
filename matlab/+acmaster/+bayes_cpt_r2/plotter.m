function [retval,id] = plotter(params,id)
% bayes_cpt_r2.plotter parameters: R_2_all.
% Source: https://github.com/mingsongli/acycle/blob/dcba4279168745b563e0535b954297023dd62fc7/code/package/bayes_changepoint/bayes_cpt_r2.m
if nargin < 2, id = []; end
[retval,id] = accompat.masterInvoke('bayes_cpt_r2-v3.1.1+dcba427/plotter',params,id,@execute);
end

function r = execute(p)
R_2_all = p.R_2_all;
%% Copied from mingsongli/acycle@dcba4279168745b563e0535b954297023dd62fc7 code/package/bayes_changepoint/bayes_cpt_r2.m:L266-L266
figure; plot(R_2_all(:,1),R_2_all(:,2),'r-o')
%% End copied source
r=[];
end
