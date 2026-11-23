function meta = liveMark(fig,feature,status,kind,detail)
% Advance only on a committed UI change. Figure handles never leave MATLAB.
meta = getappdata(fig,'AcycleLive');
if isempty(meta)
    meta = struct('window_id',char(java.util.UUID.randomUUID()),'feature',feature,'revision',0,'status',status);
    listener = addlistener(fig,'ObjectBeingDestroyed',@destroyed);
    setappdata(fig,'AcycleLiveListener',listener);
end
meta.status = status; meta.revision = meta.revision+1;
setappdata(fig,'AcycleLive',meta);
announce(meta,kind,detail);
end

function announce(meta,kind,detail)
acgui.liveEvents('append',struct('window_id',meta.window_id,'feature',meta.feature, ...
    'revision',meta.revision,'kind',kind,'detail',detail));
end

function destroyed(fig,~)
meta = getappdata(fig,'AcycleLive');
if isempty(meta), return; end
meta.revision = meta.revision+1;
if strcmp(meta.status,'awaiting_input'), kind = 'cancelled'; else, kind = 'closed'; end
announce(meta,kind,struct());
end
