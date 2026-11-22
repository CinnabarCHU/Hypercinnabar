function guard = swaWorkspace(names)
% Isolate the base-workspace assignments and text reports of the pinned SWA.
previousFolder = pwd;
folder = tempname;
mkdir(folder);
values = cell(size(names));
present = false(size(names));
for i = 1:numel(names)
    present(i) = evalin('base',['exist(''',names{i},''',''var'') ~= 0']);
    if present(i), values{i} = evalin('base',names{i}); end
end
priorGlobals = who('global');
wasGlobal = any(strcmp(priorGlobals,'unit2fid'));
global unit2fid
oldUnit = unit2fid;
guard = onCleanup(@() restore(previousFolder,folder,names,present,values,wasGlobal,oldUnit));
cd(folder);
end

function restore(previousFolder,folder,names,present,values,wasGlobal,oldUnit)
cd(previousFolder);
for i = 1:numel(names)
    if present(i)
        assignin('base',names{i},values{i});
    else
        evalin('base',['clear ',names{i}]);
    end
end
if wasGlobal
    global unit2fid
    unit2fid = oldUnit;
else
    clear global unit2fid
end
rmdir(folder,'s');
end
