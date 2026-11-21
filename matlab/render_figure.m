function render_figure(id,profile,root,outdir)
% Figures are rebuilt as native, editable MATLAB axes. IDs distinguish the
% two figures numbered 2. Physical widths refer to the saved page.
if ~exist(outdir,'dir'), mkdir(outdir); end
set(groot,'defaultFigureVisible','off','defaultAxesFontName','Times New Roman', ...
 'defaultTextFontName','Times New Roman','defaultAxesFontSize',9,'defaultTextFontSize',9);
isSupp=startsWith(id,'S');
sizeMM=struct('F1',[173 134],'F2h',[190 71],'F2iso',[177 203],'F3',[178 90], ...
 'F4',[184 162],'F5',[190 102],'F6',[180 165],'F7',[190 132],'F8',[170 185], ...
 'S1',[162 211],'S2',[162 166],'S3',[162 221],'S4',[162 194],'S5',[162 173], ...
 'S6',[162 210],'S7',[162 214]);
mm=sizeMM.(id); fig=figure('Color','w','Units','centimeters','Position',[1 1 mm/10], ...
    'PaperUnits','centimeters','PaperSize',mm/10,'PaperPosition',[0 0 mm/10], ...
    'PaperPositionMode','manual','Renderer','painters','Name',[id ' - ' profile],'NumberTitle','off');
closeFigure=onCleanup(@()close(fig)); fig.InvertHardcopy='off';
if isSupp, set(fig,'DefaultAxesFontSize',8,'DefaultTextFontSize',8); end
c=[.53 .68 .20;.11 .27 .54;.78 .17 .16;.93 .52 .14];
prefix=regexprep(profile,'-(caption|negative|native|bulk)$','');
if ismember(id,{'F1','F2h','F8','S6'}), orbit=load(fullfile(root,'fields','orbits.mat')); end
if ismember(id,{'F2iso','F3','F4','F5','F6','S1','S2','S3','S4','S5'})
    n=4; if ismember(id,{'F3','F6','S1','S2','S5'}), n=2; end
    q=cell(1,n);
    for k=1:n, q{k}=load(fullfile(root,'fields',prefix,sprintf('series%d.mat',k))); end
end
switch id
case 'F1'
    for j=1:3
        ax=panel([.105 .745-(j-1)*.323 .865 .225]); draworbit(ax,orbit,j,true);
    end
case 'F2h'
    for j=1:2
        ax=panel([.055+(j-1)*.5 .145 .438 .77]); horbit(ax,orbit.(['h' num2str(j)]),j,true);
        letter(ax,char(96+j));
    end
case 'F2iso'
    pos=[.874,.745,.514,.381,.251,.035]; ht=[.105,.087,.187,.105,.087,.187];
    for j=1:6
        k=1+(j>3); a=q{k}; ax=panel([.117 pos(j)+.03 .81 ht(j)]);
        typ=mod(j-1,3); t=a.t/1000;
        if typ==0
            plot(ax,a.pda(:,1)/1000,a.pda(:,2),'Color',c(k,:),'LineWidth',1.15); ylim(ax,[-.04 .63]);
            pda_arcs(ax,k,.50,.07); ylabel(ax,{'Short eccentricity','band power'});
        elseif typ==1
            plot(ax,t,a.y,'Color',light(c(k,:),.52),'LineWidth',.35); hold(ax,'on');
            plot(ax,t,2*a.g(:,1),'Color',c(k,:),'LineWidth',1.5);
            plot(ax,t,2*a.g(:,2),'Color',light(c(k,:),.32),'LineWidth',.9);
            ylim(ax,[-1.6 .8]); ylabel(ax,iso(k)); if j==2, legend(ax,{'Residual','Long band (2x)','Short band (2x)'},'Location','northwest','NumColumns',3,'FontSize',6); end
        else
            plot(ax,a.raw(:,1)/1000,a.raw(:,2),'Color',light(c(k,:),.45),'LineWidth',.35); hold(ax,'on');
            plot(ax,t,a.trend,'Color',c(k,:),'LineWidth',1.15);ylim(ax,[-2.5 2.5]);ylabel(ax,[iso(k) ' (‰)']); xlabel(ax,'Age (Ma)');
            if k==2, set(ax,'YDir','reverse'); end
        end
        xlim(ax,[39.5 65.5]); set(ax,'XTick',40:2:64); grid(ax,'on');
        if typ<2, ax.XTickLabel=[]; end
        letter(ax,char(103-j));
    end
