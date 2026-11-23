function extendDesktop(fig)
% Insert genuinely new master entries without reparenting the original menu tree.
h = acgui.state(fig);
catalog = accore.register();
for k = 1:numel(catalog.menus)
    m = catalog.menus(k);
    if ~isempty(m.guide) || isempty(m.master) || isfield(h,m.tag), continue; end
    segments = strsplit(m.master,' > ');
    parent = find(strcmp({catalog.menus.master},strjoin(segments(1:end-1),' > ')),1);
    if isempty(parent), error('Acycle:GUI:Menu','Missing parent for %s.',m.tag); end
    host = h.(catalog.menus(parent).tag);
    item = uimenu(host,'Label',segments{end},'Tag',m.tag);
    h.(m.tag) = item;
    if strcmp(m.masterVisibility,'hidden'), item.Visible = 'off'; end
    if strcmp(m.tag,'menu_bispectral'), item.Position = h.menu_CSA.Position + 1; end
    if strcmp(m.tag,'menu_settings'), item.Position = 1; end
    if ~isempty(m.entry)
        tag = m.tag;
        item.Callback = @(~,~)accore.dispatchMenu(tag,@()acgui.masterMenu(fig,tag));
    end
end
robot = findall(fig,'Tag','push_robot');
if isscalar(robot)
    original = robot.Callback;
    robot.Callback = @(obj,evt)accore.dispatchMenu('push_robot',@()original(obj,evt));
end
acgui.state(fig,h);
end
