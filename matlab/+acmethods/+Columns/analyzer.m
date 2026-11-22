function [retval, id] = analyzer(params, id)
% Columns.analyzer parameters: data c1 c2.
% Source: https://github.com/mingsongli/acycle/blob/b52ea9f510f3be00bde9a0238b9898a1e2315b74/code/guicode/AC.m#L6790
if nargin < 2, id = []; end
[retval, id] = aclog.invoke('Columns-v1.0/analyzer', params, id, @execute);
end

function r = execute(p)
data = p.data;
c1 = p.c1;
c2 = p.c2;
%% Copied from mingsongli/acycle@b52ea9f510f3be00bde9a0238b9898a1e2315b74 code/guicode/AC.m:L6790-L6790
                data = data(~any(isnan(data),2),:);
%% End copied source
%% Copied from mingsongli/acycle@b52ea9f510f3be00bde9a0238b9898a1e2315b74 code/guicode/AC.m:L6792-L6793
                    data_new(:,1) = data(:,c1);
                    data_new(:,2:2+length(c2)-1) = data(:,c2);
%% End copied source
r = struct();
r.data_new = data_new;
end