case {'F3','S2'}
    for k=1:2
        if isSupp, pos=[.13 .59-(k-1)*.47 .81 .31];
        else, pos=[.063+(k-1)*.49 .16 .425 .72]; end
        ax=panel(pos); spectrum(ax,q{k},k,isSupp); letter(ax,char(96+k));
    end
    if isSupp, header('2\pi-MTM spectra and significance'); end
case 'F4'
    for j=1:4
        k=5-j; ax=panel([.16 .783-(j-1)*.184 .805 .126]); hold(ax,'on');
        windows=[41 42.3;43.4 44.4;45.6 47.5;52.2 53;53.55 54.15;55.1 55.85;56.55 57.5;58.2 59;59.8 60.55;61.5 62.3;63.2 64.1];
        for w=windows', patch(ax,w([1 2 2 1]),[0 0 1.35 1.35],[.99 .964 .89],'EdgeColor','none'); end
        a=q{k}; if ~isfield(a,'pda'),axis(ax,'off');text(ax,.4,.5,'Window count exceeds revision limit','Units','normalized');continue,end
        plot(ax,a.pda(:,1)/1000,a.pda(:,2),'Color',c(k,:),'LineWidth',1.25);
        yl=[.55 .55 1 1]; ylim(ax,[0 yl(k)]); xlim(ax,[40 65]);
        pda_arcs(ax,k,yl(k)*.91,yl(k)*.12); ax.XTick=[]; ylabel(ax,name(k)); letter(ax,char(96+k));
    end
    annotation(fig,'textbox',[.28 .541 .58 .035],'String','~2.4 Myr              \leftarrow  Resonance transition  \rightarrow             ~1.2 Myr', ...
        'HorizontalAlignment','center','EdgeColor','none','FitBoxToText','off','FontSize',8);
    stages(panel([.16 .062 .805 .091]),40,65);
case 'F5'
    for k=1:4
        x=.045+(k-1)*.249; s=evo_field(q{k},profile);
        side=panel([x .135 .037 .745]); map=panel([x+.053 .135 .145 .745]);
        evo_panel(map,side,q{k},s,k,c(k,:),true,endsWith(profile,'-native'));
        letter(side,char(96+k));
    end
case {'F6','S5'}
    for k=1:2
        y=.565-(k-1)*.445;
        ax=panel([.09 y .674 .348]); axg=panel([.813 y .105 .348]);
        isotope_wave(ax,axg,q{k}.cwt,k,c(k,:),isSupp); letter(ax,char(96+k));
    end
    if isSupp, header('Isotope continuous wavelet power'); end
case {'F7','S7'}
    for k=1:5
        if isSupp
            x=.11; y=.803-(k-1)*.183; ww=.76; hh=.121;
        else
            x=.056+mod(k-1,2)*.493; y=.707-floor((k-1)/2)*.326; ww=.407; hh=.243;
        end
        ax=panel([x y ww hh]); a=load(fullfile(root,'fields','wtc',sprintf('pair%d.mat',k)));
        coherent(ax,a,k,endsWith(profile,'negative'),~isSupp); letter(ax,char(96+k));
    end
    if isSupp, header('Wavelet coherence and relative phase');
    else
        ax=panel([.575 .063 .36 .20]); legendphase(ax); letter(ax,'f');
    end
case 'F8'
    l=load(fullfile(root,'data','figure8_sources.mat')); l.kt_primary=readmatrix(fullfile(root,'data','kt2014_panel1c.csv')); composite8(orbit,l,endsWith(profile,'bulk'));
