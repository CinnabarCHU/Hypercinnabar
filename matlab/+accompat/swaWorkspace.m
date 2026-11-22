function guard = swaWorkspace(names)
% SWA writes named base variables and hard-coded filenames during computation.
previousFolder = pwd;
folder = tempname;
mkdir(folder);
values = cell(size(names));
present = false(size(names));
for i = 1:numel(names)
    present(i) = evalin('base',['exist(''',names{i},''',''var'') ~= 0']);
    if present(i), values{i}=evalin('base',names{i}); end
end
guard = onCleanup(@restore);
cd(folder);
    function restore
        cd(previousFolder);
        for k = 1:numel(names)
            if present(k)
                assignin('base',names{k},values{k});
            else
                evalin('base',['clear ',names{k}]);
            end
        end
        rmdir(folder,'s');
    end
end
