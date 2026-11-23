function masterMenu(fig,tag)
h = acgui.state(fig);
guard = accompat.masterPath(); %#ok<NASGU>
before = findall(groot,'Type','figure');
switch tag
case 'menu_bispectral'
    names = cellstr(h.listbox_acmain.String);
    selection = h.listbox_acmain.Value;
    if numel(selection) ~= 1 || selection > numel(names)
        warndlg('Select exactly one data file for Bispectral Analysis.','Bispectral Analysis');
        return
    end
    name = regexprep(names{selection},'<[^>]*>','');
    file = fullfile(accore.io('workspace'),name);
    try
        [h.current_data,message] = bispectralReadDataFile(file);
        if ~isempty(message), warndlg(message,'Bispectral Analysis'); return; end
    catch err
        warndlg(err.message,'Bispectral Analysis'); return
    end
    h.data_name = file;
    acgui.state(fig,h);
    bispectralGUI(h);
case 'menu_settings'
    h.SettingsRestartFcn = @()restart(fig);
    settingsGUI(h);
case 'push_robot'
    AC('push_robot_clbk',findall(fig,'Tag',tag),[],h);
otherwise
    AC('AC_dispatch',[tag,'_Callback'],findall(fig,'Tag',tag),[]);
end
acgui.scopeMaster(before);
end

function restart(fig)
delete(fig);
acgui.desktop();
end
