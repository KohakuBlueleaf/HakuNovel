from json import loads
import asyncio

from utils import aio_get, aio_size


MAINURL = "https://webapi.ctfile.com/"
API: list[str] = [
    MAINURL + "getfile.php?path=f&f={file_id}&passcode={passcode}&ref=",
    MAINURL + "getfile.php?path=file&f={file_id}",
    MAINURL + "get_file_url.php?uid={uid}&fid={fid}&file_chk={chk}",
]
CHUNK = 4 * 1024**2

# ctfile limit 1 download at a time
# use a lock to ensure there is only 1 download task
CTFILE_LOCK = asyncio.Lock()


async def get_file_info(
    file_id: str,
    passcode: str = "",
) -> tuple[str]:
    """get file info for getting download link"""
    if passcode:
        raw, _ = await aio_get(
            API[0].format(file_id=file_id, passcode=passcode),
        )
    else:
        raw, _ = await aio_get(API[1].format(file_id=file_id))

    data = loads(bytes.decode(raw))
    return data["file"]["file_name"], data["file"]["file_chk"]


async def get_download_link(file_id: str, passcode: str = "") -> tuple[str]:
    """get download link from file info"""
    if file_id.count("-") > 1 and passcode == "":
        raise ValueError("You should provide passcode !")

    uid, fid = file_id.split("-")[:2]
    if file_id.count("-") == 1:
        name, chk = await get_file_info(file_id)
    else:
        name, chk = await get_file_info(file_id, passcode)

    raw, _ = await aio_get(API[2].format(uid=uid, fid=fid, chk=chk))
    data = loads(bytes.decode(raw))

    return name, data["downurl"]


async def download_file(file_id: str, passcode: str = "") -> tuple[str, bytes]:
    """
    Download file by file_id and passcode
    Still cannot bypass speed limit
    Use 4MB chunk to avoid payload not completed error
    """
    name, downlink = await get_download_link(file_id, passcode)
    fsize = await aio_size(downlink)

    print(downlink)
    print(f"starting download {name}.")
    print(f"size is {fsize}")

    iter = 0
    raw = b""
    while True:
        await CTFILE_LOCK.acquire()
        await asyncio.sleep(0.5)
        temp, _ = await aio_get(
            downlink, headers={"Range": f"{iter*CHUNK}-{(iter+1)*CHUNK-1}"}
        )
        await CTFILE_LOCK.release()

        if len(temp) != CHUNK:
            if len(raw) + len(temp) == fsize:
                raw += temp
                break
        else:
            raw += temp
            iter += 1

    print(f"{name} is downloaded.")
    print(len(raw))
    return name, raw
