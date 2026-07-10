# HERO figure: county choropleth of negative-equity share (the "zombie coast").
suppressWarnings(suppressMessages({library(data.table); library(sf); library(ggplot2); library(giscoR)}))
# house palette + theme (mirrors R/house_style.R; inlined to avoid the config/.env loader)
house_pal <- list(paper="#F7F7F4", ink="#18181B", muted="#71717A", hair="#E6E6E1",
                  accent="#2348E5", rise="#1C8F5A", fall="#D2463A", surface="#ECE9E1",
                  amber="#C77B30", purple="#6D4AA6")
theme_house <- function(base_size=12) ggplot2::theme_minimal(base_size=base_size, base_family="mono") +
  ggplot2::theme(
    plot.background=ggplot2::element_rect(fill=house_pal$paper, color=NA),
    panel.background=ggplot2::element_rect(fill=house_pal$paper, color=NA),
    plot.title.position="plot", plot.caption.position="plot",
    plot.title=ggplot2::element_text(face="bold", color=house_pal$ink, hjust=0, size=base_size+3),
    plot.subtitle=ggplot2::element_text(color=house_pal$muted, hjust=0, size=base_size-2.5, margin=ggplot2::margin(t=4,b=12)),
    plot.caption=ggplot2::element_text(color=house_pal$muted, hjust=0, size=base_size-4, margin=ggplot2::margin(t=12)),
    axis.text=ggplot2::element_text(color=house_pal$muted, size=base_size-3),
    axis.title=ggplot2::element_blank(), axis.ticks=ggplot2::element_blank(),
    panel.grid.minor=ggplot2::element_blank(), panel.grid.major.x=ggplot2::element_blank(),
    panel.grid.major.y=ggplot2::element_line(color=house_pal$hair, linewidth=0.4),
    plot.margin=ggplot2::margin(14,18,10,14))

## --- data: negative-equity share by county, avg 2021-2023 (has balance sheet) ---
afs <- readRDS("data/raw/zombie_extract_v2.rds")
afs <- afs[!is.na(oib) & oib!="" & grepl("^[A-U]$", nace) & nace!="K"]
afs[, has_bs := !is.na(assets) & assets>0]
cty <- afs[has_bs==TRUE & year %in% 2021:2023,
           .(ne = 100*mean(!is.na(equity) & equity<0),
             emp_ne = 100*sum(emp[!is.na(equity)&equity<0], na.rm=TRUE)/sum(emp, na.rm=TRUE)),
           by=county]
names_dt <- data.table(county=1:21, naziv=c("Zagrebačka","Krapinsko-zagorska","Sisačko-moslavačka",
  "Karlovačka","Varaždinska","Koprivničko-križevačka","Bjelovarsko-bilogorska","Primorsko-goranska",
  "Ličko-senjska","Virovitičko-podravska","Požeško-slavonska","Brodsko-posavska","Zadarska",
  "Osječko-baranjska","Šibensko-kninska","Vukovarsko-srijemska","Splitsko-dalmatinska","Istarska",
  "Dubrovačko-neretvanska","Međimurska","Grad Zagreb"))
cty <- names_dt[cty, on="county"]

## --- county id -> NUTS-3 crosswalk (from the plan) ---
xw <- data.table(county=1:21, NUTS_ID=c("HR065","HR064","HR028","HR027","HR062","HR063","HR021",
  "HR031","HR032","HR022","HR023","HR024","HR033","HR025","HR034","HR026","HR035","HR036","HR037",
  "HR061","HR050"))
cty <- xw[cty, on="county"]

## --- boundaries ---
hr <- gisco_get_nuts(year=2021, nuts_level=3, resolution="03", country="HR", epsg=4326)
setDT(cty)
map <- merge(hr, as.data.frame(cty), by="NUTS_ID", all.x=TRUE)
map <- st_transform(st_as_sf(map), 3765)   # HTRS96/TM
map$lab <- paste0(round(map$ne), "%")

## --- plot ---
p <- ggplot(map) +
  geom_sf(aes(fill=ne), color=house_pal$paper, linewidth=0.35) +
  geom_sf_text(aes(label=lab), size=2.7, color=house_pal$ink, family="mono", fontface="bold") +
  scale_fill_stepsn(colors=c("#F1E7D8","#E8C9A6","#D98E63","#CC5B44","#A8342B"),
                    n.breaks=6, name="Firme s\nnegativnim\nkapitalom (%)",
                    guide=guide_colorsteps(barheight=6, barwidth=0.8)) +
  labs(title="Zombi obala",
       subtitle="Udio firmi s negativnim kapitalom, po županijama (2021.–2023.)",
       caption="Izvor: FINA GFI. Nefinancijske firme s bilancom. Obrada: AI.econ") +
  theme_house(base_size=13) +
  theme(axis.text=element_blank(), panel.grid=element_blank(),
        plot.subtitle=element_text(size=10),
        legend.title=element_text(size=8, color=house_pal$muted),
        legend.text=element_text(size=8, color=house_pal$muted))

dir.create("outputs/figures", showWarnings=FALSE, recursive=TRUE)
ggsave("outputs/figures/zombie_map.png", p, width=8.6, height=6.4, dpi=150, device=ragg::agg_png)
cat("saved outputs/figures/zombie_map.png\n")
print(cty[order(-ne), .(naziv, ne=round(ne,1), emp_ne=round(emp_ne,1))])
