function acycle_batch(folder, acycleRoot)
ids = string(jsondecode(fileread(fullfile(folder,'cases.json'))));
for k=1:numel(ids)
    parent = fullfile(folder,ids(k));
    acycle_candidate(fullfile(parent,'request'),fullfile(parent,'submission'),acycleRoot);
end
end
