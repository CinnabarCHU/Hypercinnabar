function [retval, id] = analyzer(params, id)
% PCA.analyzer parameters: data_new depthtime.
% Source: https://github.com/mingsongli/acycle/blob/b52ea9f510f3be00bde9a0238b9898a1e2315b74/code/guicode/AC.m#L6936
if nargin < 2, id = []; end
[retval, id] = aclog.invoke('PCA-v1.0/analyzer', params, id, @execute);
end

function r = execute(p)
data_new = p.data_new;
depthtime = p.depthtime;
%% Copied from mingsongli/acycle@b52ea9f510f3be00bde9a0238b9898a1e2315b74 code/guicode/AC.m:L6936-L6950
        if depthtime == 1
            data_new2 = data_new(:,2:end);
        else
            data_new2 = data_new;
        end

        % pca
        [coeff, pc, latent, tsquared, explained, mu] = pca(data_new2); 
        if depthtime == 1
            pcn = [data_new(:,1),pc];
            disp('>>    col#1: depth/time; col#2: PC1; col#3: PC2 ...')
        else
            pcn = pc;
            disp('>>    col#1: PC1; col#2: PC2; col#3: PC3 ...')
        end
%% End copied source
r = struct();
r.coeff = coeff;
r.pc = pc;
r.latent = latent;
r.tsquared = tsquared;
r.explained = explained;
r.mu = mu;
r.pcn = pcn;
end
