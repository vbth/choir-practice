(function(){
var D=window.PAGE,$=function(s,r){return (r||document).querySelector(s)},$$=function(s,r){return Array.prototype.slice.call((r||document).querySelectorAll(s))};
// menu
var bar=$('.bar'),bg=$('.burger');
bg.addEventListener('click',function(){var o=bar.classList.toggle('open');bg.setAttribute('aria-expanded',o)});
function barH(){document.documentElement.style.setProperty('--barh',bar.offsetHeight+'px')}
barH();window.addEventListener('resize',barH);window.addEventListener('load',barH);
// a menu click always scrolls to its section; layout shifts during the smooth scroll (late images, fonts) are corrected afterwards
$$('#nav a[href^="#"]').forEach(function(a){a.addEventListener('click',function(e){
 bar.classList.remove('open');bg.setAttribute('aria-expanded',false);
 var t=document.getElementById(a.getAttribute('href').slice(1));if(!t)return;e.preventDefault();
 function y(){return Math.max(0,Math.round(t.getBoundingClientRect().top+window.pageYOffset-bar.offsetHeight))}
 window.scrollTo({top:y(),behavior:'smooth'});
 try{history.replaceState(null,'',a.getAttribute('href'))}catch(x){}
 setTimeout(function(){if(Math.abs(window.pageYOffset-y())>2)window.scrollTo({top:y(),behavior:'auto'})},900)})});
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
function nb(t){var i=t.lastIndexOf(' ');return i>0?t.slice(0,i)+String.fromCharCode(160)+t.slice(i+1):t}   // last two words stay together
function showStep(i){
 $$('.chain button').forEach(function(b){b.setAttribute('aria-pressed',b.getAttribute('data-step')==i)});
 var s=D.steps[i],box=$('#stepbox');box.innerHTML='';
 var h=document.createElement('h3');h.innerHTML='<span>'+(i+1)+' – '+s[0]+'</span><span class="who">'+D.who[s[1]]+'</span>';
 var p=document.createElement('p');p.textContent=nb(s[2]);box.appendChild(h);box.appendChild(p);
 if(s[3]){var g=document.createElement('p');g.className='gate';g.textContent=nb(D.gate+': '+s[3]);box.appendChild(g)}
}
$$('.chain button').forEach(function(b){b.addEventListener('click',function(){showStep(+b.getAttribute('data-step'))})});
showStep(0);
// headphone mix
var NS='http://www.w3.org/2000/svg',svg=$('#hp'),cur={voice:'S',stage:'choir',sound:'choir',tempo:'normal'};
function el(n,a,t){var e=document.createElementNS(NS,n);for(var k in a)e.setAttribute(k,a[k]);if(t!=null)e.textContent=t;return e}
function rad(db){return Math.max(15,34+1.33*db)}
function mob0(W){return W<600}
function draw(){
 while(svg.lastChild)svg.removeChild(svg.lastChild);
 var sw=1.5,col='currentColor',x0=320,half=250,GAP=24,VW=656+2*GAP,W=svg.getBoundingClientRect().width||640,FS=Math.round(10*15*VW/W)/10,LS=mob0(W)?FS:Math.round(FS*15)/10;
 // over-ear headphones seen from the front, line art: steel frame, mesh canopy, telescopic arms, cups with cushions facing in, crown on the right cup
 var mob=mob0(W),oy=mob?200:230,ay=mob?338:312,py=mob?388:352;
 svg.setAttribute('viewBox',(-8-GAP)+' -53 '+VW+' '+(mob?453:419));
 function ln(d,w,dx){svg.appendChild(el('path',{d:d,fill:'none',stroke:col,'stroke-width':w||sw*2,'stroke-linecap':'round','stroke-linejoin':'round',transform:'translate('+(dx||0)+' 0)'}))}   // dx: shifts a cup outwards
 ln('M'+(47-GAP)+' 128 L'+(47-GAP)+' 120 A'+(273+GAP)+' 165 0 0 1 '+(593+GAP)+' 120 L'+(593+GAP)+' 128 L'+(581+GAP)+' 128 L'+(581+GAP)+' 120 A'+(261+GAP)+' 147 0 0 0 '+(59-GAP)+' 120 L'+(59-GAP)+' 128 Z');
 ln('M47 128 h12 v8 h-12 Z',sw*1.5,-GAP);ln('M581 128 h12 v8 h-12 Z',sw*1.5,GAP);
 ln('M30 160 C30 142 40 136 53 136 C66 136 76 142 76 160 L76 286 C76 304 66 310 53 310 C40 310 30 304 30 286 Z',null,-GAP);
 ln('M564 160 C564 142 574 136 587 136 C600 136 610 142 610 160 L610 286 C610 304 600 310 587 310 C574 310 564 304 564 286 Z',null,GAP);
 ln('M76 156 C88 156 92 164 92 174 L92 272 C92 282 88 290 76 290',sw*1.5,-GAP);
 ln('M564 156 C552 156 548 164 548 174 L548 272 C548 282 552 290 564 290',sw*1.5,GAP);
 // sound waves between cup and ear, travelling inwards, red; only visible while a recording plays (class 'playing' on the svg).
 // The circles never reach further out than x=121 (or 519 on the right); the whole headphones are GAP=24 units wider on each side, so the waves end at x=92 (or 548) and the gap to the circles is at least 29 units
 [0,1,2].forEach(function(i){var x=102+5*i,h=20+10*i,c=x+6;
  [[x-GAP,c-GAP],[640-x+GAP,640-c+GAP]].forEach(function(p){svg.appendChild(el('path',{'class':'wave',d:'M'+p[0]+' '+(223-h)+' Q'+p[1]+' 223 '+p[0]+' '+(223+h),fill:'none',stroke:'var(--link)','stroke-width':sw*1.7,'stroke-linecap':'round',style:'animation-delay:'+(i*0.25)+'s'}))})});
 var list=D.mix[cur.stage][cur.voice],own=[],acc=[];
 list.forEach(function(e){(e[3]==='acc'?acc:own).push(e)});
 function pos(e){return x0+e[1]*(cur.stage==='tutti'?270:190)}   // tutti: circles further apart
 own.forEach(function(e,i){var y=oy;
  var g=el('g',{'class':'vb',role:'button',tabindex:0,'aria-label':D.voices[e[0]],'aria-pressed':e[0]===cur.voice});var r=rad(e[2]);
  var pick=function(){change(function(){cur.voice=e[0]},true)};   // the circles switch the voice, like the voice buttons
  g.addEventListener('click',pick);g.addEventListener('keydown',function(ev){if(ev.key==='Enter'||ev.key===' '){ev.preventDefault();pick()}});
  g.appendChild(el('circle',{cx:pos(e),cy:y,r:r,fill:'none','pointer-events':'all',stroke:col,'stroke-width':e[0]===cur.voice&&e[2]===0?sw*3:sw*1.5}));
  g.appendChild(el('text',{x:pos(e),y:y,dy:'.35em','font-size':Math.min(LS,1.5*r),'text-anchor':'middle','font-weight':700},e[0]));   // dy: cap height centred in the circle
  g.appendChild(el('text',{x:pos(e),y:y+r+(mob?FS*0.95+3:16),'font-size':FS,'text-anchor':'middle'},e[2]+(mob&&i>0?'':' dB')));
  svg.appendChild(g);});
 acc.forEach(function(e){var y=ay,r=rad(e[2]);
  svg.appendChild(el('circle',{cx:pos(e),cy:y,r:r,fill:'none',stroke:col,'stroke-width':sw,'stroke-dasharray':'4 4'}));
  svg.appendChild(el('text',{x:pos(e),y:y,dy:'.35em','font-size':FS,'text-anchor':'middle'},e[0]));});
 if(acc.length){svg.appendChild(el('text',{x:x0,y:py,'font-size':FS,'text-anchor':'middle'},D.acc+' ('+acc[0][2]+' dB)'))}
 svg.setAttribute('aria-label',D.voices[cur.voice]+', '+D.stages[cur.stage]);   // no <title>: it would show a tooltip on hover
 $('#hpcap').textContent=nb(D.stage_txt[cur.stage]);
}
// one state (voice, stage, sound, tempo) drives the headphones, the buttons, the playlist and the audio
var pl=$('#player'),A=$('#plaudio'),sk=$('#plseek'),tm=$('#pltime'),base=pl.getAttribute('data-audio');
function slowOk(){return cur.stage==='solo'||cur.stage==='accomp'}
function isSlow(){return slowOk()&&cur.tempo==='slow'}
function file(){return cur.stage==='tutti'?'tutti_'+cur.sound:cur.voice.toLowerCase()+'_'+cur.stage+'_'+cur.sound+(isSlow()?'_slow':'')}
function label(){return (cur.stage==='tutti'?D.stages.tutti:D.voices[cur.voice]+', '+D.stages[cur.stage])+', '+D.sound_names[cur.sound]+(isSlow()?', '+D.slow_name:'')}
function f(t){t=Math.floor(t||0);return Math.floor(t/60)+':'+('0'+t%60).slice(-2)}
function ui(){var on=!A.paused;svg.classList.toggle('playing',on);$$('.picon').forEach(function(i){var c=i.hasAttribute('data-c');i.setAttribute('d',on?(c?'M6 4h4v16H6zM14 4h4v16h-4z':'M6.3 4.4Q8.2 4 10.1 4.5Q10.4 12 9.9 19.7Q8 20.2 6.1 19.6Q6.6 12 6.3 4.4ZM14.2 4.3Q16.1 4 18 4.6Q18.4 12 17.9 19.8Q16 20.1 14.1 19.7Q14.5 12 14.2 4.3Z'):(c?'M7 4l13 8-13 8z':'M7.2 4.6Q13.5 8.4 19.6 12.1Q13.3 15.9 7.4 19.6Q7.8 12 7.2 4.6Z'))});$$('.pbtn').forEach(function(b){b.setAttribute('aria-label',pl.getAttribute(on?'data-pause':'data-play'))})}
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
 if(restart){sk.value=0;tm.textContent='0:00';try{A.currentTime=0}catch(e){}A.play().catch(function(){});return}
 if(was){var sc=(ns?1/D.slow:1)/(ps?1/D.slow:1);A.addEventListener('loadedmetadata',function h(){A.removeEventListener('loadedmetadata',h);A.currentTime=Math.min(t*sc,Math.max(0,(A.duration||t*sc)-0.2))});A.play().catch(function(){})}
 else{sk.value=0;tm.textContent='0:00'}
}
$$('#voices button').forEach(function(b){b.addEventListener('click',function(){change(function(){cur.voice=b.getAttribute('data-voice')},true)})});
$$('#stages button').forEach(function(b){b.addEventListener('click',function(){change(function(){cur.stage=b.getAttribute('data-stage')},A.paused)})});
$$('#sounds button').forEach(function(b){b.addEventListener('click',function(){change(function(){cur.sound=b.getAttribute('data-sound')},A.paused)})});
$$('#tempos button').forEach(function(b){b.addEventListener('click',function(){change(function(){cur.tempo=b.getAttribute('data-tempo')},A.paused)})});
$$('.trk button').forEach(function(b){b.addEventListener('click',function(){change(function(){var v=b.getAttribute('data-voice');if(v)cur.voice=v;cur.stage=b.getAttribute('data-stage');cur.sound=b.getAttribute('data-sound');cur.tempo=b.getAttribute('data-tempo')},true)})});
$$('.pbtn').forEach(function(b){b.addEventListener('click',function(){if(A.paused){A.play().catch(function(){})}else{A.pause()}})});
// volume: the slider and the speaker button exist twice (remote on the header image, player); both follow one value (no effect on iPhones: the system volume rules there)
var vols=$$('.vol'),mutes=$$('.mute'),lastVol=.5;
function setVol(v){v=Math.max(0,Math.min(1,v));A.volume=v;$$('.vp').forEach(function(e){e.textContent=Math.round(v*100)+'\u00a0%'});vols.forEach(function(r){r.value=Math.round(v*100)});mutes.forEach(function(m){m.setAttribute('aria-pressed',v===0)})}
vols.forEach(function(r){r.addEventListener('input',function(){lastVol=+r.value/100||lastVol;setVol(+r.value/100)})});
mutes.forEach(function(m){m.addEventListener('click',function(){if(A.volume>0){lastVol=A.volume;setVol(0)}else setVol(lastVol||.5)})});
setVol(.5);   // starts at half volume
// remote control on the cover (shown while the pointer is over it): previous / next recording of the playlist, repeat
function step(d){var all=$$('.trk button'),i=0;all.forEach(function(b,k){if(b.getAttribute('aria-pressed')==='true')i=k});all[(i+d+all.length)%all.length].click()}
$('.ov .prev').addEventListener('click',function(){step(-1)});$('.ov .next').addEventListener('click',function(){step(1)});
// first touch on the header image: the remote grows from the single play button to the full set (and the recording starts); with a mouse nothing changes
var hw=$('.hw');
function activate(){hw.classList.add('on')}
$('.ov .pbtn').addEventListener('click',activate);
hw.addEventListener('click',function(e){if(hw.classList.contains('on'))return;activate();if(!e.target.closest('.ov')&&A.paused)A.play().catch(function(){})});
A.addEventListener('play',ui);A.addEventListener('pause',ui);
// sound waves pulse with the rhythm of the recording: Web Audio analyser on the audio element; every note onset (level jumps more than 2.5 dB above its slow average) switches the three arcs per side on, they then go off again from the outside in; while it sounds the inner arc stays on (always full red, no fading).
// Onset rate on the example recordings: 2 to 4 per second. Without Web Audio, with reduced motion or if the context cannot run, the fixed animation stays
var live=null;
function startLive(){
 if(live!==null||(window.matchMedia&&matchMedia('(prefers-reduced-motion:reduce)').matches))return;
 live=false;
 var AC=window.AudioContext||window.webkitAudioContext;if(!AC)return;
 try{
  var cx=new AC();
  var build=function(){
   if(cx.state!=='running'){try{cx.close()}catch(e){}return}   // an element routed into a suspended context would be silent
   var an=cx.createAnalyser();an.fftSize=1024;var sr=cx.createMediaElementSource(A);sr.connect(an);an.connect(cx.destination);
   live={cx:cx,an:an,buf:new Uint8Array(an.fftSize),slow:null,pulse:0,last:0,t:0,raf:0,on:[false,false,false]};svg.classList.add('live');if(!A.paused)loop()};
  if(cx.state==='running')build();else cx.resume().then(build,function(){})
 }catch(e){}
}
function stopLoop(){if(live&&live.raf){cancelAnimationFrame(live.raf);live.raf=0}if(live){live.on=[false,false,false];live.slow=null;live.pulse=0}$$('#hp .wave').forEach(function(w){w.style.opacity=''})}
function loop(now){
 if(!live||A.paused){stopLoop();return}
 now=now||performance.now();
 var b=live.buf,q=0,i;live.an.getByteTimeDomainData(b);for(i=0;i<b.length;i++){var x=(b[i]-128)/128;q+=x*x}
 var db=20*Math.log10(Math.sqrt(q/b.length)+1e-6),dt=Math.min(100,live.t?now-live.t:16);live.t=now;
 if(live.slow===null)live.slow=db;
 var flux=db-live.slow;   // jump above the slow average = note onset
 if(flux>2.5&&db>-45&&now-live.last>110){live.pulse=Math.min(1,0.55+flux/10);live.last=now}
 live.pulse*=Math.pow(0.92,dt*0.06);live.slow+=(1-Math.pow(0.95,dt*0.06))*(db-live.slow);   // per 60 Hz frame: pulse x0.92, average 5 %
 var v=Math.max(live.pulse,db>-25?0.35:0);   // inner arc stays on while it sounds
 for(i=0;i<3;i++){var th=0.25*(i+1);if(live.on[i]?v<th-0.04:v>th+0.04)live.on[i]=!live.on[i]}   // thresholds 0.25 / 0.5 / 0.75 with hysteresis against flicker
 for(i=1;i<3;i++)if(!live.on[i-1])live.on[i]=false;   // an outer arc is only on while the inner one is
 var ws=svg.querySelectorAll('.wave');for(i=0;i<ws.length;i++)ws[i].style.opacity=live.on[Math.floor(i/2)]?1:0;   // order of creation: both sides of arc 0, then arc 1, arc 2
 live.raf=requestAnimationFrame(loop)}
document.addEventListener('click',function(e){if(e.target.closest&&e.target.closest('button'))startLive()},true);   // created inside a click, so the context may run
A.addEventListener('play',function(){if(live&&!live.raf){if(live.cx.state==='suspended')live.cx.resume();loop()}});
A.addEventListener('pause',stopLoop);A.addEventListener('ended',stopLoop);
A.addEventListener('timeupdate',function(){if(A.duration)sk.value=Math.round(A.currentTime/A.duration*1000);tm.textContent=f(A.currentTime)});
A.addEventListener('loadedmetadata',function(){tm.textContent=f(A.currentTime)});
A.addEventListener('ended',function(){ui();sk.value=0});
sk.addEventListener('input',function(){if(A.duration)A.currentTime=sk.value/1000*A.duration});
sync();ui();
// mixer: the stems (4 voices, piano, starting notes) play together through Web Audio; every voice has an on/off button and its own level; the room reverb is added here
(function(){
var mx=$('#mix');if(!mx)return;
var AC=window.AudioContext||window.webkitAudioContext,base=mx.getAttribute('data-audio'),play=$('#mxplay'),ic=$('#mxicon'),seek=$('#mxseek'),time=$('#mxtime');
var names=['s','a','t','b','acc','intro'],cx=null,bufs=null,gains={},srcs=[],t0=0,off=0,dur=0,playing=false,raf=0,loading=false;
var PLAY='M7 4l13 8-13 8z',PAUSE='M6 4h4v16H6zM14 4h4v16h-4z';
function fmt(t){t=Math.floor(t||0);return Math.floor(t/60)+':'+('0'+t%60).slice(-2)}
function rows(){return $$('.mxr',mx)}
function level(r){var b=$('.mxb',r),v=+$('.mxv',r).value/100;return b.getAttribute('aria-pressed')==='true'?v*v:0}   // squared: the slider follows the loudness we hear
function apply(){rows().forEach(function(r){var k=$('.mxb',r).getAttribute('data-stem');if(gains[k])gains[k].gain.setTargetAtTime(level(r),cx.currentTime,.02)})}
function setIcon(on){ic.setAttribute('d',on?PAUSE:PLAY);play.setAttribute('aria-label',on?pl.getAttribute('data-pause'):pl.getAttribute('data-play'))}
function ir(c){var rt=1.3,n=Math.floor(c.sampleRate*rt*1.2),b=c.createBuffer(2,n,c.sampleRate);   // synthetic room: decaying noise
 for(var ch=0;ch<2;ch++){var d=b.getChannelData(ch);for(var i=0;i<n;i++)d[i]=(Math.random()*2-1)*Math.exp(-6.9*(i/c.sampleRate)/rt)*.35}return b}
function setup(){
 cx=new AC();var master=cx.createGain(),lim=cx.createDynamicsCompressor();lim.threshold.value=-6;lim.ratio.value=8;lim.attack.value=.003;lim.release.value=.15;
 var wet=cx.createGain(),cv=cx.createConvolver();wet.gain.value=.3;cv.buffer=ir(cx);master.connect(lim);master.connect(cv);cv.connect(wet);wet.connect(lim);lim.connect(cx.destination);
 names.forEach(function(k){var g=cx.createGain(),p=cx.createStereoPanner?cx.createStereoPanner():null,b=$('.mxb[data-stem="'+k+'"]',mx);g.gain.value=1;
  if(p){p.pan.value=b?+b.getAttribute('data-pan'):0;g.connect(p);p.connect(master)}else g.connect(master);gains[k]=g});
}
function load(){
 if(bufs||loading)return Promise.resolve();loading=true;mx.setAttribute('aria-busy','true');
 return Promise.all(names.map(function(k){return fetch(base+k+'.mp3').then(function(r){return r.arrayBuffer()}).then(function(a){return new Promise(function(ok,no){cx.decodeAudioData(a,ok,no)})})})).then(function(l){
  bufs={};names.forEach(function(k,i){bufs[k]=l[i]});dur=Math.max.apply(null,l.map(function(b){return b.duration}));loading=false;mx.removeAttribute('aria-busy');apply()});
}
function stopSrc(){srcs.forEach(function(s){try{s.onended=null;s.stop()}catch(e){}});srcs=[]}
function pos(){return playing?Math.min(dur,off+cx.currentTime-t0):off}
function tick(){var p=pos();seek.value=dur?Math.round(p/dur*1000):0;time.textContent=fmt(p);if(playing)raf=requestAnimationFrame(tick)}
function start(from){
 stopSrc();off=from;t0=cx.currentTime+.05;
 names.forEach(function(k){var s=cx.createBufferSource();s.buffer=bufs[k];s.connect(gains[k]);s.start(t0,from);srcs.push(s)});
 srcs[0].onended=function(){if(playing&&pos()>=dur-.1)finish()};
 playing=true;setIcon(true);cancelAnimationFrame(raf);tick();
}
function pause(){if(!playing)return;off=pos();playing=false;stopSrc();setIcon(false);cancelAnimationFrame(raf);tick()}
function finish(){playing=false;stopSrc();off=0;setIcon(false);cancelAnimationFrame(raf);tick()}
play.addEventListener('click',function(){
 if(!AC)return;if(playing){pause();return}
 if(!cx)setup();if(cx.state==='suspended')cx.resume();
 A.pause();   // only one thing plays at a time
 load().then(function(){start(off>=dur-.1?0:off)}).catch(function(){loading=false;mx.removeAttribute('aria-busy')});
});
seek.addEventListener('input',function(){if(!bufs)return;var p=seek.value/1000*dur;if(playing)start(p);else{off=p;time.textContent=fmt(p)}});
rows().forEach(function(r){var b=$('.mxb',r),v=$('.mxv',r),pc=$('.mxp2',r);
 function upd(){pc.innerHTML=v.value+'&nbsp;%';r.classList.toggle('off',b.getAttribute('aria-pressed')!=='true');if(cx)apply()}
 b.addEventListener('click',function(){b.setAttribute('aria-pressed',b.getAttribute('aria-pressed')!=='true');upd()});
 v.addEventListener('input',upd)});
A.addEventListener('play',pause);   // the recordings below take over
document.addEventListener('visibilitychange',function(){if(!document.hidden&&playing)tick()});
})();
window.addEventListener('resize',function(){clearTimeout(window.__rz);window.__rz=setTimeout(function(){draw();fitLead()},150)});
})();
