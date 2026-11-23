function scopeMaster(before)
% A master window can outlive its launch. Its deferred callbacks need the same
% revision's paths each time, including when they create another window.
figs = findall(groot,'Type','figure');
for f = reshape(figs(~ismember(figs,before)),1,[])
    if isappdata(f,'AcycleMasterScope'), continue; end
    setappdata(f,'AcycleMasterScope',true);
    objects = findall(f);
    for k = 1:numel(objects)
        obj = objects(k);
        keys = properties(obj);
        keys = keys(endsWith(keys,'Fcn') | endsWith(keys,'Callback'));
        for j = 1:numel(keys)
            key = keys{j};
            cb = obj.(key);
            if isa(cb,'function_handle') || (iscell(cb) && ~isempty(cb) && isa(cb{1},'function_handle'))
                obj.(key) = @(o,e)invoke(cb,o,e);
            end
        end
    end
end
end

function invoke(cb,obj,event)
guard = accompat.masterPath(); %#ok<NASGU>
before = findall(groot,'Type','figure');
if iscell(cb), feval(cb{1},obj,event,cb{2:end}); else, cb(obj,event); end
acgui.scopeMaster(before);
end
