import json, os
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.scrollview import ScrollView
from kivy.uix.popup import Popup
from kivy.uix.filechooser import FileChooserListView
from kivy.uix.textinput import TextInput

class AtYarisiApp(App):
    def build(self):
        self.atlar=[]
        root=BoxLayout(orientation="vertical",padding=10,spacing=8)
        root.add_widget(Label(text="🏇 AT YARIŞI ANALİZ",font_size=22,size_hint_y=None,height=50))
        info=BoxLayout(size_hint_y=None,height=45,spacing=5)
        self.hipodrom=TextInput(hint_text="Hipodrom",multiline=False)
        self.kosu=TextInput(hint_text="Koşu",multiline=False)
        self.mesafe=TextInput(hint_text="Mesafe",multiline=False)
        info.add_widget(self.hipodrom); info.add_widget(self.kosu); info.add_widget(self.mesafe)
        root.add_widget(info)
        b=Button(text="📂 YARIŞ DOSYASI SEÇ",size_hint_y=None,height=55); b.bind(on_press=self.dosya_sec); root.add_widget(b)
        b=Button(text="🏇 YARIŞI ANALİZ ET",size_hint_y=None,height=55); b.bind(on_press=self.analiz_et); root.add_widget(b)
        b=Button(text="🗑 TEMİZLE",size_hint_y=None,height=45); b.bind(on_press=self.temizle); root.add_widget(b)
        scroll=ScrollView()
        self.sonuc=Label(text="Yarış dosyası yüklenmedi.",font_size=16,halign="left",valign="top",size_hint_y=None)
        self.sonuc.bind(texture_size=lambda i,v:setattr(i,"height",v[1]+30))
        scroll.add_widget(self.sonuc); root.add_widget(scroll)
        return root

    def dosya_sec(self,*_):
        box=BoxLayout(orientation="vertical")
        chooser=FileChooserListView(path=os.getcwd(),filters=["*.json"])
        sec=Button(text="SEÇ",size_hint_y=None,height=55)
        box.add_widget(chooser); box.add_widget(sec)
        popup=Popup(title="Yarış JSON dosyasını seç",content=box,size_hint=(.95,.9))
        def secildi(*_):
            if chooser.selection:
                path=chooser.selection[0]; popup.dismiss(); self.json_yaris_oku(path)
        sec.bind(on_press=secildi); popup.open()

    def json_yaris_oku(self,path):
        try:
            with open(path,"r",encoding="utf-8") as f: veri=json.load(f)
            self.atlar=[]
            self.hipodrom.text=str(veri.get("hipodrom",""))
            self.kosu.text=str(veri.get("kosu",""))
            self.mesafe.text=str(veri.get("mesafe",""))
            for a in veri.get("atlar",[]):
                self.atlar.append({
                    "numara":a.get("numara",0),"isim":a.get("isim","İsimsiz"),
                    "form":self.form_hesapla(a.get("son6",[])),
                    "galop":float(a.get("galop",0)),"jokey":float(a.get("jokey",0)),
                    "pist":float(a.get("pist_uyumu",0)),"mesafe":float(a.get("mesafe_uyumu",0)),
                    "kilo":float(a.get("kilo",0)),"orijin":float(a.get("orijin",0)),
                    "sinif":float(a.get("sinif",0)),"kosusart":float(a.get("kosusart",0))})
            self.sonuc.text=f"✅ {len(self.atlar)} at yüklendi.\nŞimdi ANALİZ ET'e bas."
        except Exception as e: self.sonuc.text="❌ Dosya hatası:\n"+str(e)

    def form_hesapla(self,son6):
        p=[]
        for x in son6[:6]:
            try:x=int(x)
            except:continue
            p.append({1:10,2:9,3:8,4:7,5:6,6:4,7:4}.get(x,2))
        return round(sum(p)/len(p),2) if p else 0

    def puan(self,a):
        return round(a["form"]*3.5+a["galop"]*2+a["jokey"]*1.5+a["pist"]+a["mesafe"]+a["kilo"]*.5+a["orijin"]+a["sinif"]+a["kosusart"],2)

    def analiz_et(self,*_):
        if not self.atlar:
            self.sonuc.text="⚠️ Önce yarış JSON dosyası seç."; return
        for a in self.atlar:a["puan"]=self.puan(a)
        s=sorted(self.atlar,key=lambda x:x["puan"],reverse=True)
        out=f"🏇 {self.hipodrom.text} {self.kosu.text}. KOŞU\n📏 {self.mesafe.text} m\n\n📊 SIRALAMA\n"
        for i,a in enumerate(s,1):out+=f"{i}. {a['numara']} - {a['isim']} → {a['puan']}\n"
        out+="\n🏆 BİLGİSAYAR İLK 5\n"+" - ".join(str(a["numara"]) for a in s[:5])
        out+="\n\n🔥 GÜÇLÜ ADAYLAR\n"+"\n".join(f"⭐ {a['numara']} - {a['isim']}" for a in s[:2])
        if len(s)>=4:out+=f"\n\n🎯 SÜRPRİZ ADAY\n{s[3]['numara']} - {s[3]['isim']}"
        if len(s)>=2:out+=f"\n\n📈 LİDER FARKI: {s[0]['puan']-s[1]['puan']:.2f}"
        out+="\n\n⚠️ İstatistiksel analizdir; sonuç garantisi değildir."
        self.sonuc.text=out

    def temizle(self,*_):
        self.atlar=[]; self.hipodrom.text=""; self.kosu.text=""; self.mesafe.text=""
        self.sonuc.text="Yarış dosyası yüklenmedi."

if __name__=="__main__": AtYarisiApp().run()
