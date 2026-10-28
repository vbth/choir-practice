(function(){
var D=window.PAGE,$=function(s,r){return (r||document).querySelector(s)},$$=function(s,r){return Array.prototype.slice.call((r||document).querySelectorAll(s))};
// menu
var bar=$('.bar'),bg=$('.burger');
bg.addEventListener('click',function(){var o=bar.classList.toggle('open');bg.setAttribute('aria-expanded',o)});
$$('#nav a').forEach(function(a){a.addEventListener('click',function(){bar.classList.remove('open');bg.setAttribute('aria-expanded',false)})});
if('IntersectionObserver' in window){
 var links={};$$('#nav a[href^="#"]').forEach(function(a){links[a.getAttribute('href').slice(1)]=a});
 var io=new IntersectionObserver(function(es){es.forEach(function(e){if(e.isIntersecting){$$('#nav a').forEach(function(a){a.removeAttribute('aria-current')});var a=links[e.target.id];if(a)a.setAttribute('aria-current','true')}})},{rootMargin:'-45% 0px -50% 0px'});
 $$('main section').forEach(function(s){io.observe(s)});
}
// hero: the sub head wraps at the width of the headline (measured from its lines); on phones it keeps the full width
function fitLead(){var h=$('.hero h1'),l=$('.hero .lead');if(!h||!l)return;l.style.maxWidth='';if(window.innerWidth<760)return;var r=document.createRange();r.selectNodeContents(h);var a=1e9,z=0;
 Array.prototype.forEach.call(r.getClientRects(),function(q){if(q.width>1){a=Math.min(a,q.left);z=Math.max(z,q.right)}});if(z>a)l.style.maxWidth=Math.ceil(z-a)+'px'}
fitLead();if(document.fonts&&document.fonts.ready)document.fonts.ready.then(fitLead);window.addEventListener('load',fitLead);
// light / dark switch: system setting by default, the choice is kept in localStorage
(function(){var root=document.documentElement,tb=$('.theme'),mq=window.matchMedia('(prefers-color-scheme: dark)');if(!tb)return;
function dark(){var t=root.getAttribute('data-theme');return t?t==='dark':mq.matches}
function apply(){var d=dark(),t=root.getAttribute('data-theme'),src=$('.banner picture source');tb.className='theme '+(d?'is-dark':'is-light');tb.setAttribute('aria-label',d?D.theme_to_light:D.theme_to_dark);
 if(src)src.media=t==='dark'?'all':t==='light'?'not all':'(prefers-color-scheme: dark)'}
tb.addEventListener('click',function(){var t=dark()?'light':'dark';root.setAttribute('data-theme',t);try{localStorage.setItem('theme',t)}catch(e){}apply()});
if(mq.addEventListener)mq.addEventListener('change',apply);apply()})();
// folder tree
$$('.folder button').forEach(function(b){b.addEventListener('click',function(){var o=b.getAttribute('aria-expanded')==='true';b.setAttribute('aria-expanded',!o);document.getElementById(b.getAttribute('aria-controls')).hidden=o})});
// workflow chain
function showStep(i){
 $$('.chain button').forEach(function(b){b.setAttribute('aria-pressed',b.getAttribute('data-step')==i)});
 var s=D.steps[i],box=$('#stepbox');box.innerHTML='';
 var h=document.createElement('h3');h.innerHTML='<span>'+(i+1)+' – '+s[0]+'</span><span class="who">'+D.who[s[1]]+'</span>';
 var p=document.createElement('p');p.textContent=s[2];box.appendChild(h);box.appendChild(p);
 if(s[3]){var g=document.createElement('p');g.className='gate';g.textContent=D.gate+': '+s[3];box.appendChild(g)}
}
$$('.chain button').forEach(function(b){b.addEventListener('click',function(){showStep(+b.getAttribute('data-step'))})});
showStep(0);
// headphone mix
var NS='http://www.w3.org/2000/svg',svg=$('#hp'),cur={voice:'S',stage:'choir',sound:'choir',tempo:'normal'};
function el(n,a,t){var e=document.createElementNS(NS,n);for(var k in a)e.setAttribute(k,a[k]);if(t!=null)e.textContent=t;return e}
function rad(db){return Math.max(15,34+1.33*db)}
function draw(){
 while(svg.lastChild)svg.removeChild(svg.lastChild);
 var sw=1.5,col='currentColor',x0=320,half=250,W=svg.getBoundingClientRect().width||640,FS=Math.round(10*15*588/W)/10;
 // over-ear headphones seen from the front, line art: steel frame, mesh canopy, telescopic arms, cups with cushions facing in, crown on the right cup
 var mob=W<600,oy=mob?200:230,ay=mob?338:312,py=mob?388:352;
 svg.setAttribute('viewBox','26 -53 588 '+(mob?453:419));
 function ln(d,w){svg.appendChild(el('path',{d:d,fill:'none',stroke:col,'stroke-width':w||sw*2,'stroke-linecap':'round','stroke-linejoin':'round'}))}
 ln('M47 128 L47 120 A273 165 0 0 1 593 120 L593 128 L581 128 L581 120 A261 147 0 0 0 59 120 L59 128 Z');
 ln('M47 128 h12 v8 h-12 Z M581 128 h12 v8 h-12 Z',sw*1.5);
 ln('M30 160 C30 142 40 136 53 136 C66 136 76 142 76 160 L76 286 C76 304 66 310 53 310 C40 310 30 304 30 286 Z');
 ln('M564 160 C564 142 574 136 587 136 C600 136 610 142 610 160 L610 286 C610 304 600 310 587 310 C574 310 564 304 564 286 Z');
 ln('M76 156 C88 156 92 164 92 174 L92 272 C92 282 88 290 76 290',sw*1.5);
 ln('M564 156 C552 156 548 164 548 174 L548 272 C548 282 552 290 564 290',sw*1.5);
 var list=D.mix[cur.stage][cur.voice],own=[],acc=[];
 list.forEach(function(e){(e[3]==='acc'?acc:own).push(e)});
 function pos(e){return x0+e[1]*190}
 own.forEach(function(e,i){var y=oy;
  var g=el('g',{});var r=rad(e[2]);
  g.appendChild(el('circle',{cx:pos(e),cy:y,r:r,fill:'none',stroke:col,'stroke-width':e[0]===cur.voice&&e[2]===0?sw*3:sw*1.5}));
  g.appendChild(el('text',{x:pos(e),y:y+5,'font-size':FS,'text-anchor':'middle','font-weight':700},e[0]));
  g.appendChild(el('text',{x:pos(e),y:y+r+(mob?FS*0.95+3:16),'font-size':FS,'text-anchor':'middle'},e[2]+(mob&&i>0?'':' dB')));
  svg.appendChild(g);});
 acc.forEach(function(e){var y=ay,r=rad(e[2]);
  svg.appendChild(el('circle',{cx:pos(e),cy:y,r:r,fill:'none',stroke:col,'stroke-width':sw,'stroke-dasharray':'4 4'}));
  svg.appendChild(el('text',{x:pos(e),y:y+4,'font-size':FS,'text-anchor':'middle'},e[0]));});
 if(acc.length){svg.appendChild(el('text',{x:x0,y:py,'font-size':FS,'text-anchor':'middle'},D.acc+' ('+acc[0][2]+' dB)'))}
 svg.setAttribute('aria-label',D.voices[cur.voice]+', '+D.stages[cur.stage]);   // no <title>: it would show a tooltip on hover
 $('#hpcap').textContent=D.stage_txt[cur.stage];
}
// one state (voice, stage, sound, tempo) drives the headphones, the buttons, the playlist and the audio
var pl=$('#player'),A=$('#plaudio'),sk=$('#plseek'),tm=$('#pltime'),base=pl.getAttribute('data-audio');
function slowOk(){return cur.stage==='solo'||cur.stage==='accomp'}
function isSlow(){return slowOk()&&cur.tempo==='slow'}
function file(){return cur.stage==='tutti'?'tutti_'+cur.sound:cur.voice.toLowerCase()+'_'+cur.stage+'_'+cur.sound+(isSlow()?'_slow':'')}
function label(){return (cur.stage==='tutti'?D.stages.tutti:D.voices[cur.voice]+', '+D.stages[cur.stage])+', '+D.sound_names[cur.sound]+(isSlow()?', '+D.slow_name:'')}
function f(t){t=Math.floor(t||0);return Math.floor(t/60)+':'+('0'+t%60).slice(-2)}
function ui(){var on=!A.paused;$$('.picon').forEach(function(i){i.setAttribute('d',on?'M6 4h4v16H6zM14 4h4v16h-4z':'M7 4l13 8-13 8z')});$$('.pbtn').forEach(function(b){b.setAttribute('aria-label',pl.getAttribute(on?'data-pause':'data-play'))})}
function sync(){
 draw();
 $$('#voices button').forEach(function(b){b.setAttribute('aria-pressed',b.getAttribute('data-voice')===cur.voice)});
 $$('#stages button').forEach(function(b){b.setAttribute('aria-pressed',b.getAttribute('data-stage')===cur.stage)});
 $$('#sounds button').forEach(function(b){b.setAttribute('aria-pressed',b.getAttribute('data-sound')===cur.sound)});
 $$('#tempos button').forEach(function(b){b.setAttribute('aria-pressed',b.getAttribute('data-tempo')===(slowOk()?cur.tempo:'normal'))});
 $('#tempoctl').hidden=!slowOk();
 var k=file();
 $$('.trk button').forEach(function(b){var st=b.getAttribute('data-stage'),vo=b.getAttribute('data-voice')||cur.voice,sl=b.getAttribute('data-tempo')==='slow';
  b.setAttribute('aria-pressed',st===cur.stage&&b.getAttribute('data-sound')===cur.sound&&(st==='tutti'||vo===cur.voice)&&sl===isSlow())});
 $$('.groups details').forEach(function(d){d.open=cur.stage==='tutti'?d.hasAttribute('data-tutti'):d.getAttribute('data-voice')===cur.voice});   // only the group of the chosen voice is open
 $('#plname').textContent=$('#hpname').textContent=label();
 var u=base+k+'.mp3';if(A.getAttribute('src')!==u)A.setAttribute('src',u);
}
// change the selection; keep the playing position (scaled when the tempo changes), or start the chosen recording when asked
function change(fn,restart){
 var was=!A.paused,t=A.currentTime||0,ps=isSlow();fn();var ns=isSlow();sync();
 if(restart){sk.value=0;tm.textContent='0:00';A.play().catch(function(){});return}
 if(was){var sc=(ns?1/D.slow:1)/(ps?1/D.slow:1);A.addEventListener('loadedmetadata',function h(){A.removeEventListener('loadedmetadata',h);A.currentTime=Math.min(t*sc,Math.max(0,(A.duration||t*sc)-0.2))});A.play().catch(function(){})}
 else{sk.value=0;tm.textContent='0:00'}
}
$$('#voices button').forEach(function(b){b.addEventListener('click',function(){change(function(){cur.voice=b.getAttribute('data-voice')},A.paused)})});
$$('#stages button').forEach(function(b){b.addEventListener('click',function(){change(function(){cur.stage=b.getAttribute('data-stage')},A.paused)})});
$$('#sounds button').forEach(function(b){b.addEventListener('click',function(){change(function(){cur.sound=b.getAttribute('data-sound')},A.paused)})});
$$('#tempos button').forEach(function(b){b.addEventListener('click',function(){change(function(){cur.tempo=b.getAttribute('data-tempo')},A.paused)})});
$$('.trk button').forEach(function(b){b.addEventListener('click',function(){change(function(){var v=b.getAttribute('data-voice');if(v)cur.voice=v;cur.stage=b.getAttribute('data-stage');cur.sound=b.getAttribute('data-sound');cur.tempo=b.getAttribute('data-tempo')},true)})});
$$('.pbtn').forEach(function(b){b.addEventListener('click',function(){if(A.paused){A.play().catch(function(){})}else{A.pause()}})});
A.addEventListener('play',ui);A.addEventListener('pause',ui);
A.addEventListener('timeupdate',function(){if(A.duration)sk.value=Math.round(A.currentTime/A.duration*1000);tm.textContent=f(A.currentTime)});
A.addEventListener('loadedmetadata',function(){tm.textContent=f(A.currentTime)});
A.addEventListener('ended',function(){ui();sk.value=0});
sk.addEventListener('input',function(){if(A.duration)A.currentTime=sk.value/1000*A.duration});
sync();ui();
window.addEventListener('resize',function(){clearTimeout(window.__rz);window.__rz=setTimeout(function(){draw();fitLead()},150)});
})();
