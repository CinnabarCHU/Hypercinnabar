function [retval, id] = helper(params, id)
% Detrending.helper parameters: data.
% Source: https://github.com/mingsongli/acycle/blob/b52ea9f510f3be00bde9a0238b9898a1e2315b74/code/guicode/prewhiten.m#L159
% Source: https://github.com/mingsongli/acycle/blob/b52ea9f510f3be00bde9a0238b9898a1e2315b74/code/guicode/prewhiten.m#L178
if nargin < 2, id = []; end
[retval, id] = aclog.invoke('Detrending-v1.0/helper', params, id, @execute);
end

function r = execute(p)
data=p.data; xmin=min(data(:,1)); xmax=max(data(:,1));
%% Copied from mingsongli/acycle@b52ea9f510f3be00bde9a0238b9898a1e2315b74 code/guicode/prewhiten.m:L162-L163
handles.smooth_win = 0.35;  % windows for smooth 
handles.prewhiten_win = (xmax-xmin) * handles.smooth_win;
%% End copied source
r=struct('data',data,'method','raw','degree',3,'span',handles.smooth_win);
r.unit='';
end
