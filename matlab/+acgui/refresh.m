function refresh(h,folder)
entries = accore.io('list',folder,h.val1);
folder = accore.io('chdir',folder);
names = cell(numel(entries),1);
for k = 1:numel(entries)
    names{k} = entries(k).name;
    if entries(k).isdir, names{k} = ['<HTML><FONT color="blue">',names{k},'</FONT></HTML>']; end
end
set(h.edit_acfigmain_dir,'String',folder);
set(h.listbox_acmain,'String',names,'Value',[]);
end
