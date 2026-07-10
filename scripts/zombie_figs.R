# Supporting figures for the zombie post.
suppressWarnings(suppressMessages({library(data.table); library(ggplot2); library(survival)}))
hp <- list(paper="#F7F7F4", ink="#18181B", muted="#71717A", hair="#E6E6E1", accent="#2348E5",
           rise="#1C8F5A", fall="#D2463A", surface="#ECE9E1", amber="#C77B30", purple="#6D4AA6")
th <- function(bs=12) theme_minimal(base_size=bs, base_family="mono") + theme(
  plot.background=element_rect(fill=hp$paper,color=NA), panel.background=element_rect(fill=hp$paper,color=NA),
  plot.title.position="plot", plot.caption.position="plot",
  plot.title=element_text(face="bold",color=hp$ink,hjust=0,size=bs+3),
  plot.subtitle=element_text(color=hp$muted,hjust=0,size=bs-2,margin=margin(t=4,b=12)),
  plot.caption=element_text(color=hp$muted,hjust=0,size=bs-4,margin=margin(t=12)),
  axis.text=element_text(color=hp$muted,size=bs-3), axis.title=element_blank(), axis.ticks=element_blank(),
  panel.grid.minor=element_blank(), panel.grid.major.x=element_blank(),
  panel.grid.major.y=element_line(color=hp$hair,linewidth=0.4), plot.margin=margin(14,18,10,14))
save_png <- function(p,f,w=8.2,h=4.6) ggsave(file.path("outputs/figures",f),p,width=w,height=h,dpi=150,device=ragg::agg_png)
dir.create("outputs/figures", showWarnings=FALSE, recursive=TRUE)

## ---- data ----
afs <- readRDS("data/raw/zombie_extract_v2.rds")
reg <- unique(readRDS("data/raw/zombie_register.rds"), by="oib")
afs <- afs[!is.na(oib) & oib!="" & grepl("^[A-U]$", nace) & nace!="K"]
setorder(afs, oib, year, -revenue); afs <- unique(afs, by=c("oib","year"))
afs[reg, `:=`(brisan_year=i.brisan_year), on="oib"]
afs[, `:=`(net=profit-loss, has_bs=!is.na(assets)&assets>0)]
afs[, z_ne := has_bs & !is.na(equity) & equity<0]
afs[, z_core := z_ne & !is.na(net) & net<0]

## ---- FIG 1: stock trend ----
st <- afs[has_bs==TRUE & year>=2004, .(ne=100*mean(z_ne), core=100*mean(z_core)), by=year][order(year)]
stm <- melt(st, id.vars="year")
p1 <- ggplot(stm, aes(year, value, color=variable)) +
  geom_line(linewidth=1.1) +
  geom_point(data=stm[year==max(year)], size=2.3) +
  geom_text(data=stm[year==max(year)], aes(label=paste0(round(value),"%")), hjust=-0.25, size=3.3, family="mono", fontface="bold") +
  scale_color_manual(values=c(ne=hp$fall, core=hp$amber),
                     labels=c(ne="duguje više nego vrijedi (negativni kapital)", core="+ posluje s gubitkom")) +
  scale_x_continuous(limits=c(2004,2026), breaks=seq(2004,2024,4)) +
  scale_y_continuous(limits=c(0,35), labels=function(x)paste0(x,"%")) +
  labs(title="Svaka četvrta firma duguje više nego što vrijedi",
       subtitle="Udio nefinancijskih firmi s negativnim kapitalom, 2004.–2024.",
       caption="Izvor: FINA GFI. Obrada: AI.econ", color=NULL) +
  th() + theme(legend.position="top", legend.text=element_text(size=8))
save_png(p1,"zombie_stock.png")

