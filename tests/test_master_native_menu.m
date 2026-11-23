function test_master_native_menu()
% Reconstruct the original 3.1.1 menu objects and dispatch the real Settings callback.
root = fileparts(fileparts(mfilename('fullpath')));
setup_migration;
guard = accompat.masterPath(); %#ok<NASGU>
[fig,handles] = AC('AC_buildCodeUI');
cleanup = onCleanup(@() closeWindows(fig)); %#ok<NASGU>
guidata(fig,handles);
rows = readtable(fullfile(root,'migration','master','menus.tsv'),'Delimiter','tab', ...
    'FileType','text','TextType','string','VariableNamingRule','preserve');
for i = 1:height(rows)
    item = findall(fig,'Type','uimenu','Tag',char(rows.tag(i)));
    if rows.master_initial(i) == "absent"
        assert(isempty(item));
    else
        assert(numel(item)==1,'Expected one instance of %s.',rows.tag(i));
        hidden = false; parent = item;
        while isgraphics(parent,'uimenu')
            hidden = hidden || strcmp(get(parent,'Visible'),'off');
            parent = get(parent,'Parent');
        end
        assert(hidden == (rows.master_initial(i)=="hidden"),'%s visibility',rows.tag(i));
    end
end
h=acMenuSettings_helper('id',acMenuNewId());
r=acMenuSettings_plotter(h.plt,'params',h.params,'id',acMenuNewId());
assert(strcmp(r.tag,'menu_settings') && ~isempty(findall(groot,'Tag','AcycleSettingsFigure')));
try
    acmaster.Desktop.plotter(struct('tag','menu_opendir'));
    error('test:ExpectedFailure','Hidden Open Directory must stay hidden.');
catch err
    assert(strcmp(err.identifier,'Acycle:Desktop:Unavailable'));
end
fprintf('Verified the 3.1.1 main-window menu tags, visibility and Settings callback.\n');
end

function closeWindows(fig)
delete(findall(groot,'Tag','AcycleSettingsFigure'));
if isgraphics(fig), delete(fig); end
end
