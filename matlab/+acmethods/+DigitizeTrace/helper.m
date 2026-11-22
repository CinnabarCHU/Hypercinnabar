function [retval, id] = helper(params, id)
% DigitizeTrace.helper parameters: image seeds.
% Source: https://github.com/mingsongli/acycle/blob/b52ea9f510f3be00bde9a0238b9898a1e2315b74/code/guicode/DataExtractML.m#L79
% Source: https://github.com/mingsongli/acycle/blob/b52ea9f510f3be00bde9a0238b9898a1e2315b74/code/guicode/DataExtractML.m#L756
if nargin < 2, id = []; end
[retval, id] = aclog.invoke('DigitizeTrace-v1.0/helper', params, id, @execute);
end

function r = execute(p)
r=p;
r.srsh=10;
r.shreshn=255/2;
% Select the historical functions only when both signatures are present.
r.engine='ecocotrackn';
if ~isempty(which('getPKS')) && ~isempty(which('trackline')) && nargin('getPKS')~=1
    r.engine='trackline';
end
end
