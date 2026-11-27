# Synthesizes the music bed and SFX (no external samples), writes audio/music_sfx.wav
import numpy as np, wave
def W(x): return x
SR=48000; DUR=47.6; N=int(SR*DUR); OFF=0.0
rng=np.random.default_rng(3)
t=np.arange(N)/SR
mus=np.zeros(N); sfx=np.zeros(N)
def hz(m): return 440*2**((m-69)/12)
def lp(x,a):  # one-pole lowpass, a in (0,1)
    y=np.empty_like(x); s=0.0
    for i in range(len(x)): s+=a*(x[i]-s); y[i]=s
    return y
# --- pad: D major progression, 8 bars of 4.875s
prog=[[48,55,60,64,67],[45,52,57,60,64],[41,48,53,57,60],[43,50,55,59,62]]*3
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
beat=60/96/2
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
for vt in (3.45,9.75,14.85,17.45,21.6,28.75,33.6,40.9):
    add(vt-0.25,whoosh(),.5)
add(0.55,boom(),.5); add(31.6,boom(),.75); add(44.05,boom(),.7)
for s in (4.0,5.25,6.75,22.3,24.5,26.0,33.9,36.1,38.3): add(s,chime(86,5),.6)
for i in range(8): add(10.9+i*.09,popv(),.25)
add(19.7,thud(),.5)
mix=mus+sfx
mix/=np.max(np.abs(mix))*1.12
st=np.stack([mix,mix],1)
w=wave.open('audio/music_sfx.wav','wb');w.setnchannels(2);w.setsampwidth(2);w.setframerate(SR)
w.writeframes((st*32767).astype('<i2').tobytes());w.close();print('ok')
