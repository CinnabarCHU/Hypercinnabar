function out = liveEvents(action,value,windowId)
% Sequence numbers are local to one shared desktop. Retain recent committed events.
persistent cursor history
if isempty(cursor), cursor = 0; history = {}; end
if strcmp(action,'append')
    cursor = cursor+1;
    value.cursor = cursor;
    history{end+1} = value;
    if numel(history)>256, history(1) = []; end
    out = cursor;
else
    first = cursor+1;
    if ~isempty(history), first = history{1}.cursor; end
    selected = cellfun(@(e)e.cursor>value && (isempty(windowId) || strcmp(e.window_id,windowId)),history);
    out = struct('status','ok','cursor',cursor,'resync',value<first-1 || value>cursor, ...
        'events',{history(selected)});
end
end