case 'S1'
    header('Sampling and preprocessing');
    for k=1:2
        a=q{k}; base=.755-(k-1)*.45;
        ax=panel([.12 base .31 .13]); histogram(ax,diff(a.raw(:,1)),'BinEdges',[0:.5:10 12 15 20 30 50 100 250],'FaceColor',c(k,:),'EdgeColor','none');xlim(ax,[0 25]);
        xlabel(ax,'Sampling interval (kyr)');ylabel(ax,'Count');title(ax,name(k));xline(ax,median(diff(a.raw(:,1))),'--');letter(ax,char(96+(k-1)*3+1));
        ax=panel([.57 base .38 .13]);plot(ax,a.raw(:,1)/1000,a.raw(:,2),'Color',light(c(k,:),.56));hold(ax,'on');plot(ax,a.t/1000,a.trend,'Color',c(k,:),'LineWidth',1.4);
        xlim(ax,[40 65]);xlabel(ax,'Age (Ma)');ylabel(ax,'‰');title(ax,'4 Myr LOWESS');letter(ax,char(96+(k-1)*3+2));
        ax=panel([.12 base-.212 .83 .125]);plot(ax,a.t/1000,a.residual,'Color',light(c(k,:),.51));hold(ax,'on');
        plot(ax,a.t/1000,a.y,'Color',c(k,:),'LineWidth',.95);xlim(ax,[55.55 56.12]);xlabel(ax,'Age (Ma)');ylabel(ax,'Residual (‰)');title(ax,sprintf('PETM replacement  (%d samples)',sum(a.y~=a.residual)));
        legend(ax,{'Before','After'},'Location','southwest','FontSize',7);letter(ax,char(96+(k-1)*3+3));
    end
case 'S3'
    header('Gaussian bands and short-eccentricity power');
    for k=1:2
        a=q{k}; ax=panel([.13 .794-(k-1)*.129 .80 .089]);hold(ax,'on');
        for j=1:2, plot(ax,a.t/1000,a.g(:,j),'Color',light(c(k,:),.32*(j-1)),'LineWidth',1.05,'LineStyle',pick(j,'-','--')); end
        xlim(ax,[40 65]);ylabel(ax,iso(k));if k==1,legend(ax,{'Long band','Short band'},'Location','northwest','NumColumns',2,'FontSize',7);end
    end
    for k=1:4
        a=q{k}; ax=panel([.13 .50-(k-1)*.137 .80 .089]);if ~isfield(a,'pda'),axis(ax,'off');text(ax,.4,.5,'Window count exceeds revision limit','Units','normalized');continue,end;plot(ax,a.pda(:,1)/1000,a.pda(:,2),'Color',c(k,:));hold(ax,'on');
        [pk,tx]=findpeaks(a.pda(:,2),a.pda(:,1)/1000,'MinPeakDistance',.9,'MinPeakProminence',.055);
        plot(ax,tx,pk,'.','Color',c(k,:));for j=2:numel(tx),text(ax,mean(tx(j-1:j)),max(pk)*1.03,sprintf('%.1f',diff(tx(j-1:j))),'FontSize',5.5,'HorizontalAlignment','center');end
        xlim(ax,[40 65]);ylim(ax,[0 max(max(a.pda(:,2))*1.31,eps)]);ylabel(ax,name(k));if k==4,xlabel(ax,'Age (Ma)');end
    end
case 'S4'
    header('Taner filters and evolutionary FFT');
    for k=1:4
        x=.11+mod(k-1,2)*.469; y=.552-floor((k-1)/2)*.452;
        side=panel([x y .065 .344]);map=panel([x+.094 y .246 .344]);s=evo_field(q{k},profile);
        evo_panel(map,side,q{k},s,k,c(k,:),false,endsWith(profile,'-native'));letter(side,char(96+k));
    end
case 'S6'
    header('Orbital eccentricity and wavelet power of h');
    for j=1:3
        ax=panel([.12 .792-(j-1)*.157 .82 .111]);draworbit(ax,orbit,j,j==1);letter(ax,char(96+j));
    end
    for j=1:2
        ax=panel([.12 .256-(j-1)*.177 .82 .13]);horbit(ax,orbit.(['h' num2str(j)]),j,false);letter(ax,char(99+j));
    end
end
drawnow;
savefig(fig,fullfile(outdir,'plot.fig'),'compact');
print(fig,fullfile(outdir,'plot.svg'),'-dsvg','-painters');
% Reopening the saved object verifies that it is an editable MATLAB figure.
chk=openfig(fullfile(outdir,'plot.fig'),'invisible'); assert(~isempty(findall(chk,'Type','axes')));close(chk);
end

