function event(owner,name,object,data)
% UI objects stay in the desktop. Scientific stage calls have independent journals.
if strcmp(func2str(owner),'AC') && isgraphics(object,'uimenu') && endsWith(name,'_Callback')
    tag = object.Tag;
    catalog = accore.register();
    if ismember(tag,{catalog.menus.tag})
        menu = accore.register(tag);
        if isempty(menu.entry), return; end
        accore.dispatchMenu(tag,@()owner(name,object,data,acgui.state(object)));
        return
    end
end
owner(name,object,data,acgui.state(object));
end
