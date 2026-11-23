function id = acMenuNewId()
% Reserve a portable positive integer invocation identifier in ACYCLE_LOG_DIR.
id = aclog.interfaceId('register');
end