function ax=panel(pos)
ax=axes('Units','normalized','Position',pos,'Box','on','Layer','top','TickDir','out');
end
function header(t)
annotation(gcf,'textbox',[.09 .945 .84 .042],'String',t,'HorizontalAlignment','center','EdgeColor','none','FontWeight','bold','FontSize',12);
end
function letter(ax,t)
text(ax,-.082,1.026,t,'Units','normalized','FontName','Arial','FontWeight','bold','FontSize',12,'VerticalAlignment','bottom','Clipping','off');
end
function t=iso(k)
labels={'\delta^{13}C','\delta^{18}O'};t=labels{k};
end
function t=name(k)
labels={'Benthic \delta^{13}C','Benthic \delta^{18}O','ZB18a eccentricity','La10c eccentricity'};t=labels{k};
end
function a=light(c,x),a=c*(1-x)+x;end
function v=pick(j,a,b),if j==1,v=a;else,v=b;end,end
function draworbit(ax,o,j,showLegend)
names={'La10a','La10b','La10c','ZB18a','ZB20a','ZB20b'};
col=[.835 .369 0;.902 .624 0;.533 .133 .333;0 .447 .698;.337 .706 .914;0 .62 .451]; left=-45-5*j;hold(ax,'on');
for i=1:6,z=o.(names{i});x=-z(:,1);use=x>=left&x<=left+5;plot(ax,x(use),z(use,2),'Color',light(col(i,:),.4),'LineWidth',.4);end
h=gobjects(1,6);
for i=1:6,z=o.(names{i});x=-z(:,1);use=x>=left&x<=left+5;h(i)=plot(ax,x(use),z(use,3),'Color',col(i,:),'LineWidth',1.65);end
xlim(ax,[left left+5]);ylim(ax,[0 .08]);ax.YTick=0:.02:.08;ylabel(ax,'e_{\oplus}');if j==3,xlabel(ax,'Time (Myr)');end
if showLegend && j==1,legend(ax,h([4 1 5 2 6 3]),names([4 1 5 2 6 3]),'NumColumns',3,'Location','northwest','FontSize',6.5);end
end
function horbit(ax,d,k,annotated)
v=max(-8,min(6,floor(double(d.logpower))));imagesc(ax,d.t,log2(d.scale),v);set(ax,'YDir','reverse');hold(ax,'on');colormap(ax,jet(15));clim(ax,[-8 6]);
ticks=[73 174 232 304];set(ax,'YTick',log2(ticks),'YTickLabel',string(ticks));xlim(ax,[38 67]);xlabel(ax,'Age (Ma)');ylabel(ax,'Period (kyr)');
titles={'ZB18a','La10c'};title(ax,[titles{k} ' Earth h = e sin(\varpi)']);
ff=4*pi/(6+sqrt(38));plot(ax,d.t,log2(max(d.coi,eps)),'k','LineWidth',.6);
if annotated
    for m=1:size(d.arc_age,1),a=d.arc_age(m,:);if mean(a)>48.3 && mean(a)<52,continue,end;plot(ax,a,log2(d.arc_period(m,:)/ff),'k','LineWidth',1.2);end
    text(ax,42.8,log2(61),'~2.4','FontWeight','bold');text(ax,55.1,log2(61),'~1.5','FontWeight','bold');
    if k==2,text(ax,58.3,log2(61),'~2.0','FontWeight','bold');end
    for j=1:4,gt={'g_3, g_4','g_2','g_1','g_5'};text(ax,38.25,log2(ticks(j)),gt{j},'Color','w','FontSize',7);end
