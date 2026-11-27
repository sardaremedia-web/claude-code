// node render_range.js out.mp4 startFrame endFrame workers  (30fps, renders [a,b))
const {chromium}=require('playwright');const {spawn,execFileSync}=require('child_process');const path=require('path');const fs=require('fs');
(async()=>{const out=process.argv[2],A=+process.argv[3],B=+process.argv[4],W=+(process.argv[5]||4),fps=30;
 const b=await chromium.launch();const per=Math.ceil((B-A)/W);const parts=[];
 await Promise.all([...Array(W).keys()].map(async w=>{const p=await b.newPage({viewport:{width:1080,height:1920}});await p.goto('file://'+path.resolve(__dirname,'reel.html'));await p.evaluate(()=>document.fonts.ready);await p.waitForTimeout(800);
  const a=A+w*per,z=Math.min(B,a+per),seg=`${out}.p${w}.mp4`;parts[w]=seg;
  const ff=spawn('ffmpeg',['-y','-v','error','-f','image2pipe','-framerate',''+fps,'-i','-','-c:v','libx264','-preset','medium','-crf','16','-pix_fmt','yuv420p',seg],{stdio:['pipe','inherit','inherit']});
  for(let i=a;i<z;i++){await p.evaluate(t=>seek(t),i/fps);const buf=await p.screenshot({type:'jpeg',quality:93});if(!ff.stdin.write(buf))await new Promise(r=>ff.stdin.once('drain',r))}
  ff.stdin.end();await new Promise(r=>ff.on('close',r));await p.close()}));
 await b.close();fs.writeFileSync(out+'.txt',parts.map(p=>`file '${path.resolve(p)}'`).join('\n'));execFileSync('ffmpeg',['-y','-v','error','-f','concat','-safe','0','-i',out+'.txt','-c','copy',out]);parts.forEach(p=>fs.unlinkSync(p));fs.unlinkSync(out+'.txt');console.log('DONE')})();
