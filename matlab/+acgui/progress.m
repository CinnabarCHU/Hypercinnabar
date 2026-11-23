function previous = progress(varargin)
% Transient UI observer. Stored Analyzer options refer only to a named function.
persistent observer
previous = observer;
if nargin == 1
    observer = varargin{1};
elseif nargin == 2 && ~isempty(observer)
    observer(varargin{1},varargin{2});
end
end
