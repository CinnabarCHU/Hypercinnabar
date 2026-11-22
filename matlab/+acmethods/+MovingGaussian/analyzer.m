function [retval, id] = analyzer(params, id)
% MovingGaussian.analyzer parameters: data window.
% Source: https://github.com/mingsongli/acycle/blob/b52ea9f510f3be00bde9a0238b9898a1e2315b74/code/guicode/AC.m#L7726
if nargin < 2, id = []; end
[retval, id] = aclog.invoke('MovingGaussian-v1.0/analyzer', params, id, @execute);
end

function r = execute(p)
data = p.data;
window = p.window;
data(:,2) = smoothdata(data(:,2),'gaussian',window);
r = struct();
r.data = data;
end
