from typing import List, Dict, Any, Optional
import math

def _safe_int(v):
    try:
        return int(v) if v is not None else 0
    except Exception:
        return 0

def pick_video_audio_urls(formats: List[Dict[str, Any]]) -> Dict[str, Optional[Dict[str, Any]]]:
    """
    Given a list of format dicts (each dict like your examples), return a mapping:
    {
      "video_high": {...}, "video_med": {...}, "video_low": {...},
      "audio_high": {...}, "audio_med": {...}, "audio_low": {...}
    }
    Each value is the selected format dict (or None).
    """
    if not formats:
        return {k: None for k in (
            "video_high","video_med","video_low",
            "audio_high","audio_med","audio_low"
        )}

    # Separate video and audio entries
    video_formats = []
    audio_formats = []

    for f in formats:
        f_copy = dict(f)  # avoid mutating original
        # normalize numeric fields
        f_copy["_height"] = _safe_int(f.get("height"))
        f_copy["_width"] = _safe_int(f.get("width"))
        f_copy["_bitrate"] = _safe_int(f.get("bitrate"))
        # Determine type: prefer explicit 'type' then check ext/formatId/is_audio
        ftype = (f.get("type") or "").lower()
        if ftype == "video":
            video_formats.append(f_copy)
        elif ftype == "audio":
            audio_formats.append(f_copy)
        else:
            # fallback heuristics: some entries are video+audio (like mp4 itag 18)
            # treat entries with height>0 as video, with width/height==0 and bitrate>0 as audio
            if f_copy["_height"] > 0:
                video_formats.append(f_copy)
            elif f_copy.get("is_audio") or (f_copy["_height"] == 0 and f_copy["_bitrate"] > 0 and f.get("mimeType","").startswith("audio")):
                audio_formats.append(f_copy)
            else:
                # if unknown, try to classify by extension: webm/mp4 usually video, opus/mp3/ogg usually audio
                ext = (f.get("ext") or "").lower()
                if ext in ("mp4","webm","mkv","flv","mov"):
                    video_formats.append(f_copy)
                elif ext in ("mp3","aac","opus","m4a","wav","ogg"):
                    audio_formats.append(f_copy)
                else:
                    # if still ambiguous, put into video if it has height, else audio if no height
                    if f_copy["_height"] > 0:
                        video_formats.append(f_copy)
                    else:
                        audio_formats.append(f_copy)

    # Sort video by height then bitrate (descending)
    video_formats.sort(key=lambda x: (x["_height"], x["_bitrate"]), reverse=True)
    # Sort audio by bitrate (descending)
    audio_formats.sort(key=lambda x: x["_bitrate"], reverse=True)

    def pick_three(sorted_list):
        """Return high, med, low from a descending-sorted list."""
        if not sorted_list:
            return (None, None, None)
        n = len(sorted_list)
        high = sorted_list[0]
        low = sorted_list[-1]
        if n == 1:
            med = None
        elif n == 2:
            med = sorted_list[1]  # treat second as med
        else:
            # pick middle element as med
            med = sorted_list[n//2]
        return (high, med, low)

    v_high, v_med, v_low = pick_three(video_formats)
    a_high, a_med, a_low = pick_three(audio_formats)

    result = {
        "video_high": v_high,
        "video_med": v_med,
        "video_low": v_low,
        "audio_high": a_high,
        "audio_med": a_med,
        "audio_low": a_low,
    }

    # For convenience, also add direct URL strings (or None)
    for k, val in list(result.items()):
        result[k + "_url"] = None if val is None else val.get("url")

    return result

# -------------------------
# Example usage:
if __name__ == "__main__":
    # imagine `formats` is the list you pasted (truncated here for brevity)
    formats = [
        {
            "formatId": 18,
            "label": "mp4 (360p)",
            "type": "video",
            "ext": "mp4",
            "quality": "mp4 (360p)",
            "width": 560,
            "height": 360,
            "url": "https://redirector.googlevideo.com/videoplayback?expire=1757984114&ei=EmHIaO7pNunbzPsPsoS0wAo&ip=178.133.164.253&id=o-AF_yKqtMLMS5E_Tj8fkPP-z4-wZXt33KwmVN8BE1bdYq&itag=18&source=youtube&requiressl=yes&xpc=EgVo2aDSNQ%3D%3D&met=1757962514%2C&mh=2x&mm=31%2C29&mn=sn-jvhnu5g03g-3c2z%2Csn-3c27sn7s&ms=au%2Crdu&mv=m&mvi=2&pl=25&rms=au%2Cau&initcwndbps=1003750&bui=AY1jyLMe1R1SuudHkqP4kjbn_st4I2JdAUoj4Io1dJDFfA2iV1WNJ-CaCR3VEYQtxrXYc2XBikqkwPgO&spc=l3OVKTB4lM7NyX7wNagLLW5x4pVrRny05V4qDcr9_TnIY0YWSlx2SnO_o39IBB525KRQUmedmgqZuuU1VrpzT_QPqGI&vprv=1&svpuc=1&mime=video%2Fmp4&ns=UcDqVX3IB6p2T9jR6D2AlD8Q&rqh=1&gir=yes&clen=14519650&ratebypass=yes&dur=204.614&lmt=1751195249647658&mt=1757961965&fvip=17&fexp=51331020%2C51552689%2C51565115%2C51565681%2C51580968&c=MWEB&sefc=1&txp=4538534&n=WeIDrZQYariXhg&sparams=expire%2Cei%2Cip%2Cid%2Citag%2Csource%2Crequiressl%2Cxpc%2Cbui%2Cspc%2Cvprv%2Csvpuc%2Cmime%2Cns%2Crqh%2Cgir%2Cclen%2Cratebypass%2Cdur%2Clmt&sig=AJfQdSswRQIhAM_c1GctcFhkzDS8K4WndFkrKboxnPvzZXleMESWOetIAiABNv7zl4xk--Q4SngMU4Y-H6jOXGWfqZ5vToNJBcsQHw%3D%3D&lsparams=met%2Cmh%2Cmm%2Cmn%2Cms%2Cmv%2Cmvi%2Cpl%2Crms%2Cinitcwndbps&lsig=APaTxxMwRQIhAN_GFt_7z03gfGcAJBeS0bgNht0gJMgbVD-_HEqGTwJzAiAaejtsmje9hVgTvcVUulsdggjw1WINJMvAujX854q04Q%3D%3D&pot=MnbXEQJFVEJcmNcv1FMM-aa1Z3ZjSiI2JX90LxmWfbUbvnK1t2dfnH0lzSA5Z2O1_CW2otEmJCcB-iYx_xwvuxnfZVXV3vX4HUpqgLfZ1G3U8rA8i1cl7w5QNDZtoSHb6MX5Fn66sa9iFni1KIe8x-Uf2kYM6mDM",
            "bitrate": 567892,
            "fps": 24,
            "audioQuality": "AUDIO_QUALITY_LOW",
            "audioSampleRate": "44100",
            "mimeType": "video/mp4; codecs=\"avc1.42001E, mp4a.40.2\"",
            "duration": 3,
            "is_audio": True,
            "extension": "mp4"
        },
        {
            "formatId": 313,
            "label": "webm (2160p)",
            "type": "video",
            "ext": "webm",
            "quality": "webm (2160p)",
            "width": 3358,
            "height": 2160,
            "url": "https://redirector.googlevideo.com/videoplayback?expire=1757984114&ei=EmHIaO7pNunbzPsPsoS0wAo&ip=178.133.164.253&id=o-AF_yKqtMLMS5E_Tj8fkPP-z4-wZXt33KwmVN8BE1bdYq&itag=313&aitags=133%2C134%2C135%2C136%2C137%2C160%2C242%2C243%2C244%2C247%2C248%2C271%2C278%2C313%2C394%2C395%2C396%2C397%2C398%2C399%2C400%2C401%2C598&source=youtube&requiressl=yes&xpc=EgVo2aDSNQ%3D%3D&met=1757962514%2C&mh=2x&mm=31%2C29&mn=sn-jvhnu5g03g-3c2z%2Csn-3c27sn7s&ms=au%2Crdu&mv=m&mvi=2&pl=25&rms=au%2Cau&initcwndbps=1003750&bui=AY1jyLPrRKSPs7w-py3YPFI6ZzzxRXkHh2vTttiFankTq28oke3V23LeYvK5csurVaQP7zDbR1FqdafE&spc=l3OVKTB7lM7NyX7wNagLLW5x4pVqRny05V4qDcr9_TnIY0YWSlx2SnO_o39IBB5G4b5dKGmFDtiuvkLrVIJ37_WT&vprv=1&svpuc=1&mime=video%2Fwebm&ns=EZOay5mK4ezir93Hthf78IEQ&rqh=1&gir=yes&clen=264777042&dur=204.541&lmt=1751197658376544&mt=1757961965&fvip=17&keepalive=yes&fexp=51331020%2C51552689%2C51565115%2C51565681%2C51580968&c=MWEB&sefc=1&txp=4532534&n=NV0OZWVsA3iW7w&sparams=expire%2Cei%2Cip%2Cid%2Caitags%2Csource%2Crequiressl%2Cxpc%2Cbui%2Cspc%2Cvprv%2Csvpuc%2Cmime%2Cns%2Crqh%2Cgir%2Cclen%2Cdur%2Clmt&sig=AJfQdSswRAIgPbGZNonJvbuCfKRytkvG_EdLs7rcQtIGDIm-YkT8TaYCIDDvlM_FLS6gDFAKJ2Hj9PN6Wsmdj-P6zec3vZ2W9fv6&lsparams=met%2Cmh%2Cmm%2Cmn%2Cms%2Cmv%2Cmvi%2Cpl%2Crms%2Cinitcwndbps&lsig=APaTxxMwRQIhAN_GFt_7z03gfGcAJBeS0bgNht0gJMgbVD-_HEqGTwJzAiAaejtsmje9hVgTvcVUulsdggjw1WINJMvAujX854q04Q%3D%3D&pot=MnbXEQJFVEJcmNcv1FMM-aa1Z3ZjSiI2JX90LxmWfbUbvnK1t2dfnH0lzSA5Z2O1_CW2otEmJCcB-iYx_xwvuxnfZVXV3vX4HUpqgLfZ1G3U8rA8i1cl7w5QNDZtoSHb6MX5Fn66sa9iFni1KIe8x-Uf2kYM6mDM",
            "bitrate": 15745798,
            "fps": 24,
            "audioQuality": None,
            "audioSampleRate": None,
            "mimeType": "video/webm; codecs=\"vp9\"",
            "duration": 3,
            "extension": "webm"
        },
        {
            "formatId": 401,
            "label": "mp4 (2160p)",
            "type": "video",
            "ext": "mp4",
            "quality": "mp4 (2160p)",
            "width": 3358,
            "height": 2160,
            "url": "https://redirector.googlevideo.com/videoplayback?expire=1757984114&ei=EmHIaO7pNunbzPsPsoS0wAo&ip=178.133.164.253&id=o-AF_yKqtMLMS5E_Tj8fkPP-z4-wZXt33KwmVN8BE1bdYq&itag=401&aitags=133%2C134%2C135%2C136%2C137%2C160%2C242%2C243%2C244%2C247%2C248%2C271%2C278%2C313%2C394%2C395%2C396%2C397%2C398%2C399%2C400%2C401%2C598&source=youtube&requiressl=yes&xpc=EgVo2aDSNQ%3D%3D&met=1757962514%2C&mh=2x&mm=31%2C29&mn=sn-jvhnu5g03g-3c2z%2Csn-3c27sn7s&ms=au%2Crdu&mv=m&mvi=2&pl=25&rms=au%2Cau&initcwndbps=1003750&bui=AY1jyLPrRKSPs7w-py3YPFI6ZzzxRXkHh2vTttiFankTq28oke3V23LeYvK5csurVaQP7zDbR1FqdafE&spc=l3OVKTB7lM7NyX7wNagLLW5x4pVqRny05V4qDcr9_TnIY0YWSlx2SnO_o39IBB5G4b5dKGmFDtiuvkLrVIJ37_WT&vprv=1&svpuc=1&mime=video%2Fmp4&ns=EZOay5mK4ezir93Hthf78IEQ&rqh=1&gir=yes&clen=153543981&dur=204.541&lmt=1751195478741237&mt=1757961965&fvip=17&keepalive=yes&fexp=51331020%2C51552689%2C51565115%2C51565681%2C51580968&c=MWEB&sefc=1&txp=4532534&n=NV0OZWVsA3iW7w&sparams=expire%2Cei%2Cip%2Cid%2Caitags%2Csource%2Crequiressl%2Cxpc%2Cbui%2Cspc%2Cvprv%2Csvpuc%2Cmime%2Cns%2Crqh%2Cgir%2Cclen%2Cdur%2Clmt&sig=AJfQdSswRgIhAKHTMI2bH7Zxrof0TCmrmqps8tsJQeJWquu7iSY5fJF2AiEArVEXxGEfE4qWOPSnLj7QQESlSA9lSVtRpgzVc61p51A%3D&lsparams=met%2Cmh%2Cmm%2Cmn%2Cms%2Cmv%2Cmvi%2Cpl%2Crms%2Cinitcwndbps&lsig=APaTxxMwRQIhAN_GFt_7z03gfGcAJBeS0bgNht0gJMgbVD-_HEqGTwJzAiAaejtsmje9hVgTvcVUulsdggjw1WINJMvAujX854q04Q%3D%3D&pot=MnbXEQJFVEJcmNcv1FMM-aa1Z3ZjSiI2JX90LxmWfbUbvnK1t2dfnH0lzSA5Z2O1_CW2otEmJCcB-iYx_xwvuxnfZVXV3vX4HUpqgLfZ1G3U8rA8i1cl7w5QNDZtoSHb6MX5Fn66sa9iFni1KIe8x-Uf2kYM6mDM",
            "bitrate": 12107204,
            "fps": 24,
            "audioQuality": None,
            "audioSampleRate": None,
            "mimeType": "video/mp4; codecs=\"av01.0.12M.08\"",
            "duration": 3,
            "extension": "mp4"
        },
        {
            "formatId": 271,
            "label": "webm (1440p)",
            "type": "video",
            "ext": "webm",
            "quality": "webm (1440p)",
            "width": 2240,
            "height": 1440,
            "url": "https://redirector.googlevideo.com/videoplayback?expire=1757984114&ei=EmHIaO7pNunbzPsPsoS0wAo&ip=178.133.164.253&id=o-AF_yKqtMLMS5E_Tj8fkPP-z4-wZXt33KwmVN8BE1bdYq&itag=271&aitags=133%2C134%2C135%2C136%2C137%2C160%2C242%2C243%2C244%2C247%2C248%2C271%2C278%2C313%2C394%2C395%2C396%2C397%2C398%2C399%2C400%2C401%2C598&source=youtube&requiressl=yes&xpc=EgVo2aDSNQ%3D%3D&met=1757962514%2C&mh=2x&mm=31%2C29&mn=sn-jvhnu5g03g-3c2z%2Csn-3c27sn7s&ms=au%2Crdu&mv=m&mvi=2&pl=25&rms=au%2Cau&initcwndbps=1003750&bui=AY1jyLPrRKSPs7w-py3YPFI6ZzzxRXkHh2vTttiFankTq28oke3V23LeYvK5csurVaQP7zDbR1FqdafE&spc=l3OVKTB7lM7NyX7wNagLLW5x4pVqRny05V4qDcr9_TnIY0YWSlx2SnO_o39IBB5G4b5dKGmFDtiuvkLrVIJ37_WT&vprv=1&svpuc=1&mime=video%2Fwebm&ns=EZOay5mK4ezir93Hthf78IEQ&rqh=1&gir=yes&clen=104449764&dur=204.541&lmt=1751195479127859&mt=1757961965&fvip=17&keepalive=yes&fexp=51331020%2C51552689%2C51565115%2C51565681%2C51580968&c=MWEB&sefc=1&txp=4532534&n=NV0OZWVsA3iW7w&sparams=expire%2Cei%2Cip%2Cid%2Caitags%2Csource%2Crequiressl%2Cxpc%2Cbui%2Cspc%2Cvprv%2Csvpuc%2Cmime%2Cns%2Crqh%2Cgir%2Cclen%2Cdur%2Clmt&sig=AJfQdSswRQIhAJKST_JOJZa_UYVJU2Te-zpBaeahBOhPNKK_n7XILZChAiBaw1RqhXlnpb-o5FDmtj2ynV_Y_ApFeTjA4HE-Y4GMgg%3D%3D&lsparams=met%2Cmh%2Cmm%2Cmn%2Cms%2Cmv%2Cmvi%2Cpl%2Crms%2Cinitcwndbps&lsig=APaTxxMwRQIhAN_GFt_7z03gfGcAJBeS0bgNht0gJMgbVD-_HEqGTwJzAiAaejtsmje9hVgTvcVUulsdggjw1WINJMvAujX854q04Q%3D%3D&pot=MnbXEQJFVEJcmNcv1FMM-aa1Z3ZjSiI2JX90LxmWfbUbvnK1t2dfnH0lzSA5Z2O1_CW2otEmJCcB-iYx_xwvuxnfZVXV3vX4HUpqgLfZ1G3U8rA8i1cl7w5QNDZtoSHb6MX5Fn66sa9iFni1KIe8x-Uf2kYM6mDM",
            "bitrate": 7907195,
            "fps": 24,
            "audioQuality": None,
            "audioSampleRate": None,
            "mimeType": "video/webm; codecs=\"vp9\"",
            "duration": 3,
            "extension": "webm"
        },
        {
            "formatId": 400,
            "label": "mp4 (1440p)",
            "type": "video",
            "ext": "mp4",
            "quality": "mp4 (1440p)",
            "width": 2240,
            "height": 1440,
            "url": "https://redirector.googlevideo.com/videoplayback?expire=1757984114&ei=EmHIaO7pNunbzPsPsoS0wAo&ip=178.133.164.253&id=o-AF_yKqtMLMS5E_Tj8fkPP-z4-wZXt33KwmVN8BE1bdYq&itag=400&aitags=133%2C134%2C135%2C136%2C137%2C160%2C242%2C243%2C244%2C247%2C248%2C271%2C278%2C313%2C394%2C395%2C396%2C397%2C398%2C399%2C400%2C401%2C598&source=youtube&requiressl=yes&xpc=EgVo2aDSNQ%3D%3D&met=1757962514%2C&mh=2x&mm=31%2C29&mn=sn-jvhnu5g03g-3c2z%2Csn-3c27sn7s&ms=au%2Crdu&mv=m&mvi=2&pl=25&rms=au%2Cau&initcwndbps=1003750&bui=AY1jyLPrRKSPs7w-py3YPFI6ZzzxRXkHh2vTttiFankTq28oke3V23LeYvK5csurVaQP7zDbR1FqdafE&spc=l3OVKTB7lM7NyX7wNagLLW5x4pVqRny05V4qDcr9_TnIY0YWSlx2SnO_o39IBB5G4b5dKGmFDtiuvkLrVIJ37_WT&vprv=1&svpuc=1&mime=video%2Fmp4&ns=EZOay5mK4ezir93Hthf78IEQ&rqh=1&gir=yes&clen=83436363&dur=204.541&lmt=1751194882841712&mt=1757961965&fvip=17&keepalive=yes&fexp=51331020%2C51552689%2C51565115%2C51565681%2C51580968&c=MWEB&sefc=1&txp=4532534&n=NV0OZWVsA3iW7w&sparams=expire%2Cei%2Cip%2Cid%2Caitags%2Csource%2Crequiressl%2Cxpc%2Cbui%2Cspc%2Cvprv%2Csvpuc%2Cmime%2Cns%2Crqh%2Cgir%2Cclen%2Cdur%2Clmt&sig=AJfQdSswRQIgIBjwUY8iwNu3V9Lh7yCyBTC-JxxQA7AKvDfyYC7SDGsCIQCe4FtBPUnPvuOL62EX2jlJ2FwbWC8wYUyPcOuOdZnRFA%3D%3D&lsparams=met%2Cmh%2Cmm%2Cmn%2Cms%2Cmv%2Cmvi%2Cpl%2Crms%2Cinitcwndbps&lsig=APaTxxMwRQIhAN_GFt_7z03gfGcAJBeS0bgNht0gJMgbVD-_HEqGTwJzAiAaejtsmje9hVgTvcVUulsdggjw1WINJMvAujX854q04Q%3D%3D&pot=MnbXEQJFVEJcmNcv1FMM-aa1Z3ZjSiI2JX90LxmWfbUbvnK1t2dfnH0lzSA5Z2O1_CW2otEmJCcB-iYx_xwvuxnfZVXV3vX4HUpqgLfZ1G3U8rA8i1cl7w5QNDZtoSHb6MX5Fn66sa9iFni1KIe8x-Uf2kYM6mDM",
            "bitrate": 6312271,
            "fps": 24,
            "audioQuality": None,
            "audioSampleRate": None,
            "mimeType": "video/mp4; codecs=\"av01.0.12M.08\"",
            "duration": 3,
            "extension": "mp4"
        },
        {
            "formatId": 137,
            "label": "mp4 (1080p)",
            "type": "video",
            "ext": "mp4",
            "quality": "mp4 (1080p)",
            "width": 1680,
            "height": 1080,
            "url": "https://redirector.googlevideo.com/videoplayback?expire=1757984114&ei=EmHIaO7pNunbzPsPsoS0wAo&ip=178.133.164.253&id=o-AF_yKqtMLMS5E_Tj8fkPP-z4-wZXt33KwmVN8BE1bdYq&itag=137&aitags=133%2C134%2C135%2C136%2C137%2C160%2C242%2C243%2C244%2C247%2C248%2C271%2C278%2C313%2C394%2C395%2C396%2C397%2C398%2C399%2C400%2C401%2C598&source=youtube&requiressl=yes&xpc=EgVo2aDSNQ%3D%3D&met=1757962514%2C&mh=2x&mm=31%2C29&mn=sn-jvhnu5g03g-3c2z%2Csn-3c27sn7s&ms=au%2Crdu&mv=m&mvi=2&pl=25&rms=au%2Cau&initcwndbps=1003750&bui=AY1jyLPrRKSPs7w-py3YPFI6ZzzxRXkHh2vTttiFankTq28oke3V23LeYvK5csurVaQP7zDbR1FqdafE&spc=l3OVKTB7lM7NyX7wNagLLW5x4pVqRny05V4qDcr9_TnIY0YWSlx2SnO_o39IBB5G4b5dKGmFDtiuvkLrVIJ37_WT&vprv=1&svpuc=1&mime=video%2Fmp4&ns=EZOay5mK4ezir93Hthf78IEQ&rqh=1&gir=yes&clen=50974907&dur=204.541&lmt=1751194808761137&mt=1757961965&fvip=17&keepalive=yes&fexp=51331020%2C51552689%2C51565115%2C51565681%2C51580968&c=MWEB&sefc=1&txp=4532534&n=NV0OZWVsA3iW7w&sparams=expire%2Cei%2Cip%2Cid%2Caitags%2Csource%2Crequiressl%2Cxpc%2Cbui%2Cspc%2Cvprv%2Csvpuc%2Cmime%2Cns%2Crqh%2Cgir%2Cclen%2Cdur%2Clmt&sig=AJfQdSswRQIgOstw20gommHAYa2KWH33c29HgiqOIQ9dNa3VOT119koCIQCpq5U_jzZUGRVQv9vXrWiHImI58YAQfeoBCQAFXIxYag%3D%3D&lsparams=met%2Cmh%2Cmm%2Cmn%2Cms%2Cmv%2Cmvi%2Cpl%2Crms%2Cinitcwndbps&lsig=APaTxxMwRQIhAN_GFt_7z03gfGcAJBeS0bgNht0gJMgbVD-_HEqGTwJzAiAaejtsmje9hVgTvcVUulsdggjw1WINJMvAujX854q04Q%3D%3D&pot=MnbXEQJFVEJcmNcv1FMM-aa1Z3ZjSiI2JX90LxmWfbUbvnK1t2dfnH0lzSA5Z2O1_CW2otEmJCcB-iYx_xwvuxnfZVXV3vX4HUpqgLfZ1G3U8rA8i1cl7w5QNDZtoSHb6MX5Fn66sa9iFni1KIe8x-Uf2kYM6mDM",
            "bitrate": 3791913,
            "fps": 24,
            "audioQuality": None,
            "audioSampleRate": None,
            "mimeType": "video/mp4; codecs=\"avc1.640028\"",
            "duration": 3,
            "extension": "mp4"
        },
        {
            "formatId": 248,
            "label": "webm (1080p)",
            "type": "video",
            "ext": "webm",
            "quality": "webm (1080p)",
            "width": 1680,
            "height": 1080,
            "url": "https://redirector.googlevideo.com/videoplayback?expire=1757984114&ei=EmHIaO7pNunbzPsPsoS0wAo&ip=178.133.164.253&id=o-AF_yKqtMLMS5E_Tj8fkPP-z4-wZXt33KwmVN8BE1bdYq&itag=248&aitags=133%2C134%2C135%2C136%2C137%2C160%2C242%2C243%2C244%2C247%2C248%2C271%2C278%2C313%2C394%2C395%2C396%2C397%2C398%2C399%2C400%2C401%2C598&source=youtube&requiressl=yes&xpc=EgVo2aDSNQ%3D%3D&met=1757962514%2C&mh=2x&mm=31%2C29&mn=sn-jvhnu5g03g-3c2z%2Csn-3c27sn7s&ms=au%2Crdu&mv=m&mvi=2&pl=25&rms=au%2Cau&initcwndbps=1003750&bui=AY1jyLPrRKSPs7w-py3YPFI6ZzzxRXkHh2vTttiFankTq28oke3V23LeYvK5csurVaQP7zDbR1FqdafE&spc=l3OVKTB7lM7NyX7wNagLLW5x4pVqRny05V4qDcr9_TnIY0YWSlx2SnO_o39IBB5G4b5dKGmFDtiuvkLrVIJ37_WT&vprv=1&svpuc=1&mime=video%2Fwebm&ns=EZOay5mK4ezir93Hthf78IEQ&rqh=1&gir=yes&clen=36761034&dur=204.541&lmt=1751196808290090&mt=1757961965&fvip=17&keepalive=yes&fexp=51331020%2C51552689%2C51565115%2C51565681%2C51580968&c=MWEB&sefc=1&txp=4537534&n=NV0OZWVsA3iW7w&sparams=expire%2Cei%2Cip%2Cid%2Caitags%2Csource%2Crequiressl%2Cxpc%2Cbui%2Cspc%2Cvprv%2Csvpuc%2Cmime%2Cns%2Crqh%2Cgir%2Cclen%2Cdur%2Clmt&sig=AJfQdSswRQIgV_W3nGbskr5r0QoC7gnNDWaqw2njpfRkD-zlUwGQwIECIQC80xfKvHRVGMuPp59lThmpYGhPAKWJWD9to5TdKeqZJw%3D%3D&lsparams=met%2Cmh%2Cmm%2Cmn%2Cms%2Cmv%2Cmvi%2Cpl%2Crms%2Cinitcwndbps&lsig=APaTxxMwRQIhAN_GFt_7z03gfGcAJBeS0bgNht0gJMgbVD-_HEqGTwJzAiAaejtsmje9hVgTvcVUulsdggjw1WINJMvAujX854q04Q%3D%3D&pot=MnbXEQJFVEJcmNcv1FMM-aa1Z3ZjSiI2JX90LxmWfbUbvnK1t2dfnH0lzSA5Z2O1_CW2otEmJCcB-iYx_xwvuxnfZVXV3vX4HUpqgLfZ1G3U8rA8i1cl7w5QNDZtoSHb6MX5Fn66sa9iFni1KIe8x-Uf2kYM6mDM",
            "bitrate": 2888231,
            "fps": 24,
            "audioQuality": None,
            "audioSampleRate": None,
            "mimeType": "video/webm; codecs=\"vp9\"",
            "duration": 3,
            "extension": "webm"
        },
        {
            "formatId": 136,
            "label": "mp4 (720p)",
            "type": "video",
            "ext": "mp4",
            "quality": "mp4 (720p)",
            "width": 1120,
            "height": 720,
            "url": "https://redirector.googlevideo.com/videoplayback?expire=1757984114&ei=EmHIaO7pNunbzPsPsoS0wAo&ip=178.133.164.253&id=o-AF_yKqtMLMS5E_Tj8fkPP-z4-wZXt33KwmVN8BE1bdYq&itag=136&aitags=133%2C134%2C135%2C136%2C137%2C160%2C242%2C243%2C244%2C247%2C248%2C271%2C278%2C313%2C394%2C395%2C396%2C397%2C398%2C399%2C400%2C401%2C598&source=youtube&requiressl=yes&xpc=EgVo2aDSNQ%3D%3D&met=1757962514%2C&mh=2x&mm=31%2C29&mn=sn-jvhnu5g03g-3c2z%2Csn-3c27sn7s&ms=au%2Crdu&mv=m&mvi=2&pl=25&rms=au%2Cau&initcwndbps=1003750&bui=AY1jyLPrRKSPs7w-py3YPFI6ZzzxRXkHh2vTttiFankTq28oke3V23LeYvK5csurVaQP7zDbR1FqdafE&spc=l3OVKTB7lM7NyX7wNagLLW5x4pVqRny05V4qDcr9_TnIY0YWSlx2SnO_o39IBB5G4b5dKGmFDtiuvkLrVIJ37_WT&vprv=1&svpuc=1&mime=video%2Fmp4&ns=EZOay5mK4ezir93Hthf78IEQ&rqh=1&gir=yes&clen=17368731&dur=204.541&lmt=1751195107413122&mt=1757961965&fvip=17&keepalive=yes&fexp=51331020%2C51552689%2C51565115%2C51565681%2C51580968&c=MWEB&sefc=1&txp=4532534&n=NV0OZWVsA3iW7w&sparams=expire%2Cei%2Cip%2Cid%2Caitags%2Csource%2Crequiressl%2Cxpc%2Cbui%2Cspc%2Cvprv%2Csvpuc%2Cmime%2Cns%2Crqh%2Cgir%2Cclen%2Cdur%2Clmt&sig=AJfQdSswRQIgbiBu7pVxTtz5kjM3MXDXuIxQlbExLbXBOfIibuF9qTACIQDhEIhWl3oyjQqwkKIszE42YNvCPZFpxXozcnkiy3-axQ%3D%3D&lsparams=met%2Cmh%2Cmm%2Cmn%2Cms%2Cmv%2Cmvi%2Cpl%2Crms%2Cinitcwndbps&lsig=APaTxxMwRQIhAN_GFt_7z03gfGcAJBeS0bgNht0gJMgbVD-_HEqGTwJzAiAaejtsmje9hVgTvcVUulsdggjw1WINJMvAujX854q04Q%3D%3D&pot=MnbXEQJFVEJcmNcv1FMM-aa1Z3ZjSiI2JX90LxmWfbUbvnK1t2dfnH0lzSA5Z2O1_CW2otEmJCcB-iYx_xwvuxnfZVXV3vX4HUpqgLfZ1G3U8rA8i1cl7w5QNDZtoSHb6MX5Fn66sa9iFni1KIe8x-Uf2kYM6mDM",
            "bitrate": 1358230,
            "fps": 24,
            "audioQuality": None,
            "audioSampleRate": None,
            "mimeType": "video/mp4; codecs=\"avc1.4d401f\"",
            "duration": 3,
            "extension": "mp4"
        },
        {
            "formatId": 247,
            "label": "webm (720p)",
            "type": "video",
            "ext": "webm",
            "quality": "webm (720p)",
            "width": 1120,
            "height": 720,
            "url": "https://redirector.googlevideo.com/videoplayback?expire=1757984114&ei=EmHIaO7pNunbzPsPsoS0wAo&ip=178.133.164.253&id=o-AF_yKqtMLMS5E_Tj8fkPP-z4-wZXt33KwmVN8BE1bdYq&itag=247&aitags=133%2C134%2C135%2C136%2C137%2C160%2C242%2C243%2C244%2C247%2C248%2C271%2C278%2C313%2C394%2C395%2C396%2C397%2C398%2C399%2C400%2C401%2C598&source=youtube&requiressl=yes&xpc=EgVo2aDSNQ%3D%3D&met=1757962514%2C&mh=2x&mm=31%2C29&mn=sn-jvhnu5g03g-3c2z%2Csn-3c27sn7s&ms=au%2Crdu&mv=m&mvi=2&pl=25&rms=au%2Cau&initcwndbps=1003750&bui=AY1jyLPrRKSPs7w-py3YPFI6ZzzxRXkHh2vTttiFankTq28oke3V23LeYvK5csurVaQP7zDbR1FqdafE&spc=l3OVKTB7lM7NyX7wNagLLW5x4pVqRny05V4qDcr9_TnIY0YWSlx2SnO_o39IBB5G4b5dKGmFDtiuvkLrVIJ37_WT&vprv=1&svpuc=1&mime=video%2Fwebm&ns=EZOay5mK4ezir93Hthf78IEQ&rqh=1&gir=yes&clen=21078055&dur=204.541&lmt=1751196227371918&mt=1757961965&fvip=17&keepalive=yes&fexp=51331020%2C51552689%2C51565115%2C51565681%2C51580968&c=MWEB&sefc=1&txp=4537534&n=NV0OZWVsA3iW7w&sparams=expire%2Cei%2Cip%2Cid%2Caitags%2Csource%2Crequiressl%2Cxpc%2Cbui%2Cspc%2Cvprv%2Csvpuc%2Cmime%2Cns%2Crqh%2Cgir%2Cclen%2Cdur%2Clmt&sig=AJfQdSswRQIge9fdMTYvFDeBsrWNbIsFCwT9DwbeW_tBb-dopA5DacECIQCf8EPLYh8amFt9CNlJztkLBfG_OalOIsBXf3kEpuCxLw%3D%3D&lsparams=met%2Cmh%2Cmm%2Cmn%2Cms%2Cmv%2Cmvi%2Cpl%2Crms%2Cinitcwndbps&lsig=APaTxxMwRQIhAN_GFt_7z03gfGcAJBeS0bgNht0gJMgbVD-_HEqGTwJzAiAaejtsmje9hVgTvcVUulsdggjw1WINJMvAujX854q04Q%3D%3D&pot=MnbXEQJFVEJcmNcv1FMM-aa1Z3ZjSiI2JX90LxmWfbUbvnK1t2dfnH0lzSA5Z2O1_CW2otEmJCcB-iYx_xwvuxnfZVXV3vX4HUpqgLfZ1G3U8rA8i1cl7w5QNDZtoSHb6MX5Fn66sa9iFni1KIe8x-Uf2kYM6mDM",
            "bitrate": 1764232,
            "fps": 24,
            "audioQuality": None,
            "audioSampleRate": None,
            "mimeType": "video/webm; codecs=\"vp9\"",
            "duration": 3,
            "extension": "webm"
        },
        {
            "formatId": 135,
            "label": "mp4 (480p)",
            "type": "video",
            "ext": "mp4",
            "quality": "mp4 (480p)",
            "width": 746,
            "height": 480,
            "url": "https://redirector.googlevideo.com/videoplayback?expire=1757984114&ei=EmHIaO7pNunbzPsPsoS0wAo&ip=178.133.164.253&id=o-AF_yKqtMLMS5E_Tj8fkPP-z4-wZXt33KwmVN8BE1bdYq&itag=135&aitags=133%2C134%2C135%2C136%2C137%2C160%2C242%2C243%2C244%2C247%2C248%2C271%2C278%2C313%2C394%2C395%2C396%2C397%2C398%2C399%2C400%2C401%2C598&source=youtube&requiressl=yes&xpc=EgVo2aDSNQ%3D%3D&met=1757962514%2C&mh=2x&mm=31%2C29&mn=sn-jvhnu5g03g-3c2z%2Csn-3c27sn7s&ms=au%2Crdu&mv=m&mvi=2&pl=25&rms=au%2Cau&initcwndbps=1003750&bui=AY1jyLPrRKSPs7w-py3YPFI6ZzzxRXkHh2vTttiFankTq28oke3V23LeYvK5csurVaQP7zDbR1FqdafE&spc=l3OVKTB7lM7NyX7wNagLLW5x4pVqRny05V4qDcr9_TnIY0YWSlx2SnO_o39IBB5G4b5dKGmFDtiuvkLrVIJ37_WT&vprv=1&svpuc=1&mime=video%2Fmp4&ns=EZOay5mK4ezir93Hthf78IEQ&rqh=1&gir=yes&clen=10159930&dur=204.541&lmt=1751194945839987&mt=1757961965&fvip=17&keepalive=yes&fexp=51331020%2C51552689%2C51565115%2C51565681%2C51580968&c=MWEB&sefc=1&txp=4532534&n=NV0OZWVsA3iW7w&sparams=expire%2Cei%2Cip%2Cid%2Caitags%2Csource%2Crequiressl%2Cxpc%2Cbui%2Cspc%2Cvprv%2Csvpuc%2Cmime%2Cns%2Crqh%2Cgir%2Cclen%2Cdur%2Clmt&sig=AJfQdSswRAIgcTqlB9F0rkZok-FM48aJlfhbvFtK9aD7F79IWgNjMc0CIDYOKpFey0c0OZ0jD6xPlkhZO20qvnmIxO4dWhnOypQT&lsparams=met%2Cmh%2Cmm%2Cmn%2Cms%2Cmv%2Cmvi%2Cpl%2Crms%2Cinitcwndbps&lsig=APaTxxMwRQIhAN_GFt_7z03gfGcAJBeS0bgNht0gJMgbVD-_HEqGTwJzAiAaejtsmje9hVgTvcVUulsdggjw1WINJMvAujX854q04Q%3D%3D&pot=MnbXEQJFVEJcmNcv1FMM-aa1Z3ZjSiI2JX90LxmWfbUbvnK1t2dfnH0lzSA5Z2O1_CW2otEmJCcB-iYx_xwvuxnfZVXV3vX4HUpqgLfZ1G3U8rA8i1cl7w5QNDZtoSHb6MX5Fn66sa9iFni1KIe8x-Uf2kYM6mDM",
            "bitrate": 962266,
            "fps": 24,
            "audioQuality": None,
            "audioSampleRate": None,
            "mimeType": "video/mp4; codecs=\"avc1.4d401e\"",
            "duration": 3,
            "extension": "mp4"
        },
        {
            "formatId": 244,
            "label": "webm (480p)",
            "type": "video",
            "ext": "webm",
            "quality": "webm (480p)",
            "width": 746,
            "height": 480,
            "url": "https://redirector.googlevideo.com/videoplayback?expire=1757984114&ei=EmHIaO7pNunbzPsPsoS0wAo&ip=178.133.164.253&id=o-AF_yKqtMLMS5E_Tj8fkPP-z4-wZXt33KwmVN8BE1bdYq&itag=244&aitags=133%2C134%2C135%2C136%2C137%2C160%2C242%2C243%2C244%2C247%2C248%2C271%2C278%2C313%2C394%2C395%2C396%2C397%2C398%2C399%2C400%2C401%2C598&source=youtube&requiressl=yes&xpc=EgVo2aDSNQ%3D%3D&met=1757962514%2C&mh=2x&mm=31%2C29&mn=sn-jvhnu5g03g-3c2z%2Csn-3c27sn7s&ms=au%2Crdu&mv=m&mvi=2&pl=25&rms=au%2Cau&initcwndbps=1003750&bui=AY1jyLPrRKSPs7w-py3YPFI6ZzzxRXkHh2vTttiFankTq28oke3V23LeYvK5csurVaQP7zDbR1FqdafE&spc=l3OVKTB7lM7NyX7wNagLLW5x4pVqRny05V4qDcr9_TnIY0YWSlx2SnO_o39IBB5G4b5dKGmFDtiuvkLrVIJ37_WT&vprv=1&svpuc=1&mime=video%2Fwebm&ns=EZOay5mK4ezir93Hthf78IEQ&rqh=1&gir=yes&clen=11301525&dur=204.541&lmt=1751196222193354&mt=1757961965&fvip=17&keepalive=yes&fexp=51331020%2C51552689%2C51565115%2C51565681%2C51580968&c=MWEB&sefc=1&txp=4537534&n=NV0OZWVsA3iW7w&sparams=expire%2Cei%2Cip%2Cid%2Caitags%2Csource%2Crequiressl%2Cxpc%2Cbui%2Cspc%2Cvprv%2Csvpuc%2Cmime%2Cns%2Crqh%2Cgir%2Cclen%2Cdur%2Clmt&sig=AJfQdSswRQIhAIKcTyN4owL-RtUJAGDB0M6lsiq1cPKU5datnSM8GfbNAiBtVACMvUnUhEoQ-peiNjLurGV0dOIjzqAKevIWszQS1g%3D%3D&lsparams=met%2Cmh%2Cmm%2Cmn%2Cms%2Cmv%2Cmvi%2Cpl%2Crms%2Cinitcwndbps&lsig=APaTxxMwRQIhAN_GFt_7z03gfGcAJBeS0bgNht0gJMgbVD-_HEqGTwJzAiAaejtsmje9hVgTvcVUulsdggjw1WINJMvAujX854q04Q%3D%3D&pot=MnbXEQJFVEJcmNcv1FMM-aa1Z3ZjSiI2JX90LxmWfbUbvnK1t2dfnH0lzSA5Z2O1_CW2otEmJCcB-iYx_xwvuxnfZVXV3vX4HUpqgLfZ1G3U8rA8i1cl7w5QNDZtoSHb6MX5Fn66sa9iFni1KIe8x-Uf2kYM6mDM",
            "bitrate": 960273,
            "fps": 24,
            "audioQuality": None,
            "audioSampleRate": None,
            "mimeType": "video/webm; codecs=\"vp9\"",
            "duration": 3,
            "extension": "webm"
        },
        {
            "formatId": 134,
            "label": "mp4 (360p)",
            "type": "video",
            "ext": "mp4",
            "quality": "mp4 (360p)",
            "width": 560,
            "height": 360,
            "url": "https://redirector.googlevideo.com/videoplayback?expire=1757984114&ei=EmHIaO7pNunbzPsPsoS0wAo&ip=178.133.164.253&id=o-AF_yKqtMLMS5E_Tj8fkPP-z4-wZXt33KwmVN8BE1bdYq&itag=134&aitags=133%2C134%2C135%2C136%2C137%2C160%2C242%2C243%2C244%2C247%2C248%2C271%2C278%2C313%2C394%2C395%2C396%2C397%2C398%2C399%2C400%2C401%2C598&source=youtube&requiressl=yes&xpc=EgVo2aDSNQ%3D%3D&met=1757962514%2C&mh=2x&mm=31%2C29&mn=sn-jvhnu5g03g-3c2z%2Csn-3c27sn7s&ms=au%2Crdu&mv=m&mvi=2&pl=25&rms=au%2Cau&initcwndbps=1003750&bui=AY1jyLPrRKSPs7w-py3YPFI6ZzzxRXkHh2vTttiFankTq28oke3V23LeYvK5csurVaQP7zDbR1FqdafE&spc=l3OVKTB7lM7NyX7wNagLLW5x4pVqRny05V4qDcr9_TnIY0YWSlx2SnO_o39IBB5G4b5dKGmFDtiuvkLrVIJ37_WT&vprv=1&svpuc=1&mime=video%2Fmp4&ns=EZOay5mK4ezir93Hthf78IEQ&rqh=1&gir=yes&clen=6150735&dur=204.541&lmt=1751195124492900&mt=1757961965&fvip=17&keepalive=yes&fexp=51331020%2C51552689%2C51565115%2C51565681%2C51580968&c=MWEB&sefc=1&txp=4532534&n=NV0OZWVsA3iW7w&sparams=expire%2Cei%2Cip%2Cid%2Caitags%2Csource%2Crequiressl%2Cxpc%2Cbui%2Cspc%2Cvprv%2Csvpuc%2Cmime%2Cns%2Crqh%2Cgir%2Cclen%2Cdur%2Clmt&sig=AJfQdSswRQIgXBBcuZL17O7-eNcpYooIvTcfzR9Wkpa7dHuUbTw7YfICIQCl4Uhqk0bLma_ufMzw4qPPvtdnc6hU6LkmZ7u804MVBQ%3D%3D&lsparams=met%2Cmh%2Cmm%2Cmn%2Cms%2Cmv%2Cmvi%2Cpl%2Crms%2Cinitcwndbps&lsig=APaTxxMwRQIhAN_GFt_7z03gfGcAJBeS0bgNht0gJMgbVD-_HEqGTwJzAiAaejtsmje9hVgTvcVUulsdggjw1WINJMvAujX854q04Q%3D%3D&pot=MnbXEQJFVEJcmNcv1FMM-aa1Z3ZjSiI2JX90LxmWfbUbvnK1t2dfnH0lzSA5Z2O1_CW2otEmJCcB-iYx_xwvuxnfZVXV3vX4HUpqgLfZ1G3U8rA8i1cl7w5QNDZtoSHb6MX5Fn66sa9iFni1KIe8x-Uf2kYM6mDM",
            "bitrate": 553404,
            "fps": 24,
            "audioQuality": None,
            "audioSampleRate": None,
            "mimeType": "video/mp4; codecs=\"avc1.4d4016\"",
            "duration": 3,
            "extension": "mp4"
        },
        {
            "formatId": 243,
            "label": "webm (360p)",
            "type": "video",
            "ext": "webm",
            "quality": "webm (360p)",
            "width": 560,
            "height": 360,
            "url": "https://redirector.googlevideo.com/videoplayback?expire=1757984114&ei=EmHIaO7pNunbzPsPsoS0wAo&ip=178.133.164.253&id=o-AF_yKqtMLMS5E_Tj8fkPP-z4-wZXt33KwmVN8BE1bdYq&itag=243&aitags=133%2C134%2C135%2C136%2C137%2C160%2C242%2C243%2C244%2C247%2C248%2C271%2C278%2C313%2C394%2C395%2C396%2C397%2C398%2C399%2C400%2C401%2C598&source=youtube&requiressl=yes&xpc=EgVo2aDSNQ%3D%3D&met=1757962514%2C&mh=2x&mm=31%2C29&mn=sn-jvhnu5g03g-3c2z%2Csn-3c27sn7s&ms=au%2Crdu&mv=m&mvi=2&pl=25&rms=au%2Cau&initcwndbps=1003750&bui=AY1jyLPrRKSPs7w-py3YPFI6ZzzxRXkHh2vTttiFankTq28oke3V23LeYvK5csurVaQP7zDbR1FqdafE&spc=l3OVKTB7lM7NyX7wNagLLW5x4pVqRny05V4qDcr9_TnIY0YWSlx2SnO_o39IBB5G4b5dKGmFDtiuvkLrVIJ37_WT&vprv=1&svpuc=1&mime=video%2Fwebm&ns=EZOay5mK4ezir93Hthf78IEQ&rqh=1&gir=yes&clen=7060317&dur=204.541&lmt=1751196222385979&mt=1757961965&fvip=17&keepalive=yes&fexp=51331020%2C51552689%2C51565115%2C51565681%2C51580968&c=MWEB&sefc=1&txp=4537534&n=NV0OZWVsA3iW7w&sparams=expire%2Cei%2Cip%2Cid%2Caitags%2Csource%2Crequiressl%2Cxpc%2Cbui%2Cspc%2Cvprv%2Csvpuc%2Cmime%2Cns%2Crqh%2Cgir%2Cclen%2Cdur%2Clmt&sig=AJfQdSswRgIhALfOz_7yiX7cRu-MmwSjztgh1S8Rtj0YwoKkEXzLD_UkAiEA2gcBJBahzQLkoFuqhdI5N-Po3G1Q4UevGUa9QW3u9HQ%3D&lsparams=met%2Cmh%2Cmm%2Cmn%2Cms%2Cmv%2Cmvi%2Cpl%2Crms%2Cinitcwndbps&lsig=APaTxxMwRQIhAN_GFt_7z03gfGcAJBeS0bgNht0gJMgbVD-_HEqGTwJzAiAaejtsmje9hVgTvcVUulsdggjw1WINJMvAujX854q04Q%3D%3D&pot=MnbXEQJFVEJcmNcv1FMM-aa1Z3ZjSiI2JX90LxmWfbUbvnK1t2dfnH0lzSA5Z2O1_CW2otEmJCcB-iYx_xwvuxnfZVXV3vX4HUpqgLfZ1G3U8rA8i1cl7w5QNDZtoSHb6MX5Fn66sa9iFni1KIe8x-Uf2kYM6mDM",
            "bitrate": 557013,
            "fps": 24,
            "audioQuality": None,
            "audioSampleRate": None,
            "mimeType": "video/webm; codecs=\"vp9\"",
            "duration": 3,
            "extension": "webm"
        },
        {
            "formatId": 133,
            "label": "mp4 (240p)",
            "type": "video",
            "ext": "mp4",
            "quality": "mp4 (240p)",
            "width": 374,
            "height": 240,
            "url": "https://redirector.googlevideo.com/videoplayback?expire=1757984114&ei=EmHIaO7pNunbzPsPsoS0wAo&ip=178.133.164.253&id=o-AF_yKqtMLMS5E_Tj8fkPP-z4-wZXt33KwmVN8BE1bdYq&itag=133&aitags=133%2C134%2C135%2C136%2C137%2C160%2C242%2C243%2C244%2C247%2C248%2C271%2C278%2C313%2C394%2C395%2C396%2C397%2C398%2C399%2C400%2C401%2C598&source=youtube&requiressl=yes&xpc=EgVo2aDSNQ%3D%3D&met=1757962514%2C&mh=2x&mm=31%2C29&mn=sn-jvhnu5g03g-3c2z%2Csn-3c27sn7s&ms=au%2Crdu&mv=m&mvi=2&pl=25&rms=au%2Cau&initcwndbps=1003750&bui=AY1jyLPrRKSPs7w-py3YPFI6ZzzxRXkHh2vTttiFankTq28oke3V23LeYvK5csurVaQP7zDbR1FqdafE&spc=l3OVKTB7lM7NyX7wNagLLW5x4pVqRny05V4qDcr9_TnIY0YWSlx2SnO_o39IBB5G4b5dKGmFDtiuvkLrVIJ37_WT&vprv=1&svpuc=1&mime=video%2Fmp4&ns=EZOay5mK4ezir93Hthf78IEQ&rqh=1&gir=yes&clen=3143408&dur=204.541&lmt=1751194874878677&mt=1757961965&fvip=17&keepalive=yes&fexp=51331020%2C51552689%2C51565115%2C51565681%2C51580968&c=MWEB&sefc=1&txp=4532534&n=NV0OZWVsA3iW7w&sparams=expire%2Cei%2Cip%2Cid%2Caitags%2Csource%2Crequiressl%2Cxpc%2Cbui%2Cspc%2Cvprv%2Csvpuc%2Cmime%2Cns%2Crqh%2Cgir%2Cclen%2Cdur%2Clmt&sig=AJfQdSswRgIhAPnhXXiCXAhCfTi7VgKUcky3kkUByHh_7MsSntMjysxvAiEA9w0KwukOmuAEKWXQps_tAtb5vM_OutFWtSIXQ0weclY%3D&lsparams=met%2Cmh%2Cmm%2Cmn%2Cms%2Cmv%2Cmvi%2Cpl%2Crms%2Cinitcwndbps&lsig=APaTxxMwRQIhAN_GFt_7z03gfGcAJBeS0bgNht0gJMgbVD-_HEqGTwJzAiAaejtsmje9hVgTvcVUulsdggjw1WINJMvAujX854q04Q%3D%3D&pot=MnbXEQJFVEJcmNcv1FMM-aa1Z3ZjSiI2JX90LxmWfbUbvnK1t2dfnH0lzSA5Z2O1_CW2otEmJCcB-iYx_xwvuxnfZVXV3vX4HUpqgLfZ1G3U8rA8i1cl7w5QNDZtoSHb6MX5Fn66sa9iFni1KIe8x-Uf2kYM6mDM",
            "bitrate": 214673,
            "fps": 24,
            "audioQuality": None,
            "audioSampleRate": None,
            "mimeType": "video/mp4; codecs=\"avc1.4d400d\"",
            "duration": 3,
            "extension": "mp4"
        },
        {
            "formatId": 242,
            "label": "webm (240p)",
            "type": "video",
            "ext": "webm",
            "quality": "webm (240p)",
            "width": 374,
            "height": 240,
            "url": "https://redirector.googlevideo.com/videoplayback?expire=1757984114&ei=EmHIaO7pNunbzPsPsoS0wAo&ip=178.133.164.253&id=o-AF_yKqtMLMS5E_Tj8fkPP-z4-wZXt33KwmVN8BE1bdYq&itag=242&aitags=133%2C134%2C135%2C136%2C137%2C160%2C242%2C243%2C244%2C247%2C248%2C271%2C278%2C313%2C394%2C395%2C396%2C397%2C398%2C399%2C400%2C401%2C598&source=youtube&requiressl=yes&xpc=EgVo2aDSNQ%3D%3D&met=1757962514%2C&mh=2x&mm=31%2C29&mn=sn-jvhnu5g03g-3c2z%2Csn-3c27sn7s&ms=au%2Crdu&mv=m&mvi=2&pl=25&rms=au%2Cau&initcwndbps=1003750&bui=AY1jyLPrRKSPs7w-py3YPFI6ZzzxRXkHh2vTttiFankTq28oke3V23LeYvK5csurVaQP7zDbR1FqdafE&spc=l3OVKTB7lM7NyX7wNagLLW5x4pVqRny05V4qDcr9_TnIY0YWSlx2SnO_o39IBB5G4b5dKGmFDtiuvkLrVIJ37_WT&vprv=1&svpuc=1&mime=video%2Fwebm&ns=EZOay5mK4ezir93Hthf78IEQ&rqh=1&gir=yes&clen=3372661&dur=204.541&lmt=1751196222296958&mt=1757961965&fvip=17&keepalive=yes&fexp=51331020%2C51552689%2C51565115%2C51565681%2C51580968&c=MWEB&sefc=1&txp=4537534&n=NV0OZWVsA3iW7w&sparams=expire%2Cei%2Cip%2Cid%2Caitags%2Csource%2Crequiressl%2Cxpc%2Cbui%2Cspc%2Cvprv%2Csvpuc%2Cmime%2Cns%2Crqh%2Cgir%2Cclen%2Cdur%2Clmt&sig=AJfQdSswRgIhAL88JO5W9NWuXUI6uJoocQXQD69kWPa73MAn9DsC5VDCAiEAzQOc0_R1qiQUgmTfWLYHK_I2ei8VaJBwTeRsFLQrx_k%3D&lsparams=met%2Cmh%2Cmm%2Cmn%2Cms%2Cmv%2Cmvi%2Cpl%2Crms%2Cinitcwndbps&lsig=APaTxxMwRQIhAN_GFt_7z03gfGcAJBeS0bgNht0gJMgbVD-_HEqGTwJzAiAaejtsmje9hVgTvcVUulsdggjw1WINJMvAujX854q04Q%3D%3D&pot=MnbXEQJFVEJcmNcv1FMM-aa1Z3ZjSiI2JX90LxmWfbUbvnK1t2dfnH0lzSA5Z2O1_CW2otEmJCcB-iYx_xwvuxnfZVXV3vX4HUpqgLfZ1G3U8rA8i1cl7w5QNDZtoSHb6MX5Fn66sa9iFni1KIe8x-Uf2kYM6mDM",
            "bitrate": 238469,
            "fps": 24,
            "audioQuality": None,
            "audioSampleRate": None,
            "mimeType": "video/webm; codecs=\"vp9\"",
            "duration": 3,
            "extension": "webm"
        },
        {
            "formatId": 160,
            "label": "mp4 (144p)",
            "type": "video",
            "ext": "mp4",
            "quality": "mp4 (144p)",
            "width": 224,
            "height": 144,
            "url": "https://redirector.googlevideo.com/videoplayback?expire=1757984114&ei=EmHIaO7pNunbzPsPsoS0wAo&ip=178.133.164.253&id=o-AF_yKqtMLMS5E_Tj8fkPP-z4-wZXt33KwmVN8BE1bdYq&itag=160&aitags=133%2C134%2C135%2C136%2C137%2C160%2C242%2C243%2C244%2C247%2C248%2C271%2C278%2C313%2C394%2C395%2C396%2C397%2C398%2C399%2C400%2C401%2C598&source=youtube&requiressl=yes&xpc=EgVo2aDSNQ%3D%3D&met=1757962514%2C&mh=2x&mm=31%2C29&mn=sn-jvhnu5g03g-3c2z%2Csn-3c27sn7s&ms=au%2Crdu&mv=m&mvi=2&pl=25&rms=au%2Cau&initcwndbps=1003750&bui=AY1jyLPrRKSPs7w-py3YPFI6ZzzxRXkHh2vTttiFankTq28oke3V23LeYvK5csurVaQP7zDbR1FqdafE&spc=l3OVKTB7lM7NyX7wNagLLW5x4pVqRny05V4qDcr9_TnIY0YWSlx2SnO_o39IBB5G4b5dKGmFDtiuvkLrVIJ37_WT&vprv=1&svpuc=1&mime=video%2Fmp4&ns=EZOay5mK4ezir93Hthf78IEQ&rqh=1&gir=yes&clen=1415801&dur=204.541&lmt=1751195106292874&mt=1757961965&fvip=17&keepalive=yes&fexp=51331020%2C51552689%2C51565115%2C51565681%2C51580968&c=MWEB&sefc=1&txp=4532534&n=NV0OZWVsA3iW7w&sparams=expire%2Cei%2Cip%2Cid%2Caitags%2Csource%2Crequiressl%2Cxpc%2Cbui%2Cspc%2Cvprv%2Csvpuc%2Cmime%2Cns%2Crqh%2Cgir%2Cclen%2Cdur%2Clmt&sig=AJfQdSswRQIhAMH6mRydFZCxaoMiuBNqh6SB2G0p-9Q5PuuSluUkwR2xAiACLxHQE9BUw9czlHqutTqWscWI9g6H0lV7V8y2B9GjiQ%3D%3D&lsparams=met%2Cmh%2Cmm%2Cmn%2Cms%2Cmv%2Cmvi%2Cpl%2Crms%2Cinitcwndbps&lsig=APaTxxMwRQIhAN_GFt_7z03gfGcAJBeS0bgNht0gJMgbVD-_HEqGTwJzAiAaejtsmje9hVgTvcVUulsdggjw1WINJMvAujX854q04Q%3D%3D&pot=MnbXEQJFVEJcmNcv1FMM-aa1Z3ZjSiI2JX90LxmWfbUbvnK1t2dfnH0lzSA5Z2O1_CW2otEmJCcB-iYx_xwvuxnfZVXV3vX4HUpqgLfZ1G3U8rA8i1cl7w5QNDZtoSHb6MX5Fn66sa9iFni1KIe8x-Uf2kYM6mDM",
            "bitrate": 96781,
            "fps": 24,
            "audioQuality": None,
            "audioSampleRate": None,
            "mimeType": "video/mp4; codecs=\"avc1.4d400c\"",
            "duration": 3,
            "extension": "mp4"
        },
        {
            "formatId": 278,
            "label": "webm (144p)",
            "type": "video",
            "ext": "webm",
            "quality": "webm (144p)",
            "width": 224,
            "height": 144,
            "url": "https://redirector.googlevideo.com/videoplayback?expire=1757984114&ei=EmHIaO7pNunbzPsPsoS0wAo&ip=178.133.164.253&id=o-AF_yKqtMLMS5E_Tj8fkPP-z4-wZXt33KwmVN8BE1bdYq&itag=278&aitags=133%2C134%2C135%2C136%2C137%2C160%2C242%2C243%2C244%2C247%2C248%2C271%2C278%2C313%2C394%2C395%2C396%2C397%2C398%2C399%2C400%2C401%2C598&source=youtube&requiressl=yes&xpc=EgVo2aDSNQ%3D%3D&met=1757962514%2C&mh=2x&mm=31%2C29&mn=sn-jvhnu5g03g-3c2z%2Csn-3c27sn7s&ms=au%2Crdu&mv=m&mvi=2&pl=25&rms=au%2Cau&initcwndbps=1003750&bui=AY1jyLPrRKSPs7w-py3YPFI6ZzzxRXkHh2vTttiFankTq28oke3V23LeYvK5csurVaQP7zDbR1FqdafE&spc=l3OVKTB7lM7NyX7wNagLLW5x4pVqRny05V4qDcr9_TnIY0YWSlx2SnO_o39IBB5G4b5dKGmFDtiuvkLrVIJ37_WT&vprv=1&svpuc=1&mime=video%2Fwebm&ns=EZOay5mK4ezir93Hthf78IEQ&rqh=1&gir=yes&clen=1937839&dur=204.541&lmt=1751196222888088&mt=1757961965&fvip=17&keepalive=yes&fexp=51331020%2C51552689%2C51565115%2C51565681%2C51580968&c=MWEB&sefc=1&txp=4537534&n=NV0OZWVsA3iW7w&sparams=expire%2Cei%2Cip%2Cid%2Caitags%2Csource%2Crequiressl%2Cxpc%2Cbui%2Cspc%2Cvprv%2Csvpuc%2Cmime%2Cns%2Crqh%2Cgir%2Cclen%2Cdur%2Clmt&sig=AJfQdSswRgIhANdoXK6ZOnpmUZV68GP5q_yIOYctZD-5ax2-2gI4jYlZAiEAywtWCyxEUe7S-uK_IHLiMXXNl_dQn_T9LSDUp86xg4A%3D&lsparams=met%2Cmh%2Cmm%2Cmn%2Cms%2Cmv%2Cmvi%2Cpl%2Crms%2Cinitcwndbps&lsig=APaTxxMwRQIhAN_GFt_7z03gfGcAJBeS0bgNht0gJMgbVD-_HEqGTwJzAiAaejtsmje9hVgTvcVUulsdggjw1WINJMvAujX854q04Q%3D%3D&pot=MnbXEQJFVEJcmNcv1FMM-aa1Z3ZjSiI2JX90LxmWfbUbvnK1t2dfnH0lzSA5Z2O1_CW2otEmJCcB-iYx_xwvuxnfZVXV3vX4HUpqgLfZ1G3U8rA8i1cl7w5QNDZtoSHb6MX5Fn66sa9iFni1KIe8x-Uf2kYM6mDM",
            "bitrate": 117960,
            "fps": 24,
            "audioQuality": None,
            "audioSampleRate": None,
            "mimeType": "video/webm; codecs=\"vp9\"",
            "duration": 3,
            "extension": "webm"
        },
        {
            "formatId": 140,
            "label": "m4a (131kb/s)",
            "type": "audio",
            "ext": "m4a",
            "width": None,
            "height": None,
            "url": "https://redirector.googlevideo.com/videoplayback?expire=1757984114&ei=EmHIaO7pNunbzPsPsoS0wAo&ip=178.133.164.253&id=o-AF_yKqtMLMS5E_Tj8fkPP-z4-wZXt33KwmVN8BE1bdYq&itag=140&source=youtube&requiressl=yes&xpc=EgVo2aDSNQ%3D%3D&met=1757962514%2C&mh=2x&mm=31%2C29&mn=sn-jvhnu5g03g-3c2z%2Csn-3c27sn7s&ms=au%2Crdu&mv=m&mvi=2&pl=25&rms=au%2Cau&initcwndbps=1003750&bui=AY1jyLPrRKSPs7w-py3YPFI6ZzzxRXkHh2vTttiFankTq28oke3V23LeYvK5csurVaQP7zDbR1FqdafE&spc=l3OVKTB7lM7NyX7wNagLLW5x4pVqRny05V4qDcr9_TnIY0YWSlx2SnO_o39IBB5G4b5dKGmFDtiuvkLrVIJ37_WT&vprv=1&svpuc=1&mime=audio%2Fmp4&ns=EZOay5mK4ezir93Hthf78IEQ&rqh=1&gir=yes&clen=3312266&dur=204.614&lmt=1751194241706588&mt=1757961965&fvip=17&keepalive=yes&fexp=51331020%2C51552689%2C51565115%2C51565681%2C51580968&c=MWEB&sefc=1&txp=4532534&n=NV0OZWVsA3iW7w&sparams=expire%2Cei%2Cip%2Cid%2Citag%2Csource%2Crequiressl%2Cxpc%2Cbui%2Cspc%2Cvprv%2Csvpuc%2Cmime%2Cns%2Crqh%2Cgir%2Cclen%2Cdur%2Clmt&sig=AJfQdSswRQIgStlPNBURnBNKYGuPV2HGzRzYyj4LrHj55SIvTDIX3CECIQDGNUqDgA9bur7G6xJLH3RoHRQbj-TA5PErvSdG7AeK1A%3D%3D&lsparams=met%2Cmh%2Cmm%2Cmn%2Cms%2Cmv%2Cmvi%2Cpl%2Crms%2Cinitcwndbps&lsig=APaTxxMwRQIhAN_GFt_7z03gfGcAJBeS0bgNht0gJMgbVD-_HEqGTwJzAiAaejtsmje9hVgTvcVUulsdggjw1WINJMvAujX854q04Q%3D%3D&pot=MnbXEQJFVEJcmNcv1FMM-aa1Z3ZjSiI2JX90LxmWfbUbvnK1t2dfnH0lzSA5Z2O1_CW2otEmJCcB-iYx_xwvuxnfZVXV3vX4HUpqgLfZ1G3U8rA8i1cl7w5QNDZtoSHb6MX5Fn66sa9iFni1KIe8x-Uf2kYM6mDM",
            "bitrate": 130668,
            "fps": None,
            "audioQuality": "AUDIO_QUALITY_MEDIUM",
            "audioSampleRate": "44100",
            "mimeType": "audio/mp4; codecs=\"mp4a.40.2\"",
            "duration": 3,
            "quality": "m4a (131kb/s)",
            "extension": "m4a"
        },
        {
            "formatId": 249,
            "label": "opus (63kb/s)",
            "type": "audio",
            "ext": "opus",
            "width": None,
            "height": None,
            "url": "https://redirector.googlevideo.com/videoplayback?expire=1757984114&ei=EmHIaO7pNunbzPsPsoS0wAo&ip=178.133.164.253&id=o-AF_yKqtMLMS5E_Tj8fkPP-z4-wZXt33KwmVN8BE1bdYq&itag=249&source=youtube&requiressl=yes&xpc=EgVo2aDSNQ%3D%3D&met=1757962514%2C&mh=2x&mm=31%2C29&mn=sn-jvhnu5g03g-3c2z%2Csn-3c27sn7s&ms=au%2Crdu&mv=m&mvi=2&pl=25&rms=au%2Cau&initcwndbps=1003750&bui=AY1jyLPrRKSPs7w-py3YPFI6ZzzxRXkHh2vTttiFankTq28oke3V23LeYvK5csurVaQP7zDbR1FqdafE&spc=l3OVKTB7lM7NyX7wNagLLW5x4pVqRny05V4qDcr9_TnIY0YWSlx2SnO_o39IBB5G4b5dKGmFDtiuvkLrVIJ37_WT&vprv=1&svpuc=1&mime=audio%2Fwebm&ns=EZOay5mK4ezir93Hthf78IEQ&rqh=1&gir=yes&clen=1433332&dur=204.581&lmt=1751194185266151&mt=1757961965&fvip=17&keepalive=yes&fexp=51331020%2C51552689%2C51565115%2C51565681%2C51580968&c=MWEB&sefc=1&txp=4532534&n=NV0OZWVsA3iW7w&sparams=expire%2Cei%2Cip%2Cid%2Citag%2Csource%2Crequiressl%2Cxpc%2Cbui%2Cspc%2Cvprv%2Csvpuc%2Cmime%2Cns%2Crqh%2Cgir%2Cclen%2Cdur%2Clmt&sig=AJfQdSswRQIgMHS93EA_RY2nH-UkpkQTRxTdcmDDVKKb57to0caif_oCIQC-8LNzR2_6WYnVXJFkdYocNB5xkyD4rgvruVbZtsPjrw%3D%3D&lsparams=met%2Cmh%2Cmm%2Cmn%2Cms%2Cmv%2Cmvi%2Cpl%2Crms%2Cinitcwndbps&lsig=APaTxxMwRQIhAN_GFt_7z03gfGcAJBeS0bgNht0gJMgbVD-_HEqGTwJzAiAaejtsmje9hVgTvcVUulsdggjw1WINJMvAujX854q04Q%3D%3D&pot=MnbXEQJFVEJcmNcv1FMM-aa1Z3ZjSiI2JX90LxmWfbUbvnK1t2dfnH0lzSA5Z2O1_CW2otEmJCcB-iYx_xwvuxnfZVXV3vX4HUpqgLfZ1G3U8rA8i1cl7w5QNDZtoSHb6MX5Fn66sa9iFni1KIe8x-Uf2kYM6mDM",
            "bitrate": 63221,
            "fps": None,
            "audioQuality": "AUDIO_QUALITY_LOW",
            "audioSampleRate": "48000",
            "mimeType": "audio/webm; codecs=\"opus\"",
            "duration": 3,
            "quality": "opus (63kb/s)",
            "extension": "opus"
        },
        {
            "formatId": 250,
            "label": "opus (81kb/s)",
            "type": "audio",
            "ext": "opus",
            "width": None,
            "height": None,
            "url": "https://redirector.googlevideo.com/videoplayback?expire=1757984114&ei=EmHIaO7pNunbzPsPsoS0wAo&ip=178.133.164.253&id=o-AF_yKqtMLMS5E_Tj8fkPP-z4-wZXt33KwmVN8BE1bdYq&itag=250&source=youtube&requiressl=yes&xpc=EgVo2aDSNQ%3D%3D&met=1757962514%2C&mh=2x&mm=31%2C29&mn=sn-jvhnu5g03g-3c2z%2Csn-3c27sn7s&ms=au%2Crdu&mv=m&mvi=2&pl=25&rms=au%2Cau&initcwndbps=1003750&bui=AY1jyLPrRKSPs7w-py3YPFI6ZzzxRXkHh2vTttiFankTq28oke3V23LeYvK5csurVaQP7zDbR1FqdafE&spc=l3OVKTB7lM7NyX7wNagLLW5x4pVqRny05V4qDcr9_TnIY0YWSlx2SnO_o39IBB5G4b5dKGmFDtiuvkLrVIJ37_WT&vprv=1&svpuc=1&mime=audio%2Fwebm&ns=EZOay5mK4ezir93Hthf78IEQ&rqh=1&gir=yes&clen=1861938&dur=204.581&lmt=1751194185221635&mt=1757961965&fvip=17&keepalive=yes&fexp=51331020%2C51552689%2C51565115%2C51565681%2C51580968&c=MWEB&sefc=1&txp=4532534&n=NV0OZWVsA3iW7w&sparams=expire%2Cei%2Cip%2Cid%2Citag%2Csource%2Crequiressl%2Cxpc%2Cbui%2Cspc%2Cvprv%2Csvpuc%2Cmime%2Cns%2Crqh%2Cgir%2Cclen%2Cdur%2Clmt&sig=AJfQdSswRAIgd8611QNC6TsDSNLbUiN47aJ4tAQYgB4phEgpkqDE4zECIAp7q7hrOCsXwvQsNZ-cOQNAbF7WoaSIXZRpwnl3oUSH&lsparams=met%2Cmh%2Cmm%2Cmn%2Cms%2Cmv%2Cmvi%2Cpl%2Crms%2Cinitcwndbps&lsig=APaTxxMwRQIhAN_GFt_7z03gfGcAJBeS0bgNht0gJMgbVD-_HEqGTwJzAiAaejtsmje9hVgTvcVUulsdggjw1WINJMvAujX854q04Q%3D%3D&pot=MnbXEQJFVEJcmNcv1FMM-aa1Z3ZjSiI2JX90LxmWfbUbvnK1t2dfnH0lzSA5Z2O1_CW2otEmJCcB-iYx_xwvuxnfZVXV3vX4HUpqgLfZ1G3U8rA8i1cl7w5QNDZtoSHb6MX5Fn66sa9iFni1KIe8x-Uf2kYM6mDM",
            "bitrate": 80696,
            "fps": None,
            "audioQuality": "AUDIO_QUALITY_LOW",
            "audioSampleRate": "48000",
            "mimeType": "audio/webm; codecs=\"opus\"",
            "duration": 3,
            "quality": "opus (81kb/s)",
            "extension": "opus"
        },
        {
            "formatId": 251,
            "label": "opus (148kb/s)",
            "type": "audio",
            "ext": "opus",
            "width": None,
            "height": None,
            "url": "https://redirector.googlevideo.com/videoplayback?expire=1757984114&ei=EmHIaO7pNunbzPsPsoS0wAo&ip=178.133.164.253&id=o-AF_yKqtMLMS5E_Tj8fkPP-z4-wZXt33KwmVN8BE1bdYq&itag=251&source=youtube&requiressl=yes&xpc=EgVo2aDSNQ%3D%3D&met=1757962514%2C&mh=2x&mm=31%2C29&mn=sn-jvhnu5g03g-3c2z%2Csn-3c27sn7s&ms=au%2Crdu&mv=m&mvi=2&pl=25&rms=au%2Cau&initcwndbps=1003750&bui=AY1jyLPrRKSPs7w-py3YPFI6ZzzxRXkHh2vTttiFankTq28oke3V23LeYvK5csurVaQP7zDbR1FqdafE&spc=l3OVKTB7lM7NyX7wNagLLW5x4pVqRny05V4qDcr9_TnIY0YWSlx2SnO_o39IBB5G4b5dKGmFDtiuvkLrVIJ37_WT&vprv=1&svpuc=1&mime=audio%2Fwebm&ns=EZOay5mK4ezir93Hthf78IEQ&rqh=1&gir=yes&clen=3592779&dur=204.581&lmt=1751194185544582&mt=1757961965&fvip=17&keepalive=yes&fexp=51331020%2C51552689%2C51565115%2C51565681%2C51580968&c=MWEB&sefc=1&txp=4532534&n=NV0OZWVsA3iW7w&sparams=expire%2Cei%2Cip%2Cid%2Citag%2Csource%2Crequiressl%2Cxpc%2Cbui%2Cspc%2Cvprv%2Csvpuc%2Cmime%2Cns%2Crqh%2Cgir%2Cclen%2Cdur%2Clmt&sig=AJfQdSswRAIgN-aahooPJrUlKeSJhqoTYajzhwVY3LlF9biffSr6qwMCIHcEw4C8_LWteMNoBeCzUW4NDdxR2XLY7nGV_ECSacUn&lsparams=met%2Cmh%2Cmm%2Cmn%2Cms%2Cmv%2Cmvi%2Cpl%2Crms%2Cinitcwndbps&lsig=APaTxxMwRQIhAN_GFt_7z03gfGcAJBeS0bgNht0gJMgbVD-_HEqGTwJzAiAaejtsmje9hVgTvcVUulsdggjw1WINJMvAujX854q04Q%3D%3D&pot=MnbXEQJFVEJcmNcv1FMM-aa1Z3ZjSiI2JX90LxmWfbUbvnK1t2dfnH0lzSA5Z2O1_CW2otEmJCcB-iYx_xwvuxnfZVXV3vX4HUpqgLfZ1G3U8rA8i1cl7w5QNDZtoSHb6MX5Fn66sa9iFni1KIe8x-Uf2kYM6mDM",
            "bitrate": 148229,
            "fps": None,
            "audioQuality": "AUDIO_QUALITY_MEDIUM",
            "audioSampleRate": "48000",
            "mimeType": "audio/webm; codecs=\"opus\"",
            "duration": 3,
            "quality": "opus (148kb/s)",
            "extension": "opus"
        },
        {
            "formatId": 599,
            "label": "m4a (32kb/s)",
            "type": "audio",
            "ext": "m4a",
            "width": None,
            "height": None,
            "url": "https://redirector.googlevideo.com/videoplayback?expire=1757984114&ei=EmHIaO7pNunbzPsPsoS0wAo&ip=178.133.164.253&id=o-AF_yKqtMLMS5E_Tj8fkPP-z4-wZXt33KwmVN8BE1bdYq&itag=599&source=youtube&requiressl=yes&xpc=EgVo2aDSNQ%3D%3D&met=1757962514%2C&mh=2x&mm=31%2C29&mn=sn-jvhnu5g03g-3c2z%2Csn-3c27sn7s&ms=au%2Crdu&mv=m&mvi=2&pl=25&rms=au%2Cau&initcwndbps=1003750&bui=AY1jyLPrRKSPs7w-py3YPFI6ZzzxRXkHh2vTttiFankTq28oke3V23LeYvK5csurVaQP7zDbR1FqdafE&spc=l3OVKTB7lM7NyX7wNagLLW5x4pVqRny05V4qDcr9_TnIY0YWSlx2SnO_o39IBB5G4b5dKGmFDtiuvkLrVIJ37_WT&vprv=1&svpuc=1&mime=audio%2Fmp4&ns=EZOay5mK4ezir93Hthf78IEQ&rqh=1&gir=yes&clen=788978&dur=204.660&lmt=1751194236212693&mt=1757961965&fvip=17&keepalive=yes&fexp=51331020%2C51552689%2C51565115%2C51565681%2C51580968&c=MWEB&sefc=1&txp=4532534&n=NV0OZWVsA3iW7w&sparams=expire%2Cei%2Cip%2Cid%2Citag%2Csource%2Crequiressl%2Cxpc%2Cbui%2Cspc%2Cvprv%2Csvpuc%2Cmime%2Cns%2Crqh%2Cgir%2Cclen%2Cdur%2Clmt&sig=AJfQdSswRQIgCGsbj9YJ8_7WeXcl7DKb9av4drLuvCH4Y6iDsSOv3yACIQCWO8YYnQQ1y04CK4CONBQ3gnBWkORp7Bw39Cz5DHYaDA%3D%3D&lsparams=met%2Cmh%2Cmm%2Cmn%2Cms%2Cmv%2Cmvi%2Cpl%2Crms%2Cinitcwndbps&lsig=APaTxxMwRQIhAN_GFt_7z03gfGcAJBeS0bgNht0gJMgbVD-_HEqGTwJzAiAaejtsmje9hVgTvcVUulsdggjw1WINJMvAujX854q04Q%3D%3D&pot=MnbXEQJFVEJcmNcv1FMM-aa1Z3ZjSiI2JX90LxmWfbUbvnK1t2dfnH0lzSA5Z2O1_CW2otEmJCcB-iYx_xwvuxnfZVXV3vX4HUpqgLfZ1G3U8rA8i1cl7w5QNDZtoSHb6MX5Fn66sa9iFni1KIe8x-Uf2kYM6mDM",
            "bitrate": 32150,
            "fps": None,
            "audioQuality": "AUDIO_QUALITY_ULTRALOW",
            "audioSampleRate": "22050",
            "mimeType": "audio/mp4; codecs=\"mp4a.40.5\"",
            "duration": 3,
            "quality": "m4a (32kb/s)",
            "extension": "m4a"
        },
        {
            "formatId": 600,
            "label": "opus (44kb/s)",
            "type": "audio",
            "ext": "opus",
            "width": None,
            "height": None,
            "url": "https://redirector.googlevideo.com/videoplayback?expire=1757984114&ei=EmHIaO7pNunbzPsPsoS0wAo&ip=178.133.164.253&id=o-AF_yKqtMLMS5E_Tj8fkPP-z4-wZXt33KwmVN8BE1bdYq&itag=600&source=youtube&requiressl=yes&xpc=EgVo2aDSNQ%3D%3D&met=1757962514%2C&mh=2x&mm=31%2C29&mn=sn-jvhnu5g03g-3c2z%2Csn-3c27sn7s&ms=au%2Crdu&mv=m&mvi=2&pl=25&rms=au%2Cau&initcwndbps=1003750&bui=AY1jyLPrRKSPs7w-py3YPFI6ZzzxRXkHh2vTttiFankTq28oke3V23LeYvK5csurVaQP7zDbR1FqdafE&spc=l3OVKTB7lM7NyX7wNagLLW5x4pVqRny05V4qDcr9_TnIY0YWSlx2SnO_o39IBB5G4b5dKGmFDtiuvkLrVIJ37_WT&vprv=1&svpuc=1&mime=audio%2Fwebm&ns=EZOay5mK4ezir93Hthf78IEQ&rqh=1&gir=yes&clen=992451&dur=204.581&lmt=1751194185239131&mt=1757961965&fvip=17&keepalive=yes&fexp=51331020%2C51552689%2C51565115%2C51565681%2C51580968&c=MWEB&sefc=1&txp=4532534&n=NV0OZWVsA3iW7w&sparams=expire%2Cei%2Cip%2Cid%2Citag%2Csource%2Crequiressl%2Cxpc%2Cbui%2Cspc%2Cvprv%2Csvpuc%2Cmime%2Cns%2Crqh%2Cgir%2Cclen%2Cdur%2Clmt&sig=AJfQdSswRQIhAPAHNMAUNw1LIplw9_7aN8BKSGuA40oGV3crSYHYbEnQAiAWYW865VdRNLmVOqmV6iO37srLZ7kIrJYu0urqAvfGNg%3D%3D&lsparams=met%2Cmh%2Cmm%2Cmn%2Cms%2Cmv%2Cmvi%2Cpl%2Crms%2Cinitcwndbps&lsig=APaTxxMwRQIhAN_GFt_7z03gfGcAJBeS0bgNht0gJMgbVD-_HEqGTwJzAiAaejtsmje9hVgTvcVUulsdggjw1WINJMvAujX854q04Q%3D%3D&pot=MnbXEQJFVEJcmNcv1FMM-aa1Z3ZjSiI2JX90LxmWfbUbvnK1t2dfnH0lzSA5Z2O1_CW2otEmJCcB-iYx_xwvuxnfZVXV3vX4HUpqgLfZ1G3U8rA8i1cl7w5QNDZtoSHb6MX5Fn66sa9iFni1KIe8x-Uf2kYM6mDM",
            "bitrate": 44051,
            "fps": None,
            "audioQuality": "AUDIO_QUALITY_ULTRALOW",
            "audioSampleRate": "48000",
            "mimeType": "audio/webm; codecs=\"opus\"",
            "duration": 3,
            "quality": "opus (44kb/s)",
            "extension": "opus"
        }
    ]

    chosen = pick_video_audio_urls(formats)
    # Pretty print selection
    import json
    print(json.dumps({
        "video_high_url": chosen["video_high_url"],
        "video_med_url": chosen["video_med_url"],
        "video_low_url": chosen["video_low_url"],
        "audio_high_url": chosen["audio_high_url"],
        "audio_med_url": chosen["audio_med_url"],
        "audio_low_url": chosen["audio_low_url"],
    }, indent=2))