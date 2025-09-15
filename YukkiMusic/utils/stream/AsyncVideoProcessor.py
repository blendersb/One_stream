import asyncio
import json
from typing import Optional, Dict, Any

import aiohttp
import websockets


class AsyncVideoProcessor:
    """
    Async class to send a merge/process request (via a WP AJAX endpoint)
    and subscribe to websocket status updates until completion.
    """

    def __init__(
        self,
        ajax_url: str,
        nonce: str,
        video_url: str,
        audio_url: str,
        quality: str = "720p",
        session: Optional[aiohttp.ClientSession] = None,
    ):
        self.ajax_url = ajax_url
        self.nonce = nonce
        self.video_url = video_url
        self.audio_url = audio_url
        self.quality = quality
        # caller can provide an aiohttp session or we create one in run()
        self._external_session = session
        self._session: Optional[aiohttp.ClientSession] = session

    def _build_request_data(self) -> Dict[str, Any]:
        render_id = f"BSJa1UytM8w_{self.quality}"
        request_data = {
            "id": render_id,
            "ttl": 3600000,
            "inputs": [
                {
                    "url": self.video_url,
                    "ext": "mp4",
                    "chunkDownload": {
                        "type": "header",
                        "size": 1024 * 1024 * 50,
                        "concurrency": 3,
                    },
                },
                {"url": self.audio_url, "ext": "m4a"},
            ],
            "output": {
                "ext": "mp4",
                "downloadName": f"Processed_{self.quality}.mp4",
                "chunkUpload": {"size": 1024 * 1024 * 200, "concurrency": 3},
            },
            "operation": {"type": "replace_audio_in_video"},
        }
        return {"id": render_id, "ttl": 3600000, "request_data": request_data}

    async def _start_job(self) -> Dict[str, Any]:
        """
        POST to the AJAX endpoint to start processing.
        Returns parsed JSON response.
        """
        data_payload = self._build_request_data()
        form_data = {
            "action": "process_video_merge",
            "nonce": self.nonce,
            # server expects request_data as JSON string in your original code
            "request_data": json.dumps(data_payload["request_data"]),
        }
        headers = {"X-WP-Nonce": self.nonce}
        session_created = False
        if self._session is None:
            self._session = aiohttp.ClientSession()
            session_created = True

        try:
            async with self._session.post(self.ajax_url, data=form_data, headers=headers, timeout=30) as resp:
                text = await resp.text()
                try:
                    return json.loads(text)
                except json.JSONDecodeError:
                    raise RuntimeError(f"Invalid JSON response from server: {text}")
        finally:
            if session_created:
                await self._session.close()
                self._session = None

    async def _get_ws_host(self) -> str:
        """
        Call the balancer URL to get a websocket host (the original used fastytcdn balancer).
        This call returns raw host text in the original script.
        """
        balancer_url = "https://balancer-v2.fastytcdn.com/get-server"
        session_created = False
        if self._session is None:
            self._session = aiohttp.ClientSession()
            session_created = True

        try:
            async with self._session.get(balancer_url, timeout=15) as resp:
                text = (await resp.text()).strip()
                if not text:
                    raise RuntimeError("Empty WebSocket host returned by balancer")
                return text
        finally:
            if session_created:
                await self._session.close()
                self._session = None

    async def _subscribe_ws(self, ws_host: str, render_id: str, max_attempts: int = 3) -> Dict[str, Any]:
        """
        Connect to wss://{ws_host}/pub/render/status_ws/{render_id} and stream messages.
        Returns final 'output' dict when processing completes or an error dict if error occurred.
        """
        ws_url = f"wss://{ws_host}/pub/render/status_ws/{render_id}"
        attempt = 0
        while attempt < max_attempts:
            attempt += 1
            try:
                async with websockets.connect(ws_url, ping_interval=20, ping_timeout=10) as ws:
                    async for raw_msg in ws:
                        try:
                            msg = json.loads(raw_msg)
                        except Exception:
                            # non-JSON message — skip or print
                            continue
                        # handle progress / output / error fields based on earlier script
                        percent = msg.get("formatted_progress_in_percent")
                        error = msg.get("error")
                        output = msg.get("output")
                        if percent is not None:
                            print(f"🔄 Progress: {percent}%")
                        if error:
                            print("❌ Server error:", error)
                            return {"error": error}
                        if output:
                            print("✅ Processing complete, got output.")
                            return output
                # if connection closes without result, retry
                await asyncio.sleep(1)
            except Exception as e:
                print(f"⚠️ WS attempt {attempt}/{max_attempts} failed: {e}")
                await asyncio.sleep(2 ** attempt)
        raise RuntimeError("WebSocket failed after max attempts")

    async def run(self) -> Dict[str, Any]:
        """
        Orchestrates the full async flow:
         1. Start job via AJAX
         2. Get ws host
         3. Subscribe to WS and wait for completion
        Returns the final output dict (may contain 'url' or 'error')
        """
        # Use own session for start_job and get_ws_host to reuse connection
        self._session = aiohttp.ClientSession()

        try:
            # 1) start the job
            print("🚀 Starting processing job via AJAX...")
            start_resp = await self._start_job()
            if not start_resp.get("success"):
                raise RuntimeError(f"Failed to start job: {start_resp.get('message') or start_resp}")

            # Find render id: original used request_data.id in payload -> our id
            render_id = f"BSJa1UytM8w_{self.quality}"

            # 2) get websocket host
            print("🔎 Querying balancer for websocket host...")
            ws_host = await self._get_ws_host()
            print("🔌 WS host:", ws_host)

            # 3) subscribe to WS
            print("🔗 Subscribing to WS for status...")
            final_output = await self._subscribe_ws(ws_host, render_id)
            return final_output or {}
        finally:
            if self._session:
                await self._session.close()
                self._session = None


# ----------------------------
# Example usage
# ----------------------------
'''async def main():
    # Replace these values with your real ones
    AJAX_URL = "https://ssyoutube.online/wp-admin/admin-ajax.php"
    NONCE = "919d8f38e1"
    VIDEO_URL = "https://redirector.googlevideo.com/your_video_url_here"
    AUDIO_URL = "https://redirector.googlevideo.com/your_audio_url_here"
    QUALITY = "720p"

    processor = AsyncVideoProcessor(
        ajax_url=AJAX_URL,
        nonce=NONCE,
        video_url=VIDEO_URL,
        audio_url=AUDIO_URL,
        quality=QUALITY,
    )

    try:
        result = await processor.run()
        if result.get("url"):
            print("📥 Download URL:", result["url"])
        elif result.get("error"):
            print("❌ Error:", result["error"])
        else:
            print("ℹ️ Completed but no URL in response:", result)
    except Exception as exc:
        print("❌ Processing failed:", exc)


if __name__ == "__main__":
    asyncio.run(main())'''
