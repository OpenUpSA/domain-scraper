# -*- coding: utf-8 -*-
import scrapy
from urlparse import urlparse
from govzasurvey.items import GovzasurveyItem


class GovzaSpider(scrapy.Spider):
    name = 'govza'
    allowed_domains = ['gov.za']

    def parse(self, response):
        has_wordpress = 'wordpress' in response.text.lower()
        item = GovzasurveyItem()
        item['url'] = response.url
        item['has_wordpress'] = has_wordpress
        yield item

        for href in response.css("a::attr('href')"):
            url = response.urljoin(href.extract())
            if url.startswith('mailto:') and '@' in url:
                url = 'http://' + url.split('@')[1]

            # ensure absolute
            parsed = urlparse(url)
            if not parsed.netloc:
                url = response.urljoin(url)

            # remove qs
            if '?' in url:
                url = url.split('?')[0]

            # crawl it
            yield scrapy.Request(url)

    start_urls = [
        "http://www.gov.za/",
        "http://pixleykaseme.local.gov.za",
        "http://tokologo.org.za/",
        "http://www.abaqulusi.gov.za",
        "http://www.aganang.gov.za",
        "http://www.albertluthuli.gov.za",
        "http://www.amahlathi.gov.za",
        "http://www.amajuba.gov.za",
        "http://www.amathole.gov.za",
        "http://www.andm.gov.za/site/",
        "http://www.ba-phalaborwa.gov.za",
        "http://www.baviaans.co.za",
        "http://www.bcrm.gov.za",
        "http://www.beaufortwestmun.co.za",
        "http://www.belabela.gov.za",
        "http://www.bergmun.org.za",
        "http://www.big5falsebay.co.za",
        "http://www.big5hlabisa.gov.za",
        "http://www.blouberg.gov.za",
        "http://www.bojanala.gov.za",
        "http://www.buffalocity.gov.za",
        "http://www.bushbuckridge.gov.za",
        "http://www.bvm.gov.za",
        "http://www.cacadu.co.za",
        "http://www.camdeboo.gov.za",
        "http://www.capeagulhas.gov.za",
        "http://www.capetown.gov.za",
        "http://www.capewinelands.gov.za",
        "http://www.cdm.org.za",
        "http://www.cederbergmunicipality.gov.za",
        "http://www.chrishanidm.gov.za",
        "http://www.dannhauser.gov.za",
        "http://www.delmasmunic.co.za",
        "http://www.dihlabeng.co.za",
        "http://www.dipaleseng.gov.za",
        "http://www.ditsobotla.co.za",
        "http://www.drakenstein.gov.za",
        "http://www.drjsmlm.gov.za",
        "http://www.durban.gov.za",
        "http://www.ecprov.gov.za/Inkwancalm",
        "http://www.edendm.co.za",
        "http://www.edumbe.gov.za",
        "http://www.ehlanzeni.co.za",
        "http://www.ekurhuleni.gov.za",
        "http://www.eliasmotsoaledi.gov.za",
        "http://www.elundini.gov.za",
        "http://www.emadlangeni.gov.za",
        "http://www.emakhazenilm.co.za",
        "http://www.emalahleni.gov.za",
        "http://www.emalahlenilm.gov.za",
        "http://www.emfuleni.gov.za",
        "http://www.emthanjeni.co.za",
        "http://www.endumeni.gov.za",
        "http://www.ephraimmogalelm.gov.za",
        "http://www.ezingoleni.gov.za",
        "http://www.fetakgomo.gov.za",
        "http://www.feziledabi.gov.za",
        "http://www.francesbaard.gov.za",
        "http://www.gamagara.co.za",
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
        "http://www.hlabisa.org.za",
        "http://www.ihlm.gov.za",
        "http://www.ikwezimunicipality.co.za",
        "http://www.ilembe.gov.za",
        "http://www.imbabazane.org.za",
        "http://www.impendle.gov.za",
        "http://www.ingwe.gov.za",
        "http://www.intsikayethu.gov.za",
        "http://www.jgdm.gov.za",
        "http://www.joburg.org.za",
        "http://www.joemorolong.gov.za",
        "http://www.jozini.org.za",
        "http://www.kaigarib.gov.za",
        "http://www.kamiesbergmun.co.za",
        "http://www.kannaland.gov.za",
        "http://www.kareeberg.co.za",
        "http://www.karoohoogland.gov.za",
        "http://www.kaundadistrict.gov.za",
        "http://www.kgatelopele.gov.za",
        "http://www.kgetlengrivier.gov.za",
        "http://www.khaima.gov.za",
        "http://www.kharahais.gov.za",
        "http://www.kheismun.co.za",
        "http://www.kingcetshwayo.gov.za",
        "http://www.knysna.gov.za",
        "http://www.kokstad.org.za",
        "http://www.kopanong.gov.za",
        "http://www.kougamunicipality.gov.za",
        "http://www.koukammamunicipality.co.za",
        "http://www.ksd.org.za",
        "http://www.kwadukuza.gov.za",
        "http://www.kwasani.co.za",
        "http://www.ladysmith.co.za",
        "http://www.laingsburg.gov.za",
        "http://www.langeberg.gov.za",
        "http://www.lejwe.co.za",
        "http://www.lekwateemane.co.za",
        "http://www.lepelle-nkumpi.gov.za",
        "http://www.lephalale.gov.za",
        "http://www.lesedi.gov.za",
        "http://www.letsemeng.gov.za",
        "http://www.lim345.gov.za",
        "http://www.lukhanji.co.za",
        "http://www.madibeng.gov.za",
        "http://www.mafikeng.gov.za",
        "http://www.mafubemunicipality.gov.za",
        "http://www.magareng.gov.za",
        "http://www.makana.gov.za",
        "http://www.makhado.gov.za",
        "http://www.makhuduthamaga.gov.za",
        "http://www.maletswai.gov.za",
        "http://www.mamusalm.co.za",
        "http://www.mandelametro.gov.za",
        "http://www.mandeni.gov.za",
        "http://www.mangaung.co.za",
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
        "http://www.mosselbaymun.co.za",
        "http://www.mpofana.gov.za",
        "http://www.msinga.org.za",
        "http://www.msukaligwa.gov.za",
        "http://www.msunduzi.gov.za",
        "http://www.mthonjaneni.org.za",
        "http://www.mtubatuba.org.za",
        "http://www.musina.gov.za",
        "http://www.mutale.gov.za",
        "http://www.nala.org.za",
        "http://www.naledilm.co.za",
        "http://www.namakhoi.gov.za",
        "http://www.namakwa-dm.gov.za",
        "http://www.ndlambe.co.za",
        "http://www.ndwedwe.gov.za",
        "http://www.ndz.gov.za",
        "http://www.newcastle.gov.za",
        "http://www.ngqushwamun.gov.za",
        "http://www.ngwathe.fs.gov.za",
        "http://www.nkandla.co.za",
        "http://www.nkangaladm.gov.za",
        "http://www.nketoanafs.gov.za",
        "http://www.nkomazi.gov.za",
        "http://www.nkonkobe.co.za",
        "http://www.nongoma.org.za",
        "http://www.nquthu.gov.za",
        "http://www.ntambanana.org.za",
        "http://www.nxuba.co.za",
        "http://www.nyandenilm.gov.za",
        "http://www.odm.org.za",
        "http://www.okhahlamba.org.za",
        "http://www.ortambodm.org.za",
        "http://www.oudtmun.gov.za",
        "http://www.overstrand.gov.za",
        "http://www.pamun.gov.za",
        "http://www.phokwane.gov.za",
        "http://www.phumelelamun.co.za",
        "http://www.pixley.co.za",
        "http://www.plett.gov.za",
        "http://www.polokwane.gov.za",
        "http://www.potch.co.za",
        "http://www.psjlm.co.za",
        "http://www.ramotshere.gov.za",
        "http://www.randfontein.org.za",
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
        "http://www.skdm.co.za",
        "http://www.solplaatje.org.za",
        "http://www.srvm.co.za",
        "http://www.stellenbosch.gov.za",
        "http://www.stevetshwetelm.gov.za",
        "http://www.swartland.org.za",
        "http://www.swellenmun.co.za",
        "http://www.taologaetsewe.gov.za",
        "http://www.thabachweumun.gov.za",
        "http://www.thabazimbi.gov.za",
        "http://www.thabomofutsanyanadm.co.za",
        "http://www.thembelihlemunicipality.gov.za",
        "http://www.thembisilehanilm.gov.za",
        "http://www.thulamela.gov.za",
        "http://www.tsantsabane.co.za",
        "http://www.tshwane.gov.za",
        "http://www.tsolwana.co.za",
        "http://www.tswaing.gov.za",
        "http://www.tswelopele.gov.za",
        "http://www.tubatse.gov.za",
        "http://www.twk.org.za",
        "http://www.tzaneen.gov.za",
        "http://www.ubuhlebezwe.gov.za",
        "http://www.ubuntu.gov.za",
        "http://www.ugu.org.za",
        "http://www.ukdm.gov.za",
        "http://www.ulundi.gov.za",
        "http://www.umdm.gov.za",
        "http://www.umdoni.gov.za",
        "http://www.umfolozi.gov.za",
        "http://www.umhlabuyalingana.gov.za",
        "http://www.umhlathuze.gov.za",
        "http://www.umjindi.gov.za",
        "http://www.umlalazi.org.za",
        "http://www.umngeni.gov.za",
        "http://www.umsobomvumun.co.za",
        "http://www.umtshezi.co.za",
        "http://www.umuziwabantu.gov.za",
        "http://www.umvoti.gov.za",
        "http://www.umzimkhululm.gov.za",
        "http://www.umzimvubu.org.za",
        "http://www.umzinyathi.gov.za",
        "http://www.umzumbe.gov.za",
        "http://www.uphongolo.org.za",
        "http://www.uthukeladm.co.za",
        "http://www.ventersdorp.co.za",
        "http://www.vhembe.gov.za",
        "http://www.vulamehlo.org.za",
        "http://www.waterberg.gov.za",
        "http://www.westcoastdm.co.za",
        "http://www.westonaria.gov.za",
        "http://www.witzenberg.gov.za",
        "http://www.wrdm.gov.za",
        "http://www.xhariep.gov.za",
        "http://www.zfm-dm.gov.za",
        "http://www.zululand.org.za",
    ]
