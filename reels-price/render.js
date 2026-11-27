// usage: node render.js out.mp4 [stills t1,t2,...]
const {chromium}=require('playwright');const {spawn}=require('child_process');const path=require('path');
(async()=>{const out=process.argv[2];const stills=process.argv[3];
 const b=await chromium.launch();const p=await b.newPage({viewport:{width:1080,height:1920}});
 await p.goto('file://'+path.resolve(__dirname,'reel.html'));await p.evaluate(()=>document.fonts.ready);await p.waitForTimeout(800);
 if(stills){for(const s of stills.split(',')){await p.evaluate(t=>seek(t),+s);await p.screenshot({path:`${out}_${s}.jpg`,type:'jpeg',quality:80})}await b.close();return}
 const fps=30,dur=await p.evaluate(()=>DUR),N=Math.round(dur*fps);
 const ff=spawn('ffmpeg',['-y','-v','error','-f','image2pipe','-framerate',''+fps,'-i','-','-c:v','libx264','-preset','medium','-crf','16','-pix_fmt','yuv420p',out],{stdio:['pipe','inherit','inherit']});
 for(let i=0;i<N;i++){await p.evaluate(t=>seek(t),i/fps);const buf=await p.screenshot({type:'jpeg',quality:93});if(!ff.stdin.write(buf))await new Promise(r=>ff.stdin.once('drain',r));if(i%150==0)console.log('frame',i,'/',N)}
 ff.stdin.end();await new Promise(r=>ff.on('close',r));await b.close()})();
