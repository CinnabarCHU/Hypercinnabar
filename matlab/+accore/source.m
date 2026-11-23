function source(id,parents)
% Attach provenance before the first event so fin remains the terminal event.
aclog.store(aclog.interfaceId(id,true),'source',parents);
end
