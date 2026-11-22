function [retval, id] = analyzer(params, id)
% SortUnique.analyzer parameters: data datasort dataunique dataempty.
% Source: https://github.com/mingsongli/acycle/blob/b52ea9f510f3be00bde9a0238b9898a1e2315b74/code/guicode/AC.m#L4881
if nargin < 2, id = []; end
[retval, id] = aclog.invoke('SortUnique-v1.0/analyzer', params, id, @execute);
end

function r = execute(p)
data = p.data;
datasort = p.datasort;
dataunique = p.dataunique;
dataempty = p.dataempty;
%% Copied from mingsongli/acycle@b52ea9f510f3be00bde9a0238b9898a1e2315b74 code/guicode/AC.m:L4881-L4883
                            data = data(~any(isnan(data),2),:); % remove NaN values
                            if datasort == 1
                                data = sortrows(data);
%% End copied source
%% Copied from mingsongli/acycle@b52ea9f510f3be00bde9a0238b9898a1e2315b74 code/guicode/AC.m:L4885-L4887
                            end
                            if dataunique == 1
                                data=findduplicate(data);
%% End copied source
%% Copied from mingsongli/acycle@b52ea9f510f3be00bde9a0238b9898a1e2315b74 code/guicode/AC.m:L4889-L4889
                            end
%% End copied source
%% Copied from mingsongli/acycle@b52ea9f510f3be00bde9a0238b9898a1e2315b74 code/guicode/AC.m:L4893-L4894
                            if dataempty == 1
                                data(any(isinf(data),2),:) = [];
%% End copied source
end
r = struct();
r.data = data;
end
