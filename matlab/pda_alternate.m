function pda_alternate(core,reference,root)
% Recalculate a second set of frequency bounds with the April Acycle routine.
q=compute_inputs(core,reference);dest=fullfile(root,'fields','april-archiveband');
if ~exist(dest,'dir'),mkdir(dest);end
for k=1:4
    out=load(fullfile(root,'fields','april',sprintf('series%d.mat',k)));
    bands=[1/55 1/27]; if k==4,bands=[1/140 1/80];end
    padded=zeropad2([q(k).t q(k).y],800,1);
    out.pda=pdan(padded,bands,800,2,0,.08,1,5000);
    save(fullfile(dest,sprintf('series%d.mat',k)),'-struct','out','-v7');
end
end
