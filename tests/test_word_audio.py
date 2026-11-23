"""Verifies the word-by-word audio mapping for every word in the Quran.
Needs: playwright, and word_files_expected.json (built from the quran.com word dataset).
Run:  python3 tests/test_word_audio.py path/to/index.html path/to/word_files_expected.json"""
import json,sys
from playwright.sync_api import sync_playwright
html,exp=sys.argv[1],sys.argv[2]
E=json.load(open(exp))
with sync_playwright() as p:
    b=p.chromium.launch(executable_path='/usr/bin/google-chrome',args=['--no-sandbox'])
    pg=b.new_page(); errs=[]
    pg.on('pageerror',lambda x:errs.append(str(x)))
    pg.goto('file://'+html); pg.wait_for_timeout(500)
    # 1) every word of every ayah: app file name == dataset file name
    res=pg.evaluate("""(E)=>{let words=0,bad=[],disabled=0;
      for(const s of S){for(let a=1;a<=s.a.length;a++){
        const mine=s.a[a-1].split(' ').filter(x=>x.length).length;
        const exp=E[s.n+':'+a]; const f0=wordFile(s.n,a,0);
        if(exp.length!==mine){ if(f0!==0) bad.push([s.n,a,'should be disabled']); disabled+=mine; continue }
        for(let k=0;k<mine;k++){words++;
          const want=exp[k]?`wbw/${String(s.n).padStart(3,'0')}_${String(a).padStart(3,'0')}_${String(exp[k]).padStart(3,'0')}.mp3`:0;
          if(wordFile(s.n,a,k)!==want) bad.push([s.n,a,k+1,wordFile(s.n,a,k),want])}}}
      return {words,bad:bad.slice(0,10),nbad:bad.length,disabled}}""",E)
    print('words checked',res['words'],'| mismatches',res['nbad'],res['bad'],'| words in disabled verses',res['disabled'])
    # 2) real taps: the URL requested for the tapped word
    reqs=[]
    pg.route('https://audio.qurancdn.com/**',lambda r:(reqs.append(r.request.url),r.fulfill(status=200,body=b'',content_type='audio/mpeg')))
    cases=[(2,2,5),(2,2,6),(2,2,7),(1,1,3),(2,255,10),(36,52,7)]
    for s,a,k in cases:
        pg.evaluate(f"go({s},{a})"); pg.wait_for_timeout(250)
        pg.evaluate(f"document.querySelector('#a{a} .w[data-k=\"{k-1}\"]').click()"); pg.wait_for_timeout(250)
        got=reqs[-1].split('/')[-1] if reqs else None
        print(f'tap {s}:{a} word {k} ->',got if (s,a,k)!=(36,52,7) else (got,'(no file for this word; expect toast)'))
        reqs.clear()
    print('page errors',errs)
    ok=res['nbad']==0 and not errs
    b.close(); sys.exit(0 if ok else 1)
