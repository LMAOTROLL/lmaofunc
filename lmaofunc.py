import vapoursynth as vs
import muvsfunc as muvf
import fvsfunc as fvf
core = vs.core

def antialiasing(clip: vs.VideoNode, aath: int = 48) -> vs.VideoNode:
    """
    clip: Clip to be AntiAliased
    aath: the strength of anti-aliasing
    """
    ox = clip.width
    oy = clip.height
    dx = clip.width * 2
    dy = clip.height * 2

    a = clip
    reize = core.resize.Lanczos(clip, dx, dy, filter_param_a=4)
    turnL = muvf.TurnLeft(resize)
    aaL = core.sangnom.SangNom(turnL, aa=aath)
    turnR = muvf.TurnRight(aaL)
    aaR = core.sangnom.SangNom(turnR, aa=aath)
    resizeOut = core.resize.Lanczos(clip, ox, oy)
    edge = core.std.Sobel(clip)
    return core.std.MaskedMerge(a, resizeOut, edge)

def eedi3_rpow2(clip: vs.VideoNode, rfactor: int = 2, width = None, height = None, correct_shift: bool = True, kernel: str = "spline36", **eedi3_params) -> vs.VideoNode:
    funcName = "eedi3_rpow2"
    """
    eedi3_rpow2 is for enlarging images by power of 2

    Args:
        rfactor(int): Image enlargement factor.
            Must be a power of 2 in the range [2 to 1024].
        correct_shift (bool): If False, the shift is not corrected.
            The correction is accomplished by using the subpixel
            cropping capability of fmtc's resizers.
        width (int): If correcting the image center shift by using the
            "correct_shift" parameter, width/height allow you to set a
            new output resolution
        kernel (string): Sets the resizer used for correcting the image
            center shift that eedi3_rpow2 introduces. This can be any of
            fmtc kernels, such as "cubic", "spline36", etc.
            spline36 is the default one.
        eedi3_args(mixed): For helo with eedi3 args
            refert to eedi3 documentation.
    """

    if width is None:
        width = clip.width * rfactor
    if height is None:
        height = clip.height * rfactor
    hshift = 0.0
    vshift = -0.5
    eedi_args = dict(dh=True, alpha=alpha, beta=beta, gamma=gamma, vcheck=3, nrad=nrad, mdis=mdis, opt=0)
    chroma_args = dict(kernel=kernel, sy=-0.5, planes=[2, 3, 3])

    tmp = 1
    times = 0
    while tmp < rfactor:
        tmp *= 2
        times += 1

    if rfactor < 2 or rfactor > 1024:
        raise ValueError(f"{funcName}: rfactor must be between 2 and 1024")

    if tmp != rfactor:
        raise ValueError(f"{funcName}: rfactor must be a power of 2")

    if hasattr(core, 'eedi3m') is not True:
        raise RuntimeError(f"{funcName}: eedi3m plugin is required")

    if correct_shift or clip.format.subsampling_h:
        if hasattr(core, 'fmtc') is not True:
            raise RuntimeError(f"{funcName}: fmtconv plugin is required")

    last = clip
    for i in range(times):
        field = 1 if i == 0 else 0
        last = core.eedi3m.EEDI3(last, field=field, **eedi_args)
        last = core.std.Transpose(last)
        if last.format.subsampling_w:
            field = 1
            hshift = (hshift * 2) - 0.5
        else:
            hshift = -0.5
        last = core.eedi3m.EEDI3(last, field=field, **eedi_args)
        last = core.std.Transpose(last)

    if clip.format.subsampling_h:
        last = core.fmtc.resample(last, w=last.width, h=last.height, **chroma_args)

    if correct_shift:
        last = core.fmtc.resample(last, w=width, h=height, kernel=kernel, sx=hshift, sy=vshift)

    if last.format.id != clip.format.id:
        last = core.fmtc.bitdepth(last, csp=clip.format.id)

    return last

def source(clip: vs.VideoNode, lsmas: bool = True, depth: int = 16) -> vs.VideoNode:
    """
    clip: clip
    lsmas: force files to be imported with L-SMASH
    depth: Dither video
    Useless function
    """

    clip = fvf.Depth(clip, depth)

    if lsmas:
        return core.lsmas.LWLibavSource(clip)

    if clip.endswith('.d2v'):
        return core.d2v.Source(clip)

    if file.endswith('.m2ts'):
        return core.lsmas.LWLibavSource(clip)
    else:
        return core.ffms2.Source(clip)

def MergeLuma(clip1: vs.VideoNode, clip2: vs.VideoNode) -> vs.VideoNode:
    Y1, U1, V1 = split(clip1)
    Y2, U2, V2 = split(clip2)
    return core.std.ShufflePlanes(clips=[Y2, U1, V1], planes=[0, 0, 0], colorfamily=vs.YUV)

def AssumeFPS(clip: vs.VideoNode, preset: str = "ntsc_film"):
    funcName = "AssumeFPS"
    if preset == "ntsc_film":
        video = core.std.AssumeFPS(clip, fpsnum=24000, fpsden=1001)
    elif preset == "ntsc_video":
        video = core.std.AssumeFPS(clip, fpsnum=30000, fpsden=1001)
    elif preset == "ntsc_double":
        video = core.std.AssumeFPS(clip, fpsnum=60000, fpsden=1001)
    elif preset == "ntsc_quad":
        video = core.std.AssumeFPS(clip, fpsnum=120000, fpsden=1001)
    elif preset == "ntsc_round_film":
        video = core.std.AssumeFPS(clip, fpsnum=2997, fpsden=125)
    elif preset == "ntsc_round_video":
        video = core.std.AssumeFPS(clip, fpsnum=2997, fpsden=100)
    elif preset == "ntsc_round_double":
        video = core.std.AssumeFPS(clip, fpsnum=2997, fpsden=50)
    elif preset == "ntsc_round_quad":
        video = core.std.AssumeFPS(clip, fpsnum=2997, fpsden=25)
    elif preset == "film":
        video = core.std.AssumeFPS(clip, fpsnum=24, fpsden=1)
    elif preset == "pal_film":
        video = core.std.AssumeFPS(clip, fpsnum=25, fpsden=1)
    elif preset == "pal_video":
        video = core.std.AssumeFPS(clip, fpsnum=25, fpsden=1)
    elif preset == "pal_double":
        video = core.std.AssumeFPS(clip, fpsnum=50, fpsden=1)
    elif preset == "pal_quad":
        video = core.std.AssumeFPS(clip, fpsnum=100, fpsden=1)
    else:
        raise ValueError(f"{funcName}: unknown preset")

    return video

def JesusAA(clip: vs.VideoNode) -> vs.VideoNode:
    aa = eedi3_rpow2(clip, rfactor = 4, kernel="bilinear")
    resize = fvf.Debilinear(clip, clip.width, clip.height)
    return MergeLuma(aa, resize)

def ediaa(clip: vs.VideoNode) -> vs.VideoNode:
    aa = core.eedi2.EEDI2(clip, field=1)
    aa = muvf.TurnRight(aa)
    aa = core.eedi2.EEDI2(clip, field=1)
    aa = muvf.TurnLeft(aa)
    return core.resize.Spline36(aa, aa.width, aa.height, src_left=-0.5, src_top=-0.5)

