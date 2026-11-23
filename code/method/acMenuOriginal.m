function [value,status] = acMenuOriginal(engine,role,p,journal)
% Use the original versioned entry point with its enclosing public journal.
if ~ismember(role,strsplit(engine.roles))
    error('Acycle:Menu:Role','%s has no %s in the selected snapshot.',engine.operation,role);
end
if strcmp(engine.revision,'guide')
    guard=acMenuGuidePath(); %#ok<NASGU>
    ns='acmethods';
else
    ns='acmaster';
end
method=str2func([ns,'.',engine.package,'.',role]);
parent=struct('acycleParentJournal',journal);
[value,receipt]=method(p,parent);
status=receipt.status;
end
