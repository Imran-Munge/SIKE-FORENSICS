from .classical_image import dct_energy,noise_residual,bit_plane_stats,copy_move_candidates

def image_signal_bundle(raw):
    return {"dct":dct_energy(raw),"noise":noise_residual(raw),"bit_planes":bit_plane_stats(raw),"copy_move":copy_move_candidates(raw)}

def explain_signals(bundle):
    notes=[]
    noise=bundle.get("noise",{})
    if noise.get("absolute_mean",0)>8: notes.append("Elevated high-frequency residual; this is non-specific and may reflect texture or compression.")
    planes=bundle.get("bit_planes",{}).get("7")
    if planes is not None and (planes<0.01 or planes>0.99): notes.append("Extreme top-bit distribution; inspect the original image and encoding path.")
    if not notes: notes.append("No single classical signal is sufficient to establish manipulation.")
    return notes
