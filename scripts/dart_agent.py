import csv,json,os
from datetime import date
from pathlib import Path
import requests

BASE="https://opendart.fss.or.kr/api"
ROOT=Path(__file__).resolve().parents[1]
CFG=ROOT/"config"/"company.json"; RAW=ROOT/"data"/"raw"; OUT=ROOT/"data"/"processed"
KEY=os.environ.get("DART_API_KEY","").strip()
REPORTS={"annual":"11011","half_year":"11012","q1":"11013","q3":"11014"}
ALIASES={
"revenue":["매출액","영업수익","수익(매출액)","매출"],"gross_profit":["매출총이익"],
"operating_profit":["영업이익","영업이익(손실)"],"pretax_profit":["법인세비용차감전순이익","법인세비용차감전순이익(손실)","세전이익"],
"net_income":["당기순이익","당기순이익(손실)","분기순이익","반기순이익"],"assets":["자산총계"],"current_assets":["유동자산"],
"liabilities":["부채총계"],"current_liabilities":["유동부채"],"equity":["자본총계"],"cash":["현금및현금성자산"],
"inventory":["재고자산"],"receivables":["매출채권"],"payables":["매입채무"],"cfo":["영업활동현금흐름"],
"interest_expense":["이자비용","금융비용"],"depreciation":["감가상각비","감가상각비 및 무형자산상각비"]}

def api(path,params):
    if not KEY: raise RuntimeError("DART_API_KEY is not set")
    p=dict(params); p["crtfc_key"]=KEY
    r=requests.get(f"{BASE}/{path}.json",params=p,timeout=60); r.raise_for_status(); d=r.json()
    if str(d.get("status"))!="000": raise RuntimeError(f"{path}: {d.get('status')} {d.get('message')}")
    return d
def norm(x): return "".join(str(x).replace(" ","").split())
def num(x):
    if x is None or str(x).strip() in ("","-"): return None
    try:return float(str(x).replace(",",""))
    except:return None
def account(rows,aliases):
    aa=[norm(x) for x in aliases]
    for exact in (True,False):
        for a in aa:
            for r in rows:
                name=norm(r.get("account_nm",""))
                if (name==a) if exact else (a in name):
                    return num(r.get("thstrm_add_amount") or r.get("thstrm_amount"))
    return None
def filings(corp,start):
    out=[]
    for y in range(start,date.today().year+1):
        try:
            d=api("list",{"corp_code":corp,"bgn_de":f"{y}0101","end_de":f"{y}1231","page_no":1,"page_count":100})
            out += [x for x in d.get("list",[]) if any(k in x.get("report_nm","") for k in ("사업보고서","반기보고서","분기보고서"))]
        except Exception as e: out.append({"bsns_year":str(y),"status":"ERROR","message":str(e)})
    return sorted({x.get("rcept_no"):x for x in out if x.get("rcept_no")}.values(),key=lambda x:(x.get("rcept_dt",""),x.get("rcept_no","")))
def financial(corp,year,code):
    for fs in ("CFS","OFS"):
        try:
            d=api("fnlttSinglAcntAll",{"corp_code":corp,"bsns_year":str(year),"reprt_code":code,"fs_div":fs})
            if d.get("list"): return d["list"],fs
        except Exception: pass
    return [],""
def make_row(y,p,code,f,rows,fs):
    r={k:account(rows,a) for k,a in ALIASES.items()}
    r.update({"year":y,"period":p,"report_code":code,"filing_no":f.get("rcept_no",""),"filing_date":f.get("rcept_dt",""),"fs_div":fs}); return r
def add_ratios(rows):
    prev={}
    for r in sorted([x for x in rows if x["period"]=="Annual"],key=lambda x:x["year"]):
        rev,op,net,a,e=r.get("revenue"),r.get("operating_profit"),r.get("net_income"),r.get("assets"),r.get("equity")
        r["sales_growth_pct"]=(rev/prev["revenue"]-1)*100 if rev and prev.get("revenue") else None
        r["operating_margin_pct"]=op/rev*100 if op is not None and rev else None
        r["net_margin_pct"]=net/rev*100 if net is not None and rev else None
        r["debt_ratio_pct"]=r["liabilities"]/e*100 if r.get("liabilities") is not None and e else None
        r["equity_ratio_pct"]=e/a*100 if e is not None and a else None
        r["current_ratio_pct"]=r["current_assets"]/r["current_liabilities"]*100 if r.get("current_assets") is not None and r.get("current_liabilities") else None
        q=r["current_assets"]-r["inventory"] if r.get("current_assets") is not None and r.get("inventory") is not None else None
        r["quick_ratio_pct"]=q/r["current_liabilities"]*100 if q is not None and r.get("current_liabilities") else None
        r["roa_pct"]=net/((a+prev["assets"])/2)*100 if net is not None and a is not None and prev.get("assets") else None
        r["roe_pct"]=net/((e+prev["equity"])/2)*100 if net is not None and e is not None and prev.get("equity") else None
        r["interest_coverage"]=op/r["interest_expense"] if op is not None and r.get("interest_expense") not in (None,0) else None
        prev=r.copy()
def write(path,rows,fields):
    path.parent.mkdir(parents=True,exist_ok=True)
    with path.open("w",newline="",encoding="utf-8-sig") as f: csv.DictWriter(f,fieldnames=fields).writeheader(); csv.DictWriter(f,fieldnames=fields).writerows(rows)
def main():
    cfg=json.loads(CFG.read_text(encoding="utf-8")); corp=cfg["corp_code"]; start=int(cfg.get("start_year",2010))
    RAW.mkdir(parents=True,exist_ok=True); OUT.mkdir(parents=True,exist_ok=True)
    fs=filings(corp,start); (RAW/"filings.json").write_text(json.dumps({"updated_at":date.today().isoformat(),"corp_code":corp,"reports":fs},ensure_ascii=False,indent=2),encoding="utf-8")
    rows=[]
    for y in range(max(start,2015),date.today().year+1):
        for p,code in REPORTS.items():
            data,fsdiv=financial(corp,y,code)
            if not data: continue
            prefix={"annual":"사업보고서","half_year":"반기보고서","q1":"1분기보고서","q3":"3분기보고서"}[p]
            ms=[x for x in fs if x.get("rcept_no") and x.get("report_nm","").startswith(prefix) and str(x.get("bsns_year",y))==str(y)]
            rows.append(make_row(y,{"annual":"Annual","half_year":"Half-year","q1":"Q1","q3":"Q3"}[p],code,ms[-1] if ms else {},data,fsdiv))
    add_ratios(rows)
    base=["year","period","report_code","filing_no","filing_date","fs_div"]+list(ALIASES)
    rf=["sales_growth_pct","operating_margin_pct","net_margin_pct","debt_ratio_pct","equity_ratio_pct","current_ratio_pct","quick_ratio_pct","roa_pct","roe_pct","interest_coverage"]
    write(OUT/"annual.csv",[r for r in rows if r["period"]=="Annual"],base+rf)
    write(OUT/"half_year.csv",[r for r in rows if r["period"]=="Half-year"],base)
    write(OUT/"quarterly.csv",[r for r in rows if r["period"] in ("Q1","Q3")],base)
    print("DART update complete:",len(fs),"filings;",len(rows),"financial rows")
if __name__=="__main__": main()
