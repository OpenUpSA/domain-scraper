# -*- coding: utf-8 -*-
import scrapy
from urllib.parse import urlparse, urlunparse
from govzasurvey.items import PageItem, RobotsTXTItem, NetlocItem, FileItem
from os.path import splitext
import logging

logger = logging.getLogger(__name__)

file_extensions = set([
    'jpg', 'pdf', 'doc', 'docx', 'xls', 'xlsx', 'gz', 'mp3',
    'ppt', 'pptx', 'mp4', 'avi', 'zip', 'jpeg', 'gif', 'png', 'bmp',
    'accdb', 'cdf', 'csv', 'dbf', 'dem', 'dta', 'e00', 'esri', 'fits',
    'json', 'geojson', 'gridfloat', 'hdf', 'ifc', 'ddf', 'kml', 'las',
    'matlab', 'mdb', 'nsf', 'odf', 'ods', 'rdata', 'rda', 'sas', 'sdts',
    'siard', 'spss', 'por', 'sav',
])

netlocs = dict()


class GovzaSpider(scrapy.Spider):
    name = 'govza'
    allowed_domains = ['gov.za']

    def parse(self, response):
        try:
            page_text = response.text
        except AttributeError as e:
            if e.args[0] == "Response content isn't text":
                file_item = FileItem()
                file_item["url"] = response.url
                yield file_item
                return
            else:
                raise e

        page_item = PageItem()
        page_item['url'] = response.url
        page_item['referrer'] = response.url
        page_item['etag'] = response.headers.get("etag", None)
        page_item['html'] = page_text
        yield page_item

        scheme, netloc, path, params, query, fragment = urlparse(response.url)

        if netloc in netlocs:
            netlocs[netloc] += 1
        else:
            netlocs[netloc] = 1

            # try the robots.txt the first time we see a netloc
            robotsurl = urlunparse((scheme, netloc, '/robots.txt', None, None, None))
            yield scrapy.Request(robotsurl, callback=self.parse_robotstxt)

            # yield the netloc the first time we see it
            netloc_item = NetlocItem()
            netloc_item['netloc'] = netloc
            yield netloc_item

        for anchor in response.xpath("//a"):
            href = anchor.xpath("@href").extract()
            if href:
                href = href[0]
            else:
                # Skip in-page navigation anchor points
                continue

            label = anchor.xpath("text()").extract()

            if label:
                label = label[0].strip()
            else:
                label = None

            # Make it absolute if it is not
            url = response.urljoin(href)

            # If it's an email link, use the domain as the URL
            if url.startswith('mailto:'):
                if '@' in url:
                    url = 'http://' + url.split('@')[1]
                else:
                    continue

            if url.startswith('javascript:'):
                continue
            if url.startswith('mailto:'):
                continue
            if url.startswith('tel'):
                continue

            # only handle the first 1000 links discovered for a given netloc
            # to try and minimise the impact of relative links that just append and
            # append and keep returning 200
            parsed = urlparse(url)
            netloc_seen = netlocs.get(parsed.netloc, 0)
            if netloc_seen >= 1000:
                logger.info("Skipping %s - already seen enough from %s", url, parsed.netloc)
                continue

            # log but skip obvious non-html (before stripping QS)
            path, extension = splitext(parsed.path)
            if extension and extension[1:] in file_extensions:
                file_item = FileItem()
                file_item['url'] = url
                file_item['label'] = label
                yield file_item
                continue

            # remove qs
            if '?' in url:
                url = url.split('?')[0]

            # avoid endless expansion
            if len(url) > 300:
                logger.info("Skipping url > 300 chars %s", url)
                continue

            # crawl it
            yield scrapy.Request(url)

    def parse_robotstxt(self, response):
        item = RobotsTXTItem()
        item['url'] = response.url
        item['robotstxt'] = response.text
        yield item


    start_urls = [
        "http://www.gov.za/",
        "http://pixleykaseme.local.gov.za",
        "http://www.abaqulusi.gov.za",
        "http://www.aganang.gov.za",
        "http://www.albertluthuli.gov.za",
        "http://www.amahlathi.gov.za",
        "http://www.amajuba.gov.za",
        "http://www.amathole.gov.za",
        "http://www.andm.gov.za/site/",
        "http://www.ba-phalaborwa.gov.za",
        "http://www.bcrm.gov.za",
        "http://www.belabela.gov.za",
        "http://www.big5hlabisa.gov.za",
        "http://www.blouberg.gov.za",
        "http://www.bojanala.gov.za",
        "http://www.buffalocity.gov.za",
        "http://www.bushbuckridge.gov.za",
        "http://www.bvm.gov.za",
        "http://www.camdeboo.gov.za",
        "http://www.capeagulhas.gov.za",
        "http://www.capetown.gov.za",
        "http://www.capewinelands.gov.za",
        "http://www.cederbergmunicipality.gov.za",
        "http://www.chrishanidm.gov.za",
        "http://www.dannhauser.gov.za",
        "http://www.dipaleseng.gov.za",
        "http://www.drakenstein.gov.za",
        "http://www.drjsmlm.gov.za",
        "http://www.durban.gov.za",
        "http://www.ecprov.gov.za/Inkwancalm",
        "http://www.edumbe.gov.za",
        "http://www.ekurhuleni.gov.za",
        "http://www.eliasmotsoaledi.gov.za",
        "http://www.elundini.gov.za",
        "http://www.emadlangeni.gov.za",
        "http://www.emalahleni.gov.za",
        "http://www.emalahlenilm.gov.za",
        "http://www.emfuleni.gov.za",
        "http://www.endumeni.gov.za",
        "http://www.ephraimmogalelm.gov.za",
        "http://www.ezingoleni.gov.za",
        "http://www.fetakgomo.gov.za",
        "http://www.feziledabi.gov.za",
        "http://www.francesbaard.gov.za",
        "http://www.gariep.gov.za",
        "http://www.ga-segonyana.gov.za",
        "http://www.george.gov.za",
        "http://www.govanmbeki.gov.za",
        "http://www.greatergiyani.gov.za",
        "http://www.greaterletaba.gov.za",
        "http://www.greatertaung.gov.za",
        "http://www.greatkeilm.gov.za",
        "http://www.gsibande.gov.za",
        "http://www.hantam.gov.za",
        "http://www.hessequa.gov.za",
        "http://www.ihlm.gov.za",
        "http://www.ilembe.gov.za",
        "http://www.imbabazane.org.za",
        "http://www.impendle.gov.za",
        "http://www.ingwe.gov.za",
        "http://www.intsikayethu.gov.za",
        "http://www.jgdm.gov.za",
        "http://www.joemorolong.gov.za",
        "http://www.kaigarib.gov.za",
        "http://www.kannaland.gov.za",
        "http://www.karoohoogland.gov.za",
        "http://www.kaundadistrict.gov.za",
        "http://www.kgatelopele.gov.za",
        "http://www.kgetlengrivier.gov.za",
        "http://www.khaima.gov.za",
        "http://www.kharahais.gov.za",
        "http://www.kingcetshwayo.gov.za",
        "http://www.knysna.gov.za",
        "http://www.kopanong.gov.za",
        "http://www.kougamunicipality.gov.za",
        "http://www.kwadukuza.gov.za",
        "http://www.laingsburg.gov.za",
        "http://www.langeberg.gov.za",
        "http://www.lepelle-nkumpi.gov.za",
        "http://www.lephalale.gov.za",
        "http://www.lesedi.gov.za",
        "http://www.letsemeng.gov.za",
        "http://www.lim345.gov.za",
        "http://www.madibeng.gov.za",
        "http://www.mafikeng.gov.za",
        "http://www.mafubemunicipality.gov.za",
        "http://www.magareng.gov.za",
        "http://www.makana.gov.za",
        "http://www.makhado.gov.za",
        "http://www.makhuduthamaga.gov.za",
        "http://www.maletswai.gov.za",
        "http://www.mandelametro.gov.za",
        "http://www.mandeni.gov.za",
        "http://www.mantsopa.fs.gov.za",
        "http://www.map.fs.gov.za",
        "http://www.maphumuloonline.gov.za",
        "http://www.maruleng.gov.za",
        "http://www.masilonyana.local.gov.za",
        "http://www.matatiele.gov.za",
        "http://www.matjhabeng.fs.gov.za",
        "http://www.matlosana.org.za",
        "http://www.matzikamamun.co.za",
        "http://www.mbhashemun.gov.za",
        "http://www.mbizana.gov.za",
        "http://www.mbombela.gov.za",
        "http://www.merafong.co.za",
        "http://www.metsimaholo.gov.za",
        "http://www.mhlontlolm.gov.za",
        "http://www.midvaal.gov.za",
        "http://www.mkhambathini.gov.za",
        "http://www.mkhondo.gov.za",
        "http://www.mnquma.gov.za",
        "http://www.modimolle.gov.za",
        "http://www.mogalakwena.gov.za",
        "http://www.mogalecity.gov.za",
        "http://www.mohokare.gov.za",
        "http://www.molemole.gov.za",
        "http://www.mopani.gov.za",
        "http://www.moseskotane.gov.za",
        "http://www.mpofana.gov.za",
        "http://www.msukaligwa.gov.za",
        "http://www.msunduzi.gov.za",
        "http://www.musina.gov.za",
        "http://www.mutale.gov.za",
        "http://www.namakhoi.gov.za",
        "http://www.namakwa-dm.gov.za",
        "http://www.ndwedwe.gov.za",
        "http://www.ndz.gov.za",
        "http://www.newcastle.gov.za",
        "http://www.ngqushwamun.gov.za",
        "http://www.ngwathe.fs.gov.za",
        "http://www.nkangaladm.gov.za",
        "http://www.nketoanafs.gov.za",
        "http://www.nkomazi.gov.za",
        "http://www.nquthu.gov.za",
        "http://www.nyandenilm.gov.za",
        "http://www.oudtmun.gov.za",
        "http://www.overstrand.gov.za",
        "http://www.pamun.gov.za",
        "http://www.phokwane.gov.za",
        "http://www.phumelelamun.co.za",
        "http://www.plett.gov.za",
        "http://www.polokwane.gov.za",
        "http://www.ramotshere.gov.za",
        "http://www.randwestcity.gov.za",
        "http://www.raymondmhlaba.gov.za",
        "http://www.richmond.gov.za",
        "http://www.richtersveld.gov.za",
        "http://www.rnm.gov.za",
        "http://www.rsmompatidm.gov.za",
        "http://www.rustenburg.gov.za",
        "http://www.sakhisizwe.gov.za",
        "http://www.sbm.gov.za",
        "http://www.sedibeng.gov.za",
        "http://www.sekhukhune.gov.za",
        "http://www.senqu.gov.za",
        "http://www.setsoto.co.za",
        "http://www.sisonke.gov.za",
        "http://www.siyancuma.gov.za",
        "http://www.siyathemba.gov.za",
        "http://www.stellenbosch.gov.za",
        "http://www.stevetshwetelm.gov.za",
        "http://www.taologaetsewe.gov.za",
        "http://www.thabachweumun.gov.za",
        "http://www.thabazimbi.gov.za",
        "http://www.thembelihlemunicipality.gov.za",
        "http://www.thembisilehanilm.gov.za",
        "http://www.thulamela.gov.za",
        "http://www.tshwane.gov.za",
        "http://www.tswaing.gov.za",
        "http://www.tswelopele.gov.za",
        "http://www.tubatse.gov.za",
        "http://www.tzaneen.gov.za",
        "http://www.ubuhlebezwe.gov.za",
        "http://www.ubuntu.gov.za",
        "http://www.ukdm.gov.za",
        "http://www.ulundi.gov.za",
        "http://www.umdm.gov.za",
        "http://www.umdoni.gov.za",
        "http://www.umfolozi.gov.za",
        "http://www.umhlabuyalingana.gov.za",
        "http://www.umhlathuze.gov.za",
        "http://www.umjindi.gov.za",
        "http://www.umngeni.gov.za",
        "http://www.umuziwabantu.gov.za",
        "http://www.umvoti.gov.za",
        "http://www.umzimkhululm.gov.za",
        "http://www.umzinyathi.gov.za",
        "http://www.umzumbe.gov.za",
        "http://www.vhembe.gov.za",
        "http://www.waterberg.gov.za",
        "http://www.westonaria.gov.za",
        "http://www.witzenberg.gov.za",
        "http://www.wrdm.gov.za",
        "http://www.xhariep.gov.za",
        "http://www.zfm-dm.gov.za",
    ]
