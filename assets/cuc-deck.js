// Navegación de las presentaciones CUC. Parámetros de URL:
//   ?s=N        abre en la diapositiva N (1-based)
//   ?captura=1  oculta la navegación (para capturas de PDF/video)
(function(){
  const slides=[...document.querySelectorAll('.slide')];
  const counter=document.getElementById('counter');
  const progress=document.getElementById('progress');
  const stage=document.getElementById('stage');
  const q=new URLSearchParams(location.search);
  if(q.get('captura')) document.body.classList.add('captura');
  let cur=0;
  function show(i){
    i=Math.max(0,Math.min(slides.length-1,i));
    slides.forEach((s,k)=>s.classList.toggle('active',k===i));
    cur=i;
    if(counter) counter.textContent=`${i+1} / ${slides.length}`;
    if(progress) progress.style.width=`${(i+1)/slides.length*100}%`;
    if(history.replaceState && !q.get('captura')) history.replaceState(null,'',`#${i+1}`);
  }
  function fit(){
    if(document.body.classList.contains('captura')){stage.style.transform='none';return;}
    const s=Math.min(innerWidth/1280,innerHeight/720)*0.97;
    stage.style.transform=`scale(${s})`;
  }
  window.irA=show; window.totalDiapositivas=slides.length;
  document.getElementById('prev')?.addEventListener('click',()=>show(cur-1));
  document.getElementById('next')?.addEventListener('click',()=>show(cur+1));
  document.addEventListener('keydown',e=>{
    if(['ArrowRight',' ','PageDown'].includes(e.key)) show(cur+1);
    if(['ArrowLeft','PageUp'].includes(e.key)) show(cur-1);
    if(e.key==='Home') show(0);
    if(e.key==='End') show(slides.length-1);
  });
  addEventListener('resize',fit); fit();
  const h=parseInt((location.hash||'').slice(1)); const n=parseInt(q.get('s'));
  show(!isNaN(n)?n-1:(!isNaN(h)?h-1:0));
})();
