function [value,status] = acMenuNative(menu,engine,~)
% Address a live, code-defined desktop. Keep interactive commands out of headless runs.
figs = findall(groot,'Type','figure');
match = arrayfun(@(f)isequal(getappdata(f,'AcycleWindowName'),'AC'),figs);
fig = figs(match);
if ~isscalar(fig), error('Acycle:Desktop:Session','Open the Acycle desktop for %s.',menu.tag); end
obj = findall(fig,'Tag',menu.tag);
if ~isscalar(obj) || ~strcmp(obj.Visible,'on') || ~strcmp(obj.Enable,'on')
    error('Acycle:Desktop:Unavailable','Control %s is hidden or unavailable.',menu.tag);
end
if strcmp(engine.revision,'master')
    acgui.masterMenu(fig,menu.tag);
else
    cb = obj.Callback;
    if ~isa(cb,'function_handle'), error('Acycle:Desktop:Callback','No action for %s.',menu.tag); end
    cb(obj,[]);
end
value = struct('tag',menu.tag,'revision',engine.revision);
status = 'done';
end
