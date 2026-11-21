function gaussian_center(core,root)
% Apply the original spectral filter to the mean-centred residual.
addpath(fullfile(core,'code','seriesanalysis'));
dest=fullfile(root,'fields','april-demean');
if ~exist(dest,'dir'),mkdir(dest);end
bands={[.000380 .000550;.000665 .000785],[.000385 .000605;.000700 .000910]};
for k=1:4
    filename=sprintf('series%d.mat',k);source=fullfile(root,'fields','april',filename);
    if k<=2
        z=load(source,'raw','t','trend','y','pda');
        residual=z.y-mean(z.y);
        for j=1:2
            b=bands{k}(j,:);
            y=gaussfilter(residual,mean(diff(z.t)),mean(b),b(1),b(2));
            z.g(:,j)=y(:);z.env(:,j)=abs(hilbert(y(:)));
        end
    else
        z=load(source,'pda');
    end
    save(fullfile(dest,filename),'-struct','z','-v7');
end
end
