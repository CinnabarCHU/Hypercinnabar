function value = acMenuExecute(tag,role,request,journal,live)
% Shared entry for a fresh call and an exact replay of its recorded arguments.
op=['Menu_',tag,'-v1/',role];
value=aclog.invoke(op,request,journal,@dispatch);
    function [out,status]=dispatch(stored)
        menu=acMenuCatalog(tag);
        if ~ismember(role,strsplit(menu.roles)), error('Acycle:Menu:Role','%s has no %s.',tag,role); end
        s=acMenuArguments(role,stored.args);
        status='done';
        switch role
        case 'helper'
            out=acMenuPrepare(menu,s.input,s.override,journal,stored);
        case 'analyzer'
            if ~isfield(s.params,'operation'), error('Acycle:Menu:MissingOption','Missing params.operation.'); end
            engine=acMenuEngine(menu,s.params.operation);
            p=rmfield(s.params,'operation');
            acMenuValidate(engine,p);
            [out,status]=acMenuOriginal(engine,'analyzer',p,journal);
            if strcmp(engine.operation,'Bispectral') && isfield(stored,'bispectralCreated')
                out.Created = stored.bispectralCreated;
            end
        case 'plotter'
            if isfield(s.plt,'operation'), selector=s.plt.operation;
            elseif isfield(s.params,'operation'), selector=s.params.operation;
            else, error('Acycle:Menu:MissingOption','Supply operation in plt or params.'); end
            view=strcmp(selector,'Bispectral') && isfield(s.params,'operation') && strcmp(s.params.operation,'BispectralView');
            if isfield(s.params,'operation') && ~strcmp(s.params.operation,selector) && ~view
                error('Acycle:Menu:Operation','Plot and analysis selectors disagree.');
            end
            engine=acMenuEngine(menu,selector);
            [out,status]=acMenuPlot(menu,engine,s,journal,live);
        otherwise
            error('Acycle:Menu:Role','Unknown role %s.',role);
        end
    end
end
