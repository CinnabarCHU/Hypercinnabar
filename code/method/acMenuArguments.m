function s = acMenuArguments(role,args)
% Parse public name/value arguments after extracting the invocation id.
s = struct();
if strcmp(role,'analyzer')
    if numel(args)~=1 || ~isstruct(args{1}) || ~isscalar(args{1})
        error('Acycle:Menu:Arguments','Expected analyzer(params[,id]).');
    end
    s.params=args{1};
    if isfield(s.params,'override'), error('Acycle:Menu:Override','Only helper accepts override.'); end
    return
end
if strcmp(role,'helper')
    allowed={'input','override'}; first='input';
    s.input=struct(); s.override=struct();
else
    allowed={'plt','dat','res','params','target'}; first='plt';
    s.plt=struct(); s.dat=struct(); s.res=[]; s.params=struct(); s.target=[];
end
seen={};
if ~isempty(args) && isstruct(args{1})
    s.(first)=args{1}; seen={first}; args=args(2:end);
end
if mod(numel(args),2), error('Acycle:Menu:Arguments','Expected key/value pairs.'); end
for k=1:2:numel(args)
    key=args{k};
    if ~(ischar(key) && isrow(key) || isstring(key) && isscalar(key))
        error('Acycle:Menu:Arguments','Expected a parameter name.');
    end
    key=char(key);
    if ~ismember(key,allowed) || ismember(key,seen)
        error('Acycle:Menu:Arguments','Unknown or repeated %s argument "%s".',role,key);
    end
    seen{end+1}=key; %#ok<AGROW>
    s.(key)=args{k+1};
end
for key=intersect(fieldnames(s),{'input','override','plt','params','dat'})'
    if ~isstruct(s.(key{1})) || ~isscalar(s.(key{1}))
        error('Acycle:Menu:Struct','%s must be a scalar structure.',key{1});
    end
end
end
