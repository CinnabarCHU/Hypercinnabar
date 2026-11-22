function [retval, id] = helper(params, id)
% SeriesGenerator.helper parameters: data(optional).
% Source: https://github.com/mingsongli/acycle/blob/b52ea9f510f3be00bde9a0238b9898a1e2315b74/code/guicode/linegenerator.m#L193
% Source: https://github.com/mingsongli/acycle/blob/b52ea9f510f3be00bde9a0238b9898a1e2315b74/code/guicode/linegenerator.m#L239
% Source: https://github.com/mingsongli/acycle/blob/b52ea9f510f3be00bde9a0238b9898a1e2315b74/code/guicode/linegenerator.fig
if nargin < 2, id = []; end
[retval, id] = aclog.invoke('SeriesGenerator-v1.0/helper', params, id, @execute);
end

function r = execute(p)
% Guide text controls edit1..edit20 supply the scalar settings; an explicit data column fixes x.
if isfield(p,'data') && ~isempty(p.data)
    data=p.data;
%% Copied from mingsongli/acycle@b52ea9f510f3be00bde9a0238b9898a1e2315b74 code/guicode/linegenerator.m:L193-L193
    x = data(:,1); % read first column
%% End copied source
else
    handles=struct('x1',0,'x2',1000,'x_step',1);
%% Copied from mingsongli/acycle@b52ea9f510f3be00bde9a0238b9898a1e2315b74 code/guicode/linegenerator.m:L208-L209
    x = handles.x1 : handles.x_step : handles.x2;
    x = x';
%% End copied source
end
r=struct('x',x,'kind','polynomial','intercept',1,'coefficients',[], ...
    'amplitude',1,'period',100,'phase',0,'offset',0,'mean',0,'std',1,'alpha',.5);
end