end
ylim(ax,log2([d.scale(1) d.scale(end)]));
end
function spectrum(ax,z,k,supp)
if ~isfield(z,'sp'),axis(ax,'off');text(ax,.1,.5,'SWA/FDR unavailable in this revision','Units','normalized');return,end
s=z.sp;s=s(s(:,1)<=.005,:);hold(ax,'on');
plot(ax,s(:,1)*1000,s(:,6),'--','Color',[.78 .03 .08],'LineWidth',1.25);
plot(ax,s(:,1)*1000,s(:,5),'-.','Color',[.04 .39 .61],'LineWidth',.85);
plot(ax,s(:,1)*1000,s(:,4),'--','Color',[.88 .39 .11],'LineWidth',.85);
plot(ax,s(:,1)*1000,s(:,3),'Color',[.30 .30 .30],'LineWidth',.8);
plot(ax,s(:,1)*1000,s(:,2),'k','LineWidth',.8);
if supp
    use=islocalmax(s(:,2))&s(:,2)>s(:,4)&s(:,2)>s(:,6);plot(ax,s(use,1)*1000,s(use,2),'o','MarkerSize',3,'Color',[.5 .1 .1]);
end
xlim(ax,[0 5]);ylim(ax,[0 max( max(s(:,2))*1.2,1e-10)]);title(ax,name(k));ylabel(ax,'Power');xlabel(ax,'Frequency (cycles/Myr)');
legend(ax,{'5% FDR','99% \chi^2','95% \chi^2','SWA background','Power'},'Location','northeast','FontSize',6);
bands=[.00038 .00055;.000665 .000785;.00235 .00258];if k==2,bands(1:2,:)=[.000385 .000605;.0007 .00091];end
for i=1:3
 ix=find(s(:,1)>=bands(i,1)&s(:,1)<=bands(i,2));if isempty(ix),continue,end
 if ~supp && k==2 && i==1
     candidates=ix(islocalmax(s(ix,2)));[~,near]=min(abs(1./s(candidates,1)-2200));ix=candidates(near);
 end
 [v,ii]=max(s(ix,2));p=1/s(ix(ii),1);if supp,tx=sprintf('%.0f kyr',p);else,tags={'~2.2 Myr',pick(k,'~1.4 Myr','~1.3 Myr'),'405 kyr'};tx=tags{i};end
 text(ax,s(ix(ii),1)*1000,v*1.04,tx,'FontSize',7,'HorizontalAlignment','center','VerticalAlignment','bottom');
end
end
function pda_arcs(ax,k,h,dy)
% Coordinates of the interpreted intervals are artwork annotations in the source.
ends1={ [40.7 43.1 45.1 47.1],[51.9 53.2 54.5 55.8 57.8 59.0 61.0 62.4 64.4]};
ends2={ [40.45 42.85 44.85 46.85],[52.0 53.3 54.6 55.9 57.1 58.3 59.5 61.5 62.8 64.8]};
ends3={ [40.4 43.1 45.1 47.8],[51.9 53.2 54.5 55.8 57.4 59.0 60.9 62.3 64.3]};
ends4={ [40.4 43.1 45.1 47.8],[51.9 53.2 54.5 55.8 57.8 59.8 61.8 63.2 64.6]};
all={ends1,ends2,ends3,ends4};arcs=all{k};hold(ax,'on');theta=linspace(0,pi,30);
for set=1:2, e=arcs{set};for j=1:numel(e)-1
 x=linspace(e(j),e(j+1),30);plot(ax,x,h+dy*sin(theta),'--','Color',[.35 .35 .35],'LineWidth',.65);
 if ~(k>=3&&set==1&&j==3),label=e(j+1)-e(j);if k>=3&&set==1&&j==1,label=2.4;end
 text(ax,mean(x),h+dy,sprintf('%.1f',label),'HorizontalAlignment','center','VerticalAlignment','bottom','FontSize',6.2);end
end,end
end
function stages(ax,lo,hi)
hold(ax,'on'); ages=[40 41.2 47.6 56 59.5 62.05 65]; labels={'Ba.','Lutetian','Ypresian','Th.','Se.','Da.'};
for k=1:6,rectangle(ax,'Position',[ages(k) .5 diff(ages(k:k+1)) .5]);text(ax,mean(ages(k:k+1)),.75,labels{k},'HorizontalAlignment','center','FontSize',8);end
for r=[40 56;56 65]',rectangle(ax,'Position',[r(1) 0 diff(r) .5]);end
text(ax,48,.25,'Eocene','HorizontalAlignment','center');text(ax,60.5,.25,'Paleocene','HorizontalAlignment','center');
xlim(ax,[lo hi]);ylim(ax,[0 1]);ax.YTick=[];xlabel(ax,'Age (Ma)');
end
function s=evo_field(q,profile)
j=1;if contains(profile,'caption') && numel(q.evo)>1,j=2;end;s=q.evo(j);
end
function evo_panel(ax,side,q,s,k,col,mark,pure)
if pure&&isfield(q,'native_lowpass_error')
    axis(ax,'off');axis(side,'off');text(ax,.5,.5,{'f_{low} = 0','unsupported'},'Units','normalized','HorizontalAlignment','center');title(ax,name(k));return
