// parallel render: node render_par.js out.mp4 workers
const {chromium}=require('playwright');const {spawn,execFileSync}=require('child_process');const path=require('path');const fs=require('fs');
(async()=>{const out=process.argv[2],W=+(process.argv[3]||4),fps=30;
 const b=await chromium.launch();
 const probe=await b.newPage();await probe.goto('file://'+path.resolve(__dirname,'reel.html'));const dur=await probe.evaluate(()=>DUR);await probe.close();
 const N=Math.round(dur*fps),per=Math.ceil(N/W);const parts=[];
 await Promise.all([...Array(W).keys()].map(async w=>{
  const p=await b.newPage({viewport:{width:1080,height:1920}});await p.goto('file://'+path.resolve(__dirname,'reel.html'));
  await p.evaluate(()=>document.fonts.ready);await p.waitForTimeout(800);
  const a=w*per,z=Math.min(N,a+per),seg=`${out}.part${w}.mp4`;parts[w]=seg;
  const ff=spawn('ffmpeg',['-y','-v','error','-f','image2pipe','-framerate',''+fps,'-i','-','-c:v','libx264','-preset','medium','-crf','16','-pix_fmt','yuv420p',seg],{stdio:['pipe','inherit','inherit']});
  for(let i=a;i<z;i++){await p.evaluate(t=>seek(t),i/fps);const buf=await p.screenshot({type:'jpeg',quality:93});if(!ff.stdin.write(buf))await new Promise(r=>ff.stdin.once('drain',r));if((i-a)%100==0)console.log('w',w,i-a,'/',z-a)}
  ff.stdin.end();await new Promise(r=>ff.on('close',r));await p.close()}));
 await b.close();fs.writeFileSync(out+'.txt',parts.map(p=>`file '${path.resolve(p)}'`).join('\n'));
 execFileSync('ffmpeg',['-y','-v','error','-f','concat','-safe','0','-i',out+'.txt','-c','copy',out]);parts.forEach(p=>fs.unlinkSync(p));fs.unlinkSync(out+'.txt');console.log('DONE')})();
