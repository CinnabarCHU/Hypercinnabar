function dispatchMenu(tag,action)
% Track live desktop commands separately from reproducible numerical invocations.
[menu,engine] = accore.register(tag);
id = acMenuNewId();
logger(id,'ui',struct('tag',menu.tag,'operation',engine.operation,'workspace',accore.io('workspace')));
try
    action();
catch err
    logger(id,'error',struct('identifier',err.identifier,'message',err.message));
    logger(id,'fin',struct('status','cancelled'));
    rethrow(err)
end
logger(id,'fin',struct('status','done'));
end
