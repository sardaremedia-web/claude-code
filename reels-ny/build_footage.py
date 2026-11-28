# Punch-in edit of the source (constant crop per segment -> no zoom jitter), native 50 fps.
import subprocess,os
SEG=[(0,1.0,1.0),(1.0,6.27,1.0),(6.27,8.1,1.18),(8.1,11.3,1.0),(11.3,13.2,1.18),(13.2,16.4,1.0),(16.4,18.4,1.18),(18.4,21.36,1.0),(21.36,24.54,1.18),
     (24.54,27.65,1.0),(27.65,30.98,1.15),(30.98,35.8,1.0),(35.8,38.06,1.12),(38.06,44.08,1.0),(44.08,46.4,1.0),(46.4,48.78,1.12),(48.78,63.94,1.0),(63.94,66.0,1.0),(66.0,68.5,1.12)]
os.makedirs('shots',exist_ok=True);lst=[]
for i,(a,b,z) in enumerate(SEG):
    d=b-a;n=round(d*50)
    W=int(round(1080*z/2)*2);H=int(round(1920*z/2)*2);x=(W-1080)//2;y=int((H-1920)*0.38)
    vf=f"fps=50,scale={W}:{H}:flags=lanczos,crop=1080:1920:{x}:{y},setsar=1,eq=contrast=1.06:saturation=1.1,colorbalance=rh=0.03:bh=-0.02"
    out=f"shots/{i:02d}.mp4"
    subprocess.run(["ffmpeg","-v","error","-y","-ss",f"{a:.3f}","-t",f"{d+0.1:.3f}","-i","src/src.mov","-an","-vf",vf,"-frames:v",str(n),"-c:v","libx264","-preset","medium","-crf","15","-pix_fmt","yuv420p","-r","50",out],check=True)
    lst.append(f"file '{os.path.abspath(out)}'")
open('shots/list.txt','w').write("\n".join(lst))
subprocess.run(["ffmpeg","-v","error","-y","-f","concat","-safe","0","-i","shots/list.txt","-c","copy","footage.mp4"],check=True)
