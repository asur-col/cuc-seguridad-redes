// Auditoría visual: captura cada diapositiva (1280x720) y reporta desbordes.
// Uso: node herramientas/auditar_presentacion.js 2026-2-S07-....html salida/
// Requiere Playwright (npm i playwright) o PLAYWRIGHT_PATH apuntando al módulo.
const { chromium } = require(process.env.PLAYWRIGHT_PATH || 'playwright');
const path=require('path'),fs=require('fs');
(async()=>{
  const [file,out]=process.argv.slice(2); fs.mkdirSync(out,{recursive:true});
  const b=await chromium.launch(); const p=await b.newPage({viewport:{width:1280,height:720}});
  await p.goto('file://'+path.resolve(file)); await p.waitForTimeout(1500);
  const n=await p.evaluate(()=>document.querySelectorAll('.slide').length);
  const report=[];
  for(let i=0;i<n;i++){
    const r=await p.evaluate((i)=>{
      const ss=document.querySelectorAll('.slide'); ss.forEach((s,j)=>s.classList.toggle('active',j===i));
      const st=document.getElementById('stage'); if(st) st.style.transform='none';
      const s=ss[i]; const sb=s.getBoundingClientRect(); const foot=s.querySelector('.s-foot');
      const fb=foot?foot.getBoundingClientRect().top:sb.bottom;
      let issues=[];
      s.querySelectorAll('*').forEach(e=>{ if(e.closest('.s-foot')||e.closest('svg')&&e.tagName!=='svg') return;
        const b=e.getBoundingClientRect(); if(b.width===0||b.height===0) return;
        if(b.right>sb.right+1||b.bottom>sb.bottom+1) issues.push('fuera:'+e.tagName+'.'+e.className);
        else if(foot && b.bottom>fb+1 && !e.closest('.cover')) issues.push('pisa-pie:'+e.tagName+'.'+(e.className.baseVal??e.className));
        if(e.scrollHeight>e.clientHeight+2 && getComputedStyle(e).overflow!=='visible') issues.push('scroll:'+e.tagName);
      });
      return [...new Set(issues)].slice(0,4);
    },i);
    await p.waitForTimeout(150);
    const el=await p.$('#stage')||p;
    await el.screenshot({path:`${out}/s${String(i+1).padStart(2,'0')}.png`});
    if(r.length) report.push(`${i+1}: ${r.join(' ')}`);
  }
  console.log(path.basename(file), n, 'slides'); console.log(report.join('\n')||'sin desbordes');
  await b.close();
})();