end
plot(side,s.tan,q.t/1000,'Color',col,'LineWidth',.7);ylim(side,[40 65]);set(side,'YDir','reverse');ylabel(side,'Age (Ma)');
imagesc(ax,s.f*1000,s.age/1000,s.amp);set(ax,'YDir','reverse');colormap(ax,parula(128));clim(ax,[0 1]);ylim(ax,[40 65]);xlim(ax,[0 1.8]);
ax.YTickLabel=[];ax.XTick=[0 .5 1 1.5];xlabel(ax,'Frequency (cycles/Myr)');titles={'Benthic \delta^{13}C','Benthic \delta^{18}O','ZB18a Ecc','La10c Ecc'};title(ax,titles{k});
if mark
    hold(ax,'on');yy=46.6+.2*(k>2);
    for y=[yy 51.6],yline(ax,y,'w--','LineWidth',1);text(ax,1.76,y-.21,sprintf('%.1f Ma',y),'HorizontalAlignment','right','Color','w','FontSize',6);end
    x0=[.74 .70 .73 .80];x1=[.42 .64 .51 .55];quiver(ax,x0(k),51.35,x1(k)-x0(k),yy-51.1,0,'Color',[.8 .15 .12],'MaxHeadSize',.45,'LineWidth',1);
end
end
function isotope_wave(ax,axg,w,k,col,supp)
v=double(w.color);y=log2(w.period);x=w.t/1000;
% The main graphic has a normalized colour bar. The two linear transforms
% of GUI log2 power are calibrated to the colour-bar positions in its artwork.
z=log2(max(v,realmin));
if supp
    imagesc(ax,x,y,z);clim(ax,[-16 0]);
else
    offset=[.97887 .96468];slope=[.018870 .024777];
    u=max(0,min(1,offset(k)+slope(k)*z));cm=parula(256);
    idx=1+round(255*u);rgb=reshape(cm(idx(:),:),[size(u) 3]);
    exterior=w.period(:)>w.coi(:)';rgb=rgb.*(1-.33*exterior)+.33*exterior;
    image(ax,[x(1) x(end)],[y(1) y(end)],rgb);clim(ax,[0 1]);
end
set(ax,'YDir','normal');colormap(ax,parula(256));hold(ax,'on');
contour(ax,x,y,double(w.signif),[1 1],'k','LineWidth',.8);
plot(ax,x,log2(max(w.coi,eps)),'Color',[.22 .22 .22],'LineWidth',.75);
yt=[95 125 405 1200 2400];set(ax,'YTick',log2(yt),'YTickLabel',string(yt),'YLim',log2([64 5000]),'XLim',[40 65]);
xlabel(ax,'Age (Ma)');ylabel(ax,'Period (kyr)');title(ax,name(k));
if supp,fac=1;else,fac=pick(k,1e4,1e5);end
plot(axg,fac*w.global_power,y,'Color',col,'LineWidth',1);axg.YLim=ax.YLim;axg.YTick=[];
if supp,xlabel(axg,'Global power');else,xlabel(axg,pick(k,'Power (10^{-4})','Power (10^{-5})'));end
if ~supp
 for p=[2200, pick(k,1400,1300)],yline(ax,log2(p),'--','Color',[.65 .65 .65]);text(ax,46.3,log2(p)-.12,sprintf('~%.1f Myr',p/1000),'FontSize',7);end