## ---- FIG 2: survival curve (how long they stay insolvent) ----
BS <- afs[has_bs==TRUE]; setorder(BS,oib,year)
lkz <- BS[,.(oib,year,zf=z_ne)]; BS[,yprev:=year-1L]; BS[lkz,zprev:=i.zf,on=.(oib,yprev=year)]
BS[,entry:=z_ne&(is.na(zprev)|zprev==FALSE)]; BS[,sid:=cumsum(fifelse(is.na(entry),FALSE,entry))]
BS[,last_bs:=max(year),by=oib]
zt <- BS[z_ne==TRUE]
sp <- zt[,.(oib=oib[1],start=min(year),end=max(year),len=.N,lu=last_bs[1],by_=brisan_year[1]),by=sid]
sp[,ep1:=end+1L]; sp[lkz,nz:=i.zf,on=.(oib,ep1=year)]; sp[,sm1:=start-1L]; sp[lkz,pz:=i.zf,on=.(oib,sm1=year)]
sp[,incident:=!is.na(pz)&pz==FALSE]
sp[,event:=as.integer((!is.na(nz)&nz==FALSE)|(is.na(nz)&end==lu&!is.na(by_)&by_<=end+3L))]
inc <- sp[incident==TRUE]
fit <- survfit(Surv(len,event)~1, data=inc)
sd <- data.table(t=c(0,fit$time), s=100*c(1,fit$surv))
p2 <- ggplot(sd, aes(t,s)) +
  geom_step(linewidth=1.1, color=hp$fall) +
  geom_hline(yintercept=50, linetype="dashed", color=hp$muted, linewidth=0.4) +
  annotate("segment", x=4,xend=4,y=0,yend=50, linetype="dashed", color=hp$muted, linewidth=0.4) +
  annotate("text", x=4.2, y=57, label="pola ih je i dalje\nnemrtvo nakon 4 godine", hjust=0, size=3, family="mono", color=hp$ink) +
  scale_x_continuous(limits=c(0,12), breaks=0:12) +
  scale_y_continuous(limits=c(0,100), labels=function(x)paste0(x,"%")) +
  labs(title="Nemrtve godinama",
       subtitle="Udio firmi još u negativnom kapitalu, po godinama otkad su pale u minus",
       caption="Kaplan–Meier krivulja. Izvor: FINA GFI. Obrada: AI.econ") + th()
save_png(p2,"zombie_survival.png")

## ---- FIG 3: sector bars (latest) ----
snames <- c(A="Poljoprivreda",B="Rudarstvo",C="Prerađivačka ind.",D="Energetika",E="Vodoopskrba",
  F="Građevinarstvo",G="Trgovina",H="Prijevoz i skladištenje",I="Turizam (smještaj, ugost.)",
  J="Informacije i komun.",L="Nekretnine",M="Stručne djelatnosti",N="Administrativne usl.",
  O="Javna uprava",P="Obrazovanje",Q="Zdravstvo",R="Umjetnost i rekreacija",S="Ostale uslužne")
sec <- afs[has_bs==TRUE & year %in% 2021:2023, .(ne=100*mean(z_ne)), by=nace]
sec <- sec[nace %in% names(snames)]; sec[, lab:=snames[nace]]
sec[, hl := nace %in% c("I","L")]
p3 <- ggplot(sec, aes(reorder(lab,ne), ne, fill=hl)) +
  geom_col(width=0.72) +
  geom_text(aes(label=paste0(round(ne),"%")), hjust=-0.2, size=2.9, family="mono", color=hp$ink) +
  coord_flip() +
  scale_fill_manual(values=c(`FALSE`=hp$surface, `TRUE`=hp$fall), guide="none") +
  scale_y_continuous(limits=c(0,52), labels=function(x)paste0(x,"%")) +
  labs(title="Nekretnine i turizam vode",
       subtitle="Udio firmi s negativnim kapitalom, po djelatnosti (2021.–2023.)",
       caption="Izvor: FINA GFI. Obrada: AI.econ") +
  th() + theme(panel.grid.major.y=element_blank(), panel.grid.major.x=element_line(color=hp$hair,linewidth=0.4))
save_png(p3,"zombie_sector.png", h=5.2)

## ---- FIG 4: tourism pre-COVID ----
tt <- afs[has_bs==TRUE & year>=2004, .(
  Turizam=100*mean(z_ne[nace=="I"]),
  `Sve firme`=100*mean(z_ne)), by=year][order(year)]
ttm <- melt(tt, id.vars="year")
p4 <- ggplot(ttm, aes(year,value,color=variable)) +
  annotate("rect", xmin=2020,xmax=2024.5,ymin=0,ymax=50, fill=hp$hair, alpha=0.5) +
  annotate("text", x=2020.2, y=8, label="COVID", hjust=0, size=3, family="mono", color=hp$muted) +
  geom_line(linewidth=1.1) +
  geom_text(data=ttm[year==max(year)], aes(label=variable), hjust=0, nudge_x=0.2, size=3, family="mono", fontface="bold") +
  scale_color_manual(values=c(Turizam=hp$fall, `Sve firme`=hp$muted), guide="none") +
  scale_x_continuous(limits=c(2004,2028), breaks=seq(2004,2024,4)) +
  scale_y_continuous(limits=c(0,50), labels=function(x)paste0(x,"%")) +
  labs(title="Turizam je bio nemrtav i prije pandemije",
       subtitle="Udio firmi s negativnim kapitalom: turizam vs sve firme",
       caption="Izvor: FINA GFI. Obrada: AI.econ") + th()
save_png(p4,"zombie_tourism.png")

cat("saved: zombie_stock.png, zombie_survival.png, zombie_sector.png, zombie_tourism.png\n")
cat(sprintf("KM median spell = %s yr | incident spells = %s\n",
    summary(fit)$table["median"], format(nrow(inc),big.mark=",")))
