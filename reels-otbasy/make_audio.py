# Synthesizes the music bed and SFX (no external samples), writes audio/music_sfx.wav
import numpy as np, wave
SR=48000; DUR=39.0; N=int(SR*DUR); OFF=0.25
rng=np.random.default_rng(3)
t=np.arange(N)/SR
mus=np.zeros(N); sfx=np.zeros(N)
def hz(m): return 440*2**((m-69)/12)
def lp(x,a):  # one-pole lowpass, a in (0,1)
    y=np.empty_like(x); s=0.0
    for i in range(len(x)): s+=a*(x[i]-s); y[i]=s
    return y
# --- pad: D major progression, 8 bars of 4.875s
prog=[[50,57,62,66,69],[47,54,59,62,66],[43,50,55,59,62],[45,52,57,61,64]]*2
L=DUR/len(prog)
for k,ch in enumerate(prog):
    a=k*L; b=a+L
    env=np.clip((t-a+0.9)/1.8,0,1)*np.clip((b+0.9-t)/1.8,0,1); env=np.sin(env*np.pi/2)**2
    idx=env>0
    for m in ch:
        f=hz(m); tt=t[idx]
        v=sum(np.sin(2*np.pi*f*d*tt+ph) for d,ph in ((1,0),(1.003,1.3),(0.997,2.1)))/3
        v+=0.18*np.sin(2*np.pi*2*f*tt)
        mus[idx]+=v*env[idx]*0.07
mus*=0.6+0.4*np.sin(2*np.pi*0.11*t)**2
# --- soft piano arpeggio (80 bpm 8ths)
beat=60/80/2
def pluck(at,m,amp=.12,dec=1.6):
    f=hz(m); i0=int(at*SR); n=int(SR*2.5); n=min(n,N-i0)
    if n<=0: return
    tt=np.arange(n)/SR; e=np.exp(-tt*dec)*np.clip(tt/0.004,0,1)
    v=(np.sin(2*np.pi*f*tt)+.35*np.sin(2*np.pi*2*f*tt)*np.exp(-tt*3)+.12*np.sin(2*np.pi*3*f*tt)*np.exp(-tt*5))
    mus[i0:i0+n]+=v*e*amp
pat=[0,2,4,3,1,3,4,2]
for k,ch in enumerate(prog):
    up=[c+12 for c in ch]
    for j in range(int(L/beat)):
        at=k*L+j*beat
        if at>DUR-2.5: break
        pluck(at,up[pat[j%8]%len(up)],amp=.06 if j%2 else .085)
# sub swell under the CTA
mus=lp(mus,0.35)
fade=np.clip(t/1.0,0,1)*np.clip((DUR-t)/2.2,0,1); mus*=fade
# --- SFX
def add(at,v,g=1.0):
    i0=int(at*SR); n=min(len(v),N-i0)
    if i0<0 or n<=0: return
    sfx[i0:i0+n]+=v[:n]*g
def whoosh(dur=.55):
    n=int(SR*dur); x=rng.standard_normal(n); tt=np.arange(n)/n
    env=np.sin(np.pi*tt**0.7)**2
    a=0.02+0.25*np.sin(np.pi*tt)  # brighter in the middle
    y=np.empty(n); s=0.0
    for i in range(n): s+=a[i]*(x[i]-s); y[i]=s
    return y*env*0.9
def boom():
    n=int(SR*1.6); tt=np.arange(n)/SR
    f=55*np.exp(-tt*1.5)+38; ph=2*np.pi*np.cumsum(f)/SR
    v=np.sin(ph)*np.exp(-tt*2.6)*np.clip(tt/0.005,0,1)
    sh=sum(np.sin(2*np.pi*hz(m)*tt) for m in (81,86,90,93))/4*np.exp(-tt*1.8)*0.25*np.clip(tt/0.08,0,1)
    return v*0.9+sh
def thud():
    n=int(SR*.5); tt=np.arange(n)/SR
    return np.sin(2*np.pi*(70*np.exp(-tt*4)+45)*tt)*np.exp(-tt*9)*.8
def chime(m=88,dec=4):
    n=int(SR*1.2); tt=np.arange(n)/SR
    return (np.sin(2*np.pi*hz(m)*tt)+.4*np.sin(2*np.pi*hz(m+12)*tt)*np.exp(-tt*6))*np.exp(-tt*dec)*np.clip(tt/0.002,0,1)*.35
def tick(f=1500):
    n=int(SR*.06); tt=np.arange(n)/SR
    return np.sin(2*np.pi*f*tt)*np.exp(-tt*70)*.35
def popv():
    n=int(SR*.12); tt=np.arange(n)/SR
    return np.sin(2*np.pi*(500+700*tt/0.12)*tt)*np.exp(-tt*30)*.5
def shutter():
    n=int(SR*.25); x=rng.standard_normal(n); tt=np.arange(n)/SR
    e=np.exp(-tt*120)+np.exp(-np.clip(tt-0.09,0,None)*90)*(tt>0.09)*.8
    return lp(x,.5)*e*.8
for vt in (3.2,8.3,11.75,17.15,20.1,27.5,33.45):
    add(vt+OFF-0.3,whoosh(),.5)
add(1.25+OFF,boom(),.55); add(16.3+OFF,boom(),.6); add(35.85+OFF,boom(),.7)
add(7.62+OFF,thud(),.8)
for i in range(6): add(5.9+OFF+i*.12,tick(2200+rng.integers(-200,200)),.35)
for i in range(4): add(8.6+OFF+i*.53,chime(74+[0,4,7,12][i],5),.6)
add(20.85+OFF,thud(),.4); add(21.7+OFF,thud(),.4)
for i,s in enumerate((23.47,25.22,26.27)): add(s+OFF,chime(86+[0,4,7][i]),.8)
for s in (29.42,29.96,30.62): add(s+OFF,popv(),.6)
add(32.62+OFF,shutter(),1.0)
mix=mus+sfx
mix/=np.max(np.abs(mix))*1.12
st=np.stack([mix,mix],1)
w=wave.open('audio/music_sfx.wav','wb');w.setnchannels(2);w.setsampwidth(2);w.setframerate(SR)
w.writeframes((st*32767).astype('<i2').tobytes());w.close();print('ok')