end
cb=colorbar(ax,'Position',[.947 ax.Position(2) .011 ax.Position(4)]);cb.FontSize=6;if supp,cb.Ticks=-16:4:0;else,cb.Ticks=0:.2:1;end
end
function coherent(ax,a,k,neg,compact)
x=a.t(:)'/1000;y=log2(a.period(:));v=double(a.r2); cmap=parula(128);
idx=1+round(min(1,max(0,v))*127); rgb=reshape(cmap(idx(:),:),[size(v) 3]);
outside=a.period(:)>a.coi(:)'; rgb=rgb.*(1-.48*outside)+.48*outside;
image(ax,[x(1) x(end)],[y(1) y(end)],rgb);hold(ax,'on');ax.YDir='reverse';colormap(ax,cmap);clim(ax,[0 1]);
contour(ax,x,y,double(a.sig),[1 1],'k','LineWidth',.85);plot(ax,x,log2(max(a.coi,eps)),'Color',[.27 .27 .27],'LineWidth',.6);
theta=a.phase;if neg&&k<5,theta=theta+pi;end
[xx,yy]=meshgrid(a.arrow_age/1000,log2(a.arrow_period));
% Positive mathematical phase points toward greater period on these reversed axes,
% giving the same downward direction as Grinsted phaseplot.
width=diff([40 65]);height=log2(5000/64);pos=ax.Position;fpos=gcf().Position;
u=.0033*width*cos(theta); v=.0033*height*pos(3)*fpos(3)/(pos(4)*fpos(4))*sin(theta);
% Draw heads in normalized screen coordinates, including reversed period axis.
thin=1;if ~compact,thin=2;end
ii=1:thin:size(xx,2);xx=xx(:,ii);yy=yy(:,ii);u=u(:,ii);v=v(:,ii);
sy=height*pos(3)*fpos(3)/(width*pos(4)*fpos(4));
xx=xx(:)';yy=yy(:)';u=u(:)';v=v(:)';nn=nan(size(xx));
px=[xx-u;xx+u;nn;xx+.25*u+.32*v/sy;xx+u;xx+.25*u-.32*v/sy;nn]; ...
    py=[yy-v;yy+v;nn;yy+.25*v-.32*u*sy;yy+v;yy+.25*v+.32*u*sy;nn];
line(ax,px(:),py(:),'Color',[.16 .22 .20],'LineWidth',.32);
xlim(ax,[40 65]);ylim(ax,log2([64 5000]));yt=[128 256 512 1024 2048 4096];ax.YTick=log2(yt);ax.YTickLabel=string(yt);
xlabel(ax,'Age (Ma)');ylabel(ax,'Period (kyr)');n={'ZB18a vs \delta^{13}C','La10c vs \delta^{13}C','ZB18a vs \delta^{18}O','La10c vs \delta^{18}O','\delta^{13}C vs \delta^{18}O'};
title(ax,n{k});cb=colorbar(ax,'Position',[pos(1)+pos(3)+.009 pos(2) .008 pos(4)]);cb.FontSize=6;cb.Ticks=[0 .5 1];
end
function legendphase(ax)
axis(ax,'off');xlim(ax,[0 1]);ylim(ax,[0 1]);hold(ax,'on');
for j=1:2
    x=.24+(j-1)*.52;y=.37+(j-1)*.33;
    for d=[-1 0;1 0;0 -1;0 1]',quiver(ax,x,y,.155*d(1),.22*d(2),0,'k','LineWidth',1,'MaxHeadSize',.55);end
    text(ax,x,y+.24,pick(j,'\delta^{18}O leads','Isotope leads'),'HorizontalAlignment','center','FontSize',7);
    text(ax,x,y-.26,pick(j,'\delta^{13}C leads','Eccentricity leads'),'HorizontalAlignment','center','FontSize',7);
    text(ax,x+.16,y,'0°','FontSize',6);text(ax,x-.24,y,'180°','FontSize',6);
