function [value,status] = acMenuNative(menu,engine,journal)
% Deliver a menu command to the pinned desktop that owns its control.
if strcmp(engine.operation,'Desktop')
    [value,status]=acMenuOriginal(engine,'plotter',struct('tag',menu.tag),journal);
    return
end
master=strcmp(engine.revision,'master');
if master, guard=accompat.masterPath(); else, guard=acMenuGuidePath(); end %#ok<NASGU>
figs=findall(groot,'Type','figure','Tag','acfigmain');
matches=false(size(figs));
for k=1:numel(figs)
    matches(k)=master == ~isempty(findall(figs(k),'Type','uimenu','Tag','menu_bispectral'));
end
figs=figs(matches);
if numel(figs)~=1
    error('Acycle:Desktop:Session','Open one %s Acycle main window for %s.',engine.revision,menu.tag);
end
item=findall(figs,'Tag',menu.tag);
if numel(item)~=1, error('Acycle:Desktop:Menu','Cannot resolve control %s.',menu.tag); end
obj=item;
while isgraphics(obj,'uimenu') || isgraphics(obj,'uicontrol')
    if strcmp(obj.Visible,'off') || strcmp(obj.Enable,'off')
        error('Acycle:Desktop:Unavailable','The running desktop has disabled or hidden %s.',menu.tag);
    end
    obj=obj.Parent;
end
cb=get(item,'Callback');
if isa(cb,'function_handle')
    cb(item,[]);
elseif iscell(cb) && ~isempty(cb) && isa(cb{1},'function_handle')
    feval(cb{1},item,[],cb{2:end});
elseif ~master && (ischar(cb) || isstring(cb))
    % GUIDE FIGs may store a serialized AC('..._Callback',...) rather than a handle.
    token=regexp(char(cb),'^\s*AC\(\s*''(\w+_Callback)''','tokens','once');
    if isempty(token) || ~strcmp(token{1},[menu.tag,'_Callback']) || ...
            ~isfile(fullfile(fileparts(which('AC')),'AC.fig'))
        error('Acycle:Desktop:Callback','Cannot verify the GUIDE callback for %s.',menu.tag);
    end
    AC(token{1},item,[],guidata(item));
else
    error('Acycle:Desktop:Heading','No executable callback for %s.',menu.tag);
end
value=struct('tag',menu.tag);
status='done';
end
