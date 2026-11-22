function [retval, id] = plotter(params, id)
% AR1Prewhitening.plotter parameters: datp xlabel_text ylabel_text.
% Source: https://github.com/mingsongli/acycle/blob/b52ea9f510f3be00bde9a0238b9898a1e2315b74/code/guicode/prewhitenGUI.m#L287
if nargin < 2, id = []; end
[retval, id] = aclog.invoke('AR1Prewhitening-v1.0/plotter', params, id, @execute);
end

function r = execute(p)
datp = p.datp;
xlabel_text = p.xlabel_text;
ylabel_text = p.ylabel_text;
%% Copied from mingsongli/acycle@b52ea9f510f3be00bde9a0238b9898a1e2315b74 code/guicode/prewhitenGUI.m:L287-L288
figure;
plot(datp(:,1),datp(:,2),'k','LineWidth',1);
%% End copied source
xlabel(xlabel_text); ylabel(ylabel_text);
%% Copied from mingsongli/acycle@b52ea9f510f3be00bde9a0238b9898a1e2315b74 code/guicode/prewhitenGUI.m:L293-L293
xlim([min(datp(:,1)) max(datp(:,1))])
%% End copied source
r=[];
end