end
end
function composite8(o,l,bulk)
ax=panel([.092 .725 .79 .205]);hold(ax,'on');names={'La2004','La10a','La10b','La10c','La10d','ZB18a'};
cols=[.18 .18 .18;.85 .17 .18;.2 .32 .83;.16 .7 .2;.1 .78 .82;.84 .02 .78];
for j=1:6,d=o.(names{j});plot(ax,d(:,1),d(:,4),'Color',cols(j,:),'LineWidth',.65+1.65*(j==6));end
xlim(ax,[42 60]);set(ax,'XAxisLocation','top','YAxisLocation','right');xlabel(ax,'Age (Ma)');ylabel(ax,'Eccentricity');legend(ax,names,'Location','northwest','NumColumns',3,'FontSize',6);letter(ax,'a');
ax=panel([.092 .47 .79 .22]);b=o.h8;
% h8 is uniformly spaced in log2(period); interpolate onto the displayed
% linear period axis to reproduce the 20, 40, 60, 80, 100 kyr scale.
pp=linspace(16,108,160);v=interp1(b.period,double(b.logpower),pp);imagesc(ax,b.t,pp,max(-8,min(6,floor(v))));colormap(ax,jet(15));clim(ax,[-8 6]);
xlim(ax,[42 60]);ylim(ax,[16 108]);ax.YDir='reverse';ax.YAxisLocation='right';ax.XTick=[];ylabel(ax,'Period (kyr)');hold(ax,'on');b=o.h1;
for j=1:size(b.arc_age,1),t=b.arc_age(j,:);if mean(t)>48.2&&mean(t)<52.4,continue,end;plot(ax,t,b.arc_period(j,:),'k','LineWidth',1.25);end
text(ax,43,58,'~2.4 Myr','FontWeight','bold');text(ax,53.1,58,'~1.5 Myr','FontWeight','bold');letter(ax,'b');
ax=panel([.224 .23 .658 .205]);w=l.westerhold;hold(ax,'on');
zones=[49.17 49.55;51.38 51.97;52.84 53.23;54.26 54.64;55.74 56.14;58.04 58.43;59.38 59.76];
for w0=zones',patch(ax,w0([1 2 2 1]),[-1.3 -1.3 2.85 2.85],[.89 .89 .89],'EdgeColor','none');end
for j=1:2
    ids=[2 3]+2*(j-1);ok=w(:,1)>=45&w(:,1)<=60&all(isfinite(w(:,ids)),2);
    x=w(ok,1);a=w(ok,ids);fill(ax,[x;flipud(x)],[a(:,1);flipud(a(:,2))],pick(j,[1 .78 .78],[.72 .72 .72]),'EdgeColor','none');
end
plot(ax,w(:,1),w(:,6),'r','LineWidth',1.35);plot(ax,w(:,1),w(:,7),'k','LineWidth',1.35);
xlim(ax,[45 60]);ylim(ax,[-1.3 2.85]);ax.YAxisLocation='right';ax.XTick=[];ylabel(ax,'\delta^{13}C (‰)');letter(ax,'c');
ax=panel([.224 .105 .658 .115]);if bulk,xy=l.kt1258(:,[1 5]);else,xy=l.kt_primary;end
hold(ax,'on');
for w0=zones',patch(ax,w0([1 2 2 1]),[-1 -1 0 0],[.89 .89 .89],'EdgeColor','none');end
plot(ax,xy(:,1),xy(:,2),'Color',[.31 .31 .31],'LineWidth',.75);ylim(ax,[-1 0]);ax.YDir='reverse';xlim(ax,[45 60]);ylabel(ax,'\delta^{13}C (‰)');xlabel(ax,'Age (Ma)');letter(ax,'d');
ax=panel([.224 .055 .658 .015]);hold(ax,'on');
pol=[46.24 47.85;48.99 49.76;50.81 50.96;51.06 51.79;52.63 52.97;53.08 53.19;53.42 53.94;57.09 57.64;58.93 59.25];
for b=pol',rectangle(ax,'Position',[b(1) 0 diff(b) 1],'FaceColor','k');end
xlim(ax,[45 60]);ylim(ax,[0 1]);ax.XTick=[];ax.YTick=[];
ax=panel([.224 .024 .658 .028]);hold(ax,'on');
for b=[45 56;56 60]',rectangle(ax,'Position',[b(1) 0 diff(b) 1],'FaceColor',[.96 .82 .63]);end
text(ax,50,.5,'Eocene','HorizontalAlignment','center','FontSize',7);text(ax,58,.5,'Paleocene','HorizontalAlignment','center','FontSize',7);
xlim(ax,[45 60]);ylim(ax,[0 1]);axis(ax,'off');
end
