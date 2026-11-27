# Cuts the source into the reel's shot list -> footage.mp4 (1080x1920, 30fps, no audio)
import subprocess
# (src_in, out_duration, speed) ; speed<1 = slow motion
SHOTS=[(30.5,2.9,1),(53.64,2.4,1),(43.58,2.2,1),(6.6,2.1,1),(3.96,2.3,1),(24.6,2.9,1),(22.5,2.6,0.8),
(13.3,3.28,1),(36.3,2.7,1),(9.8,2.5,1),(27.6,2.4,1),(0.2,2.3,1),(57.58,2.6,1),(60.2,2.1,1),(41.46,2.1,1),
(46.2,2.2,1),(39.06,1.8,1),(62.54,2.0,1),(69.76,4.2,0.8)]
import os
os.makedirs('shots',exist_ok=True);lst=[]
for i,(s,d,sp) in enumerate(SHOTS):
    srcd=d*sp; z=0.06 if i%2==0 else 0.045
    vf=(f"setpts=(PTS-STARTPTS)/{sp},fps=30,scale=w='trunc(1080*(1+{z}*t/{d})/2)*2':h=-2:eval=frame,crop=1080:1920,setsar=1,"
        "eq=contrast=1.05:saturation=1.08:gamma=0.98,colorbalance=rm=0.04:bm=-0.04:rh=0.03:bh=-0.03,vignette=PI/5")
    out=f"shots/{i:02d}.mp4"
    subprocess.run(["ffmpeg","-v","error","-y","-ss",str(s),"-t",f"{srcd:.3f}","-i","src/src.mp4","-an","-vf",vf,"-frames:v",str(round(d*30)),"-c:v","libx264","-preset","medium","-crf","15","-pix_fmt","yuv420p","-r","30",out],check=True)
    lst.append(f"file '{os.path.abspath(out)}'")
open('shots/list.txt','w').write("\n".join(lst))
subprocess.run(["ffmpeg","-v","error","-y","-f","concat","-safe","0","-i","shots/list.txt","-c","copy","footage.mp4"],check=True)
print("total",sum(d for _,d,_ in SHOTS))
