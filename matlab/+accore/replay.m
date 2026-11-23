function [value,newId] = replay(id,role)
% The recorded menu executor uses the exact operation, arguments and initial RNG.
if nargin == 2
    session = accore.io('load',id);
    if strcmp(role,'workflow'), id = session.id; else, id = session.ids.(role); end
end
[value,newId] = aclog.replay(id);
end
