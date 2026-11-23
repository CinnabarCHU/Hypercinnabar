function test_menu_export()
% Load only two exported menu entries, run both snapshots and replay in isolation.
folder=fullfile(getenv('RUNNER_TEMP'),'acycle-menu-methods');
oldPath=path; oldDir=pwd; cleanup=onCleanup(@()acMenuRestoreTestPath(oldDir,oldPath)); %#ok<NASGU>
cd(folder); restoredefaultpath; setup_method;
cat=acMenuCatalog(); assert(numel(cat.menus)==2 && isempty(which('acMenuPower_helper')));
for selector={'SeriesSound','SeriesSound_legacy'}
    h=acMenuSound_helper(struct('operation',selector{1},'data',[1 10;2 20]),'id',acMenuNewId());
    id=acMenuNewId(); r=acMenuSound_analyzer(h.params,id);
    assert(isequaln(r,aclog.replay(id)) && r.Fs==8192);
end
fprintf('Verified both snapshot implementations from an isolated menu export.\n');
end

function acMenuRestoreTestPath(folder,previous)
cd(folder); path(previous);
end
