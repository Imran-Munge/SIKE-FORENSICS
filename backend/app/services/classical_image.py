import io
import numpy as np
from PIL import Image,ImageFilter

def dct_energy(raw):
    im=np.asarray(Image.open(io.BytesIO(raw)).convert("L"),dtype=np.float32)
    small=im[:min(256,im.shape[0]),:min(256,im.shape[1])]
    fft=np.fft.fft2(small); mag=np.abs(np.fft.fftshift(fft))
    h,w=mag.shape; cy,cx=h//2,w//2
    low=mag[max(0,cy-8):cy+8,max(0,cx-8):cx+8].mean()
    total=mag.mean() or 1.0
    return {"low_frequency_mean":float(low),"global_frequency_mean":float(total),"high_frequency_ratio":float(max(0,total-low)/total)}

def noise_residual(raw):
    im=Image.open(io.BytesIO(raw)).convert("L")
    blur=im.filter(ImageFilter.GaussianBlur(radius=1.2))
    a=np.asarray(im,dtype=np.float32); b=np.asarray(blur,dtype=np.float32); n=a-b
    return {"mean":float(n.mean()),"std":float(n.std()),"absolute_mean":float(np.abs(n).mean())}

def bit_plane_stats(raw):
    im=np.asarray(Image.open(io.BytesIO(raw)).convert("L"),dtype=np.uint8)
    return {"planes":{str(bit):float(((im>>bit)&1).mean()) for bit in range(8)}}

def copy_move_candidates(raw):
    im=np.asarray(Image.open(io.BytesIO(raw)).convert("L"),dtype=np.float32)
    h,w=im.shape
    if h<32 or w<32:return {"candidate_count":0,"note":"Image too small for coarse block comparison."}
    bh,bw=max(8,h//16),max(8,w//16); blocks=[]
    for y in range(0,h-bh+1,bh):
        for x in range(0,w-bw+1,bw):
            block=im[y:y+bh,x:x+bw]; blocks.append((float(block.mean()),float(block.std())))
    return {"candidate_count":0,"blocks_examined":len(blocks),"note":"Coarse statistical baseline; localization is not claimed."}
